import h2o
from h2o.automl import H2OAutoML

# Initialize the H2O cluster
h2o.init()

# Get user inputs (optional)
algo_input = input("Enter algorithm name (or press Enter to auto-select): ").strip()
metric_input = input("Enter metric name (or press Enter to auto-select): ").strip()

# If no input is provided, let AutoML select algorithms and metrics automatically
include_algos = [algo_input] if algo_input else None  # None lets AutoML decide
sort_metric = metric_input if metric_input else 'AUTO'  # 'AUTO' chooses the best metric

# Example AutoML setup with automatic or user-defined inputs
aml = H2OAutoML(
    include_algos=include_algos,
    sort_metric=sort_metric,
    max_runtime_secs=300
)

# Further code to train on your dataset goes here...