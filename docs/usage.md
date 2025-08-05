```python
import gen3validator
from gen3validator.logging_config import setup_logging
setup_logging()
```

## Reading in xlsx data and writing to json
- xlsx data comes from xlsx manifest file created from acdc_submission_template


```python
# ResolverClass = gen3validator.ResolveSchema(schema_path = "../schema/gen3_test_schema.json")
xlsxData = gen3validator.ParseXlsxMetadata(xlsx_path = "/Users/harrijh/projects/gen3-data-validator/data/lipid_metadata_example.xlsx", skip_rows=1)
xlsxData.parse_metadata_template()
xlsxData.write_dict_to_json(xlsx_data_dict=xlsxData.xlsx_data_dict, output_dir="/Users/harrijh/projects/gen3-data-validator/data/restricted/lipid_metadata_example")
```

## Creating Resolver Instance
- This class reads in the gen3schema.json then resolves the schema for use in the other classes



```python
Resolver = gen3validator.ResolveSchema(schema_path = "../tests/schema/gen3_test_schema.json")
Resolver.resolve_schema()
```


```python
# you can check the graph nodes in the resolved schema with 
Resolver.nodes
```

You can return the resolved schema with


```python
Resolver.schema_resolved
```

## Parsing data
- The parse data class takes in a data folder path containing json files for each data node



```python
# Testing linkage for test data that passes
Data = gen3validator.ParseData(data_folder_path = "../tests/data/pass")
```

To list the files read into the Data instance, you can use the following code:


```python
Data.file_path_list
```

All of the read data is stored in Data.data_dict as a dictionary, where the key is the entity and the value is a list of json objects


```python
Data.data_dict
```

The default link suffix is 's'
- This links suffix can be changed depending on what the key_name for the linked information is.


```python
Data.link_suffix
```

For example, in the json object below, we can see that the key "subjects" is what describes the link from sample to subject, since the value of 'subjects' is an array containing the key "submitter_id".
- Furthermore, the backref is called 'subjects' while the entity is called 'sample'
- Therefore, the link suffix is 's'


```python
Data.data_dict["sample"][0]
```

Finally, you can also check what the detected entities are below:


```python
Data.data_nodes
```

## Testing Linkage

The first thing you should do is create a linkage configuration map. The `.generate_config` method will do this for you, it will read in the data (stored in the `data_dict` attribute) and return a linkage configuration map.

The linkage configuration map is a dictionary that maps each entity to a dictionary of its primary and foreign keys, with the format:

```
{
    "entity_name": {
        "primary_key": "primary_key_field",
        "foreign_key": "foreign_key_field"
    }
}
```

Also, you can define the linkage configuration map yourself, but you need to make sure that the primary and foreign keys are defined for each entity.


```python
import gen3validator
DataPass = gen3validator.ParseData(data_folder_path = "../tests/data/pass")
LinkagePass = gen3validator.Linkage()
link_pass_config = LinkagePass.generate_config(DataPass.data_dict)
link_pass_config
```

Once you have the linkage configuration map, you can validate the links. The `.validate_links` method will do this for you, it will read in the data and the linkage configuration map then return a dictionary of the linkage validation results.

As a reminder, the data parsed to the `.validate_links` method as the `data_map` argument, has the format:

```python
{
    "entity_name_1": [
        {
            "field_name": "field_value"
        },
        {
            "field_name": "field_value"
        }
    ],
    "entity_name_2": [
        {
            "field_name": "field_value"
        },
        {
            "field_name": "field_value"
        }
    ]
}
```
Where `entity_name_1` and `entity_name_2` are the names of the entities in the data, and value is a list of json objects, each representing a record in the entity.


```python
import gen3validator
DataPass = gen3validator.ParseData(data_folder_path = "../tests/data/pass")
LinkagePass = gen3validator.Linkage()
link_pass_config = LinkagePass.generate_config(DataPass.data_dict)
LinkagePass.validate_links(data_map = DataPass.data_dict, config = link_pass_config, root_node = 'subject')
```

Testing linkage for test data that fails:
- Note that the `root_node` argument tells the validate_links method which entitie is a root node, therefore will not have any upstream links.


