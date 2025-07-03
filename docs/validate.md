# Validate Module

## Overview
The `validate` module provides functionality to validate data against JSON schemas, specifically designed for Gen3 data models. It includes classes for performing validation, generating statistics, and summarizing results.

## Classes

### Validate

The main validation class that handles the core validation logic.

#### Methods

- `__init__(data_map, resolved_schema)`
  - Initializes the validator with data and schema
  - **Parameters:**
    - `data_map`: Dictionary containing data to validate
    - `resolved_schema`: Resolved JSON schema to validate against

- `validate_object(obj, idx, validator)`
  - Validates a single object against a schema
  - **Parameters:**
    - `obj`: The object to validate
    - `idx`: Index of the object in the dataset
    - `validator`: JSON schema validator instance
  - **Returns:** List of validation results

- `validate_schema()`
  - Validates all data against the schema
  - **Returns:** Dictionary of validation results by entity

- `make_keymap()`
  - Creates a mapping of entities to their index keys
  - **Returns:** Dictionary mapping entities to their index keys

### ValidateStats

Provides statistical information about validation results.

#### Methods

- `n_rows_with_errors(entity)`
  - Returns the number of rows with validation errors for an entity
  - **Parameters:**
    - `entity`: Name of the entity
  - **Returns:** Number of rows with errors

- `count_results_by_index(entity, index_key, result_type="FAIL", print_results=False)`
  - Counts validation results for a specific index
  - **Parameters:**
    - `entity`: Name of the entity
    - `index_key`: Index key to count results for
    - `result_type`: Type of results to count ("PASS", "FAIL", "ALL")
    - `print_results`: Whether to print the results
  - **Returns:** Number of matching results

- `summary_stats()`
  - Generates summary statistics for all validation results
  - **Returns:** Pandas DataFrame with summary statistics

### ValidateSummary

Generates summaries of validation results.

#### Methods

- `flatten_validation_results(result_type="FAIL")`
  - Flattens validation results into a structured format
  - **Parameters:**
    - `result_type`: Type of results to include ("PASS", "FAIL", "ALL")
  - **Returns:** Dictionary of flattened validation results

- `flattened_results_to_pd()`
  - Converts flattened results to a pandas DataFrame
  - **Returns:** DataFrame with validation results

- `collapse_flatten_results_to_pd()`
  - Groups and summarizes validation results
  - **Returns:** DataFrame with summarized validation errors

## Example Usage

```python
from gen3_data_validator import Validate, ValidateStats, ValidateSummary

# Initialize validator
validator = Validate(data_map, resolved_schema)

# Run validation
results = validator.validate_schema()

# Get statistics
stats = ValidateStats(validator)
print(f"Total errors: {stats.total_validation_errors()}")

# Generate summary
summary = ValidateSummary(validator)
df = summary.flattened_results_to_pd()
print(df.head())
```
