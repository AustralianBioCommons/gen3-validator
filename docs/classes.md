# Class Documentation

This document provides systematic, clean, and consistent documentation for all major classes in the `gen3-data-validator` codebase, as found in `src/gen3validator`. Each class section includes the class description, constructor, attributes, methods, input/output types, and usage notes, as inferred from the code and docstrings.

---

## `Validate`

**Location:** `src/gen3validator/validate.py`

### Description
Responsible for validating data objects against a resolved JSON schema using the Draft4Validator from the `jsonschema` library. Provides methods to validate individual objects, manage validation results, and create key mappings for further processing.

### Constructor
```python
Validate(data_map: dict, resolved_schema: dict)
```
- **data_map** (`dict`): Dictionary of data objects. Keys are entity names; values are lists of JSON objects (e.g., `{ 'sample': [{id: 1, ...}, ...] }`).
- **resolved_schema** (`dict`): The resolved Gen3 JSON schema.

### Attributes
- `data_map` (`dict`): See above.
- `resolved_schema` (`dict`): See above.
- `validation_result` (`dict` or `None`): Stores validation results.
- `key_map` (`dict` or `None`): Maps entities to their index keys.

### Methods
- `validate_object(obj: dict, idx: int, validator: Draft4Validator) -> list`
    - Validates a single JSON object against the schema. Returns a list of validation result dicts.
- `validate_schema() -> dict`
    - Validates the entire data map against the schema. Returns a dict of validation results for each entity.
- `list_entities() -> list`
    - Lists all entities present in the validation results.
- `list_index_by_entity(entity: str) -> list`
    - Lists all index keys for a specified entity.
- `make_keymap() -> dict`
    - Generates a mapping of keys from the data map for reference and lookup.
- `pull_entity(entity: str, result_type: str = "FAIL") -> list`
    - Retrieves validation results for a specified entity, filtered by result type.
- `pull_index_of_entity(entity: str, index_key: int, result_type: str = "FAIL", return_failed: bool = True) -> list`
    - Retrieves validation results for a specified entity and index key.
- `flatten_validation_results(result_type: str = "FAIL") -> list`
    - Flattens validation results for easier analysis.
- `flattened_results_to_pd() -> pandas.DataFrame`
    - Converts flattened validation results to a DataFrame.
- `collapse_flatten_results_to_pd() -> pandas.DataFrame`
    - Collapses flattened results into a summarized DataFrame.

---

## `ValidateStats`

**Location:** `src/gen3validator/validate.py`

### Description
Provides summary statistics and analysis over validation results produced by the `Validate` class.

### Constructor
```python
ValidateStats(validate_instance: Validate)
```
- **validate_instance** (`Validate`): An instance of the `Validate` class.

### Attributes
- `data_map` (`dict`): Data map from the Validate instance.
- `resolved_schema` (`dict`): Schema from the Validate instance.
- `validation_result` (`dict`): Validation results from the Validate instance.

### Methods
- `n_rows_with_errors(entity: str) -> int`
    - Returns the number of rows with validation errors for a given entity.
- `count_results_by_index(entity: str, index_key: int, result_type: str = "FAIL", print_results: bool = False) -> int`
    - Counts the number of validation results for a specific entity and index.
- `count_results_by_entity(entity: str, result_type: str = "FAIL", print_results: bool = False) -> int`
    - Counts the number of failed validation results for the specified entity.
- `n_errors_per_entry(entity: str, index_key: int) -> int`
    - Returns the number of validation errors for a given entity and index.
- `total_validation_errors() -> int`
    - Calculates the total number of validation errors across all entities.
- `summary_stats() -> pandas.DataFrame`
    - Returns a DataFrame summarizing validation errors per entity.

---

## `Linkage`

**Location:** `src/gen3validator/linkage.py`

### Description
Handles linkage validation between entities, including primary and foreign key extraction, config generation, and link validation.

### Constructor
```python
Linkage(root_node: List[str] = None)
```
- **root_node** (`list[str]`, optional): List of root node names allowed to have unmatched foreign keys. Defaults to `["subject"]`.

### Attributes
- `root_node` (`list[str]`): See above.
- `link_validation_results` (`dict` or `None`): Stores results of link validation.

### Methods
- `_find_fk(data: dict) -> str`
    - Identifies the foreign key in a data record.
- `generate_config(data_map: dict, link_suffix: str = 's') -> dict`
    - Generates a config dictionary for entities based on the data map.
- `test_config_links(config_map: dict, root_node: List[str] = None) -> dict`
    - Validates the configuration map by checking foreign key links between entities.
- `get_foreign_keys(data_map: dict, config: dict) -> dict`
    - Extracts all foreign key values for each entity.
- `get_primary_keys(data_map: dict, config: dict) -> dict`
    - Extracts all primary key values for each entity.
- `validate_links(data_map: dict, config: dict, root_node: List[str] = None) -> dict`
    - Validates that all foreign keys exist among the primary keys of any entity.

---

## `ParseData`

**Location:** `src/gen3validator/parsers/parse_data.py`

### Description
Parses JSON data from a specified folder or a single file, and constructs a dictionary representation of the data.

### Constructor
```python
ParseData(data_folder_path: str = None, data_file_path: str = None, link_suffix: str = 's')
```
- **data_folder_path** (`str`, optional): Path to a folder containing JSON files.
- **data_file_path** (`str`, optional): Path to a single JSON file.
- **link_suffix** (`str`, optional): Suffix to append to link identifiers. Default is `'s'`.

