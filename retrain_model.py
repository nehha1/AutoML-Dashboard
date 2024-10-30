import h2o
import pandas as pd

# Initialize H2O and load the trained model
h2o.init()
model = h2o.load_model("path_to_your_trained_model")

while True:  # Loop until user is satisfied
    # Step 1: User uploads a test CSV file
    test_file_path = input("Upload your CSV file path for testing: ")
    test_data = h2o.import_file(test_file_path)

    # Step 2: Make predictions
    predictions = model.predict(test_data)
    predictions_df = predictions.as_data_frame()

    # Step 3: Display predictions
    print("\nPrediction Results:")
    print(predictions_df)

    # Step 4: Ask user if they are satisfied with the predictions
    satisfied = input("Are you satisfied with the results? (yes/no): ").strip().lower()

    if satisfied == "yes":
        # Option to download the predictions
        download = input("Would you like to download the results? (yes/no): ").strip().lower()
        if download == "yes":
            predictions_df.to_csv("predictions.csv", index=False)
            print("Predictions saved as 'predictions.csv'")
        break  # Exit loop if user is satisfied

    # Step 5: If not satisfied, ask if they want to change algo/metric or retry
    print("Do you want to change the algorithm, metric, or both?")
    change_algo = input("Change algorithm? (yes/no): ").strip().lower()
    change_metric = input("Change metric? (yes/no): ").strip().lower()

    if change_algo == "yes" or change_metric == "yes":
        # Ask for new algorithm/metric selection
        algo_input = input("Enter new algorithm: ").strip()
        metric_input = input("Enter new metric: ").strip()

        # Update AutoML with new configuration
        algo_input = [algo_input] if algo_input else None
        metric_input = metric_input if metric_input else 'AUTO'

        # Re-train with new settings
        model = H2OAutoML(include_algos=algo_input, sort_metric=metric_input, max_runtime_secs=300)
        print("Model re-trained with new settings.")
    else:
        print("Repeating with the same algorithm and metric.")

print("Process completed.")