# Linkage Module

## Overview
The `linkage` module provides functionality to validate relationships between different data entities in a Gen3 data model. It ensures referential integrity and validates the structure of linked data.

## Classes

### Linkage

Validates relationships between different data entities based on a schema.

#### Methods

- `__init__(schema_resolver, data_parser, root_node: List[str] = None)`
  - Initializes the linkage tester
  - **Parameters:**
    - `schema_resolver`: Instance of ResolveSchema
    - `data_parser`: Instance of ParseData
    - `root_node`: List of root node names (default: ['subject'])

- `generate_models(config: Dict[str, Any]) -> Dict[str, type]`
  - Dynamically generates Pydantic models based on configuration
  - **Parameters:**
    - `config`: Dictionary defining entities and their fields
  - **Returns:** Dictionary of Pydantic model classes

- `validate_links(data_map: Dict[str, Any], config: Dict[str, Any], root_node: List[str]) -> Dict[str, Any]`
  - Validates all links in the data map according to the configuration
  - **Parameters:**
    - `data_map`: Dictionary containing the data to validate
    - `config`: Configuration dictionary
    - `root_node`: List of root node names
  - **Returns:** Dictionary of validation results

- `validate_config_map(config_map: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]`
  - Validates the configuration map for foreign key relationships
  - **Parameters:**
    - `config_map`: Configuration map to validate
  - **Returns:** Dictionary of validation results

## Example Usage

```python
from gen3_data_validator import ResolveSchema, ParseData
from gen3_data_validator.linkage import Linkage

# Initialize required components
schema_resolver = ResolveSchema("path/to/schema.json")
data_parser = ParseData(data_folder_path="path/to/data")

# Create and run linkage tests
linkage_tester = Linkage(schema_resolver, data_parser)
results = linkage_tester.validate_links(
    data_map=data_parser.data_dict,
    config=linkage_tester.linkage_config,
    root_node=['subject']
)

# Check for validation errors
for entity, errors in results.items():
    if errors:
        print(f"Found {len(errors)} errors in {entity}:")
        for error in errors:
            print(f"  - {error}")
```

## Configuration Format

The linkage configuration should be a dictionary where each key is an entity name and the value is another dictionary with the following structure:

```python
{
    "entity_name": {
        "primary_key": "id",  # Name of the primary key column
        "foreign_key": "subject_id",  # Name of the foreign key column (optional)
        "foreign_entity": "subject"  # Name of the referenced entity (optional)
    },
    # ... more entities
}
```

## Validation Rules

1. All foreign keys must reference an existing primary key in the referenced entity
2. Root nodes (specified in `root_node`) are allowed to have null foreign keys
3. Non-root nodes must have valid foreign key references
4. Circular references are detected and reported
