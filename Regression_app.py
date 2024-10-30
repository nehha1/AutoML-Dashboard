# regression_app.py
from flask import Flask, request, jsonify
import h2o
from h2o.estimators import H2ORandomForestEstimator, H2OGradientBoostingEstimator, H2OGeneralizedLinearEstimator
from h2o.automl import H2OAutoML
import pandas as pd
import gridfs
from pymongo import MongoClient

app = Flask(__name__)

# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['model_db']
fs = gridfs.GridFS(db)


def get_model_choice(choice):
    models = {
        '1': H2ORandomForestEstimator(ntrees=100, max_depth=20, seed=1),
        '2': H2OGradientBoostingEstimator(ntrees=100, max_depth=20, seed=1),
        '3': H2OGeneralizedLinearEstimator(family='gaussian'),
        '4': H2OAutoML(max_models=10, max_runtime_secs=3600, seed=1)
    }
    return models.get(choice, H2OAutoML(max_models=10, max_runtime_secs=3600, seed=1))


def load_data(file_path, file_type):
    if file_type.lower() == 'csv':
        df = pd.read_csv(file_path)
    elif file_type.lower() == 'tabular':
        df = pd.read_table(file_path)  # Assuming the tabular file is tab-separated
        df.to_csv(file_path.replace('.txt', '.csv').replace('.tsv', '.csv'), index=False)
    elif file_type.lower() == 'excel':
        df = pd.read_excel(file_path)
        df.to_csv(file_path.replace('.xlsx', '.csv').replace('.xls', '.csv'), index=False)
    else:
        raise ValueError("Unsupported file type. Please use 'csv', 'tabular', or 'excel'.")
    return df


@app.route('/train', methods=['POST'])
def train():
    # Get input data
    file_path = request.json['file_path']
    file_type = request.json['file_type']
    target = request.json['target']
    model_choice = request.json.get('model_choice', '4')

    # Load and preprocess data
    df = load_data(file_path, file_type)
    h2o.init()
    for col in df.columns:
        try:
            pd.to_datetime(df[col], format='%d-%m-%Y', errors='raise')
            df.drop(columns=[col], inplace=True)
        except:
            continue
    df = df.dropna(subset=[target])
    df.fillna(df.mean(numeric_only=True), inplace=True)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category').cat.codes
    data = h2o.H2OFrame(df)
    train_data, test_data = data.split_frame(ratios=[0.8], seed=1)
    features = [col for col in train_data.columns if col != target]

    # Train model
    model = get_model_choice(model_choice)
    model.train(x=features, y=target, training_frame=train_data)

    # Get predictions and calculate accuracy metrics
    predictions = model.predict(test_data)
    predictions_df = predictions.as_data_frame()
    test_data_df = test_data.as_data_frame()
    mse = ((predictions_df['predict'] - test_data_df[target]) ** 2).mean()
    rmse = mse ** 0.5
    mae = (predictions_df['predict'] - test_data_df[target]).abs().mean()

    # Save model to MongoDB
    local_model_path = h2o.save_model(model=model, path="./", force=True)
    with open(local_model_path, 'rb') as model_file:
        fs.put(model_file, filename=local_model_path)

    h2o.shutdown(prompt=False)
    return jsonify({"model_path": local_model_path, "mse": mse, "rmse": rmse, "mae": mae})


@app.route('/predict', methods=['POST'])
def predict():
    file_path = request.json['file_path']
    file_type = request.json['file_type']
    model_path = request.json['model_path']

    # Retrieve model from MongoDB
    model_file = fs.find_one({'filename': model_path})
    with open(model_path, 'wb') as model_out:
        model_out.write(model_file.read())

    # Load model and data
    h2o.init()
    model = h2o.load_model(model_path)
    df = load_data(file_path, file_type)
    df.fillna(df.mean(numeric_only=True), inplace=True)
    for col in df.select_dtypes(include(['object']).columns:
        df[col] = df[col].astype('category').cat.codes
    data = h2o.H2OFrame(df)
    predictions = model.predict(data).as_data_frame()
    h2o.shutdown(prompt=False)

    return jsonify