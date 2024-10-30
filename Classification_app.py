# app.py
from flask import Flask, request, jsonify
import h2o
from h2o.estimators import H2ORandomForestEstimator, H2OGradientBoostingEstimator, H2OGeneralizedLinearEstimator
from h2o.automl import H2OAutoML
import pandas as pd

app = Flask(__name__)

def get_model_choice(choice):
    models = {
        '1': H2ORandomForestEstimator(ntrees=100, max_depth=20, seed=1),
        '2': H2OGradientBoostingEstimator(ntrees=100, max_depth=20, seed=1),
        '3': H2OGeneralizedLinearEstimator(family='binomial'),
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
    if df[target].nunique() <= 10:
        df[target] = df[target].astype('category')
    data = h2o.H2OFrame(df)
    train_data, test_data = data.split_frame(ratios=[0.8], seed=1)
    features = [col for col in train_data.columns if col != target]

    # Train model
    model = get_model_choice(model_choice)
    model.train(x=features, y=target, training_frame=train_data)

    # Get predictions and calculate accuracy
    predictions = model.predict(test_data)
    predictions_df = predictions.as_data_frame()
    test_data_df = test_data.as_data_frame()
    valid_targets = train_data[target].as_data_frame()[target].unique()
    predictions_df['predict'] = predictions_df['predict'].apply(lambda x: x if x in valid_targets else valid_targets[0])
    correct_predictions = (predictions_df['predict'] == test_data_df[target]).sum()
    accuracy = correct_predictions / len(test_data_df)

    # Save model
    model_path = h2o.save_model(model=model, path="./", force=True)
    h2o.shutdown(prompt=False)

    return jsonify({"model_path": model_path, "accuracy": accuracy * 100})

@app.route('/predict', methods=['POST'])
def predict():
    file_path = request.json['file_path']
    file_type = request.json['file_type']
    model_path = request.json['model_path']

    # Load model and data
    h2o.init()
    model = h2o.load_model(model_path)
    df = load_data(file_path, file_type)
    df.fillna(df.mean(numeric_only=True), inplace=True)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category').cat.codes
    data = h2o.H2OFrame(df)
    predictions = model.predict(data).as_data_frame()
    h2o.shutdown(prompt=False)

    return jsonify(predictions.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True)