```python
DataFail = gen3validator.ParseData(data_folder_path = "../tests/data/fail")
LinkageFail = gen3validator.Linkage()
link_fail_config = LinkageFail.generate_config(DataFail.data_dict)
LinkageFail.validate_links(data_map = DataFail.data_dict, config = link_fail_config, root_node = 'subject')
```

You can check the json files read into the DataFail instance


```python
DataFail.file_path_list
```

This returns all of the foreign keys that are not linked to a primary key


```python
LinkageFail.link_validation_results
```

# Data Validation
- Validating json data objects to the gen3jsonschema


Creating the validation class
- You will need to preload the data under the `data_map` attribute and the resolved schema under the `resolved_schema` attribute in the `Validate` class.


```python
import gen3validator

resolver = gen3validator.ResolveSchema(schema_path = "../tests/schema/gen3_test_schema.json")
resolver.resolve_schema()
data = gen3validator.ParseData(data_folder_path = "../tests/data/fail")
validator = gen3validator.Validate(data_map=data.data_dict, resolved_schema=resolver.schema_resolved)

```

You can call the orchestrator method to run the validation pipeline with `.validate_schema`


```python
validator.validate_schema()
```

What is returned is a data structure in the following format:

```python
{
    'entity_name': [
        {
            'row_index_number': [
                {
                    'index': 0, # this is the index of the row in the entity
                    'invalid_key': 'this_is_the_column_name',
                    'validation_result': 'FAIL',
                    'schema_path': 'this_is_the_path_to_the_property_in_the_schema',
                    'validator': 'the_target_data_type',
                    'validator_value': 'the_correct_value',
                    'validation_error': 'this_is_the_validation_error_message'
                },
                {
                    'index': 0, # this is the index of the row in the entity
                    'invalid_key': 'same_row_validation_error_in_another_column',
                    'validation_result': 'FAIL',
                    'schema_path': 'this_is_the_path_to_the_property_in_the_schema',
                    'validator': 'the_target_data_type',
                    'validator_value': 'the_correct_value',
                    'validation_error': 'this_is_the_validation_error_message'
                }
            ]
        }
    ],
    'metabolomics_file': [
        {
            'index_0': [
                {'index': 0, # error in first row
                'validation_result': 'FAIL',
                'invalid_key': 'data_format', # error in column called data_format
                'schema_path': 'properties.data_format.enum',
                'validator': 'enum',
                'validator_value': ['wiff'],
                'validation_error': "True is not one of ['wiff']"
                },
                {'index': 0, # error in first row
                'validation_result': 'FAIL',
                'invalid_key': 'data_type', # error in column called data_type
                'schema_path': 'properties.data_type.enum',
                'validator': 'enum',
                'validator_value': ['MS', 'MS/MS'],
                'validation_error': "'1' is not one of ['MS', 'MS/MS']"
                }
            ]
        },
        {
            'index_1': [
                {
                    'index': 1, # error in second row
                    'validation_result': 'FAIL',
                    'invalid_key': 'data_format', # error in column called data_format
                    'schema_path': 'properties.data_format.enum',
                    'validator': 'enum',
                    'validator_value': ['wiff'],
                    'validation_error': "True is not one of ['wiff']"
                }
            ]
        }
    ]
}


     
```

Lets say we want to pull the validation results for a specific entity, at a specific row / index:
- `result_type` can either be `['ALL', 'FAIL', 'PASS']`
- This will return a list of json objects, each representing a validation result for a specific row in the entity


```python
validator.pull_index_of_entity(entity="sample", index_key=0, result_type="ALL")
```

You can print what entites were validated by using the `.list_entities` method.


```python
validator.list_entities()
```

if you want to see the row / index names of an entity you can use the `.list_index_by_entity` method:


```python
validator.list_index_by_entity("sample")
```

You can pull out a validation results for a specific entity with the `.pull_entity` method


```python
validator.pull_entity("sample")
```


```python
len(validator.pull_entity("sample"))
```

You can pull validation results for a specific entity and then a specific index / row with the `pull_index_of_entity` method.