### Attributes
- `folder_path` (`str` or `None`): Path to the data folder.
- `file_path` (`str` or `None`): Path to the data file.
- `link_suffix` (`str`): Suffix for link identifiers.
- `file_path_list` (`list`): List of data file paths.
- `data_dict` (`dict`): Dictionary representation of the loaded data.
- `data_nodes` (`list`): List of node names.

### Methods
- `read_json(path: str) -> dict`
    - Reads a JSON file and returns its contents as a dictionary.
- `list_data_files() -> list`
    - Lists all JSON data files in the folder or returns the single file path.
- `load_json_data(json_paths: list, link_suffix: str = 's') -> dict`
    - Loads JSON data from file paths and constructs the internal data dictionary.
- `get_node_names() -> list`
    - Retrieves the names of nodes from the JSON files.
- `return_data(node: str) -> dict`
    - Retrieves data for a specified node.

---

## `ParseXlsxMetadata`

**Location:** `src/gen3validator/parsers/parse_xlsx.py`

### Description
Converts a specified sheet from the metadata dictionary (generated by the Gen3 metadata templates) to a JSON file. Also formats and renames the primary and foreign keys into a Gen3-compatible format.

### Constructor
```python
ParseXlsxMetadata(xlsx_path: str, link_suffix: str = 's', skip_rows: int = 0)
```
- **xlsx_path** (`str`): Path to the Excel file containing metadata templates.
- **link_suffix** (`str`, optional): Suffix to append to link identifiers. Default is `'s'`.
- **skip_rows** (`int`, optional): Number of rows to skip at the top of each sheet. Default is `0`.

### Attributes
- `xlsx_path` (`str`): See above.
- `skip_rows` (`int`): See above.
- `xlsx_data_dict` (`dict` or `None`): Loaded Excel data as a dictionary of DataFrames.
- `link_suffix` (`str`): See above.

### Methods
- `parse_metadata_template() -> dict`
    - Parses the Excel file and loads each sheet as a DataFrame.
- `get_sheet_names() -> list`
    - Retrieves the names of all sheets in the Excel file.
- `get_pk_fk_pairs(xlsx_data_dict: dict, sheet_name: str) -> tuple`
    - Extracts the primary and foreign key column names from a specified sheet.
- `format_pd_to_json(xlsx_data_dict: dict, sheet_name: str) -> list`
    - Formats a DataFrame into a specific JSON format.
- `pd_to_json(xlsx_data_dict: dict, sheet_name: str, json_path: str) -> None`
    - Writes a list of JSON objects to a JSON file.
- `write_dict_to_json(xlsx_data_dict: dict, output_dir: str) -> None`
    - Writes all DataFrames in the dictionary to JSON files in the specified directory.

---

## `ResolveSchema`

**Location:** `src/gen3validator/resolve_schema.py`

### Description
Handles loading, resolving, and manipulating Gen3 JSON schemas, including reference resolution and schema version extraction.

### Constructor
```python
ResolveSchema(schema_path: str)
```
- **schema_path** (`str`): Path to the JSON schema file.

### Attributes
- `schema_path` (`str`): See above.
- `schema` (`dict` or `None`): Loaded schema.
- `nodes` (`list` or `None`): Node names.
- `node_pairs` (`list` or `None`): Node relationships.
- `node_order` (`list` or `None`): Topologically sorted node order.
- `schema_list` (`list` or `None`): List of node schemas.
- `schema_def` (`dict` or `None`): Definitions schema.
- `schema_term` (`dict` or `None`): Terms schema.
- `schema_def_resolved` (`dict` or `None`): Resolved definitions schema.
- `schema_list_resolved` (`list` or `None`): List of resolved node schemas.
- `schema_resolved` (`dict` or `None`): Resolved schema as a dictionary.
- `schema_version` (`str` or `None`): Extracted schema version.

### Methods
- `read_json(path: str) -> dict`
    - Reads a JSON file and returns its contents as a dictionary.
- `get_nodes() -> list`
    - Retrieves all node names from the schema.
- `get_node_link(node_name: str) -> tuple`
    - Retrieves links and ID for a given node.
- `get_node_category(node_name: str) -> tuple`
    - Retrieves the category and ID for a given node.
- `get_node_properties(node_name: str) -> tuple`
    - Retrieves properties for a given node.
- `generate_node_lookup() -> dict`
    - Generates a lookup dictionary for nodes.
- `find_upstream_downstream(node_name: str) -> list`
    - Returns upstream and downstream nodes for a given node.
- `get_all_node_pairs(excluded_nodes: list = [...]) -> list`
    - Retrieves all node pairs, excluding specified nodes.
- `get_node_order(edges: list) -> list`
    - Determines the order of nodes based on dependencies.
- `split_json() -> list`
    - Splits the schema into a list of individual node schemas.
- `return_schema(target_id: str) -> dict`
    - Retrieves a dictionary from a list where the 'id' key matches `target_id`.
- `resolve_references(schema: dict, reference: dict) -> dict`
    - Recursively resolves references in a schema.
- `resolve_all_references() -> list`
    - Resolves references in all schema dictionaries.
- `schema_list_to_json(schema_list: list) -> dict`
    - Converts a list of schemas to a dictionary keyed by schema id.
- `return_resolved_schema(target_id: str) -> dict`
    - Retrieves a resolved schema by id.
- `get_schema_version(schema: dict) -> str`
    - Extracts the version from a schema dictionary.
- `resolve_schema() -> None`
    - Loads and resolves all schema-related attributes for the instance.

---

> **Note:** All method and attribute types are inferred from type hints and docstrings. For more detail, refer to the codebase or the respective source files.
