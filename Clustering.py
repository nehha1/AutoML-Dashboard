import h2o
from h2o.estimators import H2OKMeansEstimator
import pandas as pd

def get_model_choice():
    print("Choose a clustering algorithm:")
    print("1. K-Means")
    print("2. AutoML (default)")
    choice = input("Enter the number of your choice: ")
    return choice

def train_model(choice, features, train_data):
    if choice == '1':
        model = H2OKMeansEstimator(k=3, seed=1)  # K set to 3, you can adjust as needed
    else:
        model = H2OAutoML(max_models=10, max_runtime_secs=3600, seed=1)
    model.train(x=features, training_frame=train_data)
    return model

def load_data(file_path, file_type):
    if file_type.lower() == 'csv':
        df = pd.read_csv(file_path)
    elif file_type.lower() == 'tabular':
        df = pd.read_table(file_path)  # Assuming the tabular file is tab-separated
        df.to_csv(file_path.replace('.txt', '.csv').replace('.tsv', '.csv'), index=False)
        file_path = file_path.replace('.txt', '.csv').replace('.tsv', '.csv')
    elif file_type.lower() == 'excel':
        df = pd.read_excel(file_path)
        df.to_csv(file_path.replace('.xlsx', '.csv').replace('.xls', '.csv'), index=False)
        file_path = file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
    else:
        raise ValueError("Unsupported file type. Please use 'csv', 'tabular', or 'excel'.")
    return df, file_path

def automate_process():
    # Prompt user for file path, file type
    file_path = input("Enter the path to your file: ").strip('\"')
    file_type = input("Enter the file type (csv, tabular, or excel): ")

    # Load and convert data if necessary
    df, file_path = load_data(file_path, file_type)

    # Start H2O cluster
    h2o.init()

    # Drop columns with date data types
    for col in df.columns:
        try:
            pd.to_datetime(df[col], format='%d-%m-%Y', errors='raise')
            df.drop(columns=[col], inplace=True)
        except:
            continue

    # Handle missing values (e.g., fill with mean/mode/median or drop)
    df.fillna(df.mean(numeric_only=True), inplace=True)

    # Convert categorical columns to numeric (if any)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category').cat.codes

    # Convert pandas dataframe to H2O dataframe
    data = h2o.H2OFrame(df)

    # Split the data into train and test sets using H2O
    train_data, test_data = data.split_frame(ratios=[0.8], seed=1)

    # Define features
    features = [col for col in train_data.columns]

    # Get user choice for clustering algorithm
    choice = get_model_choice()

    # Train the selected model or AutoML
    model = train_model(choice, features, train_data)

    # Get predictions on the test set
    predictions = model.predict(test_data)

    # Convert H2O predictions to pandas dataframe
    predictions_df = predictions.as_data_frame()
    test_data_df = test_data.as_data_frame()

    # Print predictions for the initial test set
    print("Initial test set cluster assignments:")
    print(predictions_df.head())

    # Option to upload a separate test file
    additional_test_file = input("Enter the path to your additional test file (or press Enter to skip): ").strip('\"')
    if additional_test_file:
        additional_test_type = input("Enter the file type (csv, tabular, or excel): ")
        additional_test_df, _ = load_data(additional_test_file, additional_test_type)

        # Ensure additional test data matches training features
        for col in additional_test_df.select_dtypes(include=['object']).columns:
            additional_test_df[col] = additional_test_df[col].astype('category').cat.codes

        additional_test_df = h2o.H2OFrame(additional_test_df)

        # Get predictions for the additional test file
        additional_predictions = model.predict(additional_test_df)
        additional_predictions_df = additional_predictions.as_data_frame()

        # Print predictions for the additional test file
        print("Additional test file cluster assignments:")
        print(additional_predictions_df.head())

    else:
        print("No additional test file uploaded.")

    # Shutdown H2O cluster
    h2o.shutdown(prompt=False)

# Run the function
automate_process()