```python
validator.pull_index_of_entity("sample", 0)
```

# Getting validation stats
- The `ValidateStats` class is used to get summary statistics and data frames of the validation results.

First we create a validator object and validate the data with the schema using the `validate_schema` method.


```python
import gen3validator
from gen3validator.logging_config import setup_logging
setup_logging(level="INFO")

resolver = gen3validator.ResolveSchema(schema_path = "../tests/schema/gen3_test_schema.json")
resolver.resolve_schema()
data = gen3validator.ParseData(data_folder_path = "../tests/data/fail")
validator = gen3validator.Validate(data_map=data.data_dict, resolved_schema=resolver.schema_resolved)
validator.validate_schema()
```

We then pass the validator instance to the `ValidateStats` class to get the summary statistics and data frames of the validation results which are stored in the `validation_result` attribute of the validator instance.


```python
validate_stats = gen3validator.ValidateStats(validator)
```

To get a high level summary we can call the `.summary_stats` method on the `ValidateStats` instance.


```python
validate_stats.summary_stats()
```

There are several other methods in the `ValidateStats` class that provide detailed metrics about your validation results:

- `n_rows_with_errors(entity)`: Returns the number of rows (entries) with at least one validation error for a given entity.
- `n_errors_per_entry(entity, index_key)`: Returns the number of validation errors for a specific row (by index) within an entity.
- `count_results_by_entity(entity, result_type="FAIL")`: Counts the number of validation results of a specific type (e.g., "FAIL", "PASS", or "ALL") for an entity.
- `count_results_by_index(entity, index_key, result_type="FAIL")`: Counts the number of validation results of a specific type for a specific row (by index) within an entity.
- `total_validation_errors()`: Returns the total number of validation errors across all entities.
These methods allow you to drill down into the validation results and generate custom summaries or reports as needed.


```python

# Usage examples for ValidateStats methods

entity = "sample"

rows_with_errors = validate_stats.n_rows_with_errors(entity)
print(f"Number of rows with errors for entity '{entity}': {rows_with_errors}")

index_key = 0
errors_per_entry = validate_stats.n_errors_per_entry(entity, index_key)
print(f"Number of errors for entity '{entity}' at index {index_key}: {errors_per_entry}")

fail_count = validate_stats.count_results_by_entity(entity, result_type="FAIL")
print(f"Total number of FAIL results for entity '{entity}': {fail_count}")

pass_count = validate_stats.count_results_by_entity(entity, result_type="PASS")
print(f"Total number of PASS results for entity '{entity}': {pass_count}")

all_count = validate_stats.count_results_by_entity(entity, result_type="ALL")
print(f"Total number of validation results for entity '{entity}': {all_count}")

fail_count_index = validate_stats.count_results_by_index(entity, index_key, result_type="FAIL")
print(f"Number of FAIL results for entity '{entity}' at index {index_key}: {fail_count_index}")

total_errors = validate_stats.total_validation_errors()
print(f"Total number of validation errors: {total_errors}")

summary_df = validate_stats.summary_stats()
print("Summary statistics DataFrame:")
print(summary_df)

```

# Creating validation summary data
- We can also pass the validator instance to the `ValidateSummary` class to get a flattened summary of the validation results.

Creating ValidateSummary instance


```python
import gen3validator
from gen3validator.logging_config import setup_logging
setup_logging(level="INFO")

resolver = gen3validator.ResolveSchema(schema_path = "../tests/schema/gen3_test_schema.json")
resolver.resolve_schema()
data = gen3validator.ParseData(data_folder_path = "../tests/data/fail")
validator = gen3validator.Validate(data_map=data.data_dict, resolved_schema=resolver.schema_resolved)
validator.validate_schema() # make sure validation has been run by calling .validate_schema()

Summary = gen3validator.ValidateSummary(validator) 

```

This returns the validation results in a flattened dictionary format.


```python
Summary.flatten_validation_results()
```

This returns the validation results in a flattened pandas dataframe.


```python
Summary.flattened_results_to_pd()
```

Finally you can also create an aggreated summary of the flattened validation results with:


```python
Summary.collapse_flatten_results_to_pd()
```
