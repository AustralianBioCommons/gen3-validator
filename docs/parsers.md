# Parsers Module

## Overview
The `parsers` module contains classes for parsing different types of data files, including JSON data and Excel metadata templates. These parsers prepare the data for validation against Gen3 schemas.

## Classes

### ParseData

Parses JSON data from files or directories and prepares it for validation.

#### Methods

- `__init__(data_folder_path: str = None, data_file_path: str = None, link_suffix: str = 's')`
  - Initializes the data parser
  - **Parameters:**
    - `data_folder_path`: Path to directory containing JSON files
    - `data_file_path`: Path to a single JSON file
    - `link_suffix`: Suffix to append to link identifiers

- `read_json(path: str) -> dict`
  - Reads and parses a JSON file
  - **Parameters:**
    - `path`: Path to the JSON file
  - **Returns:** Parsed JSON data

- `list_data_files() -> list`
  - Lists all JSON files in the specified directory or returns the single file path
  - **Returns:** List of file paths

- `load_json_data(json_paths: list, link_suffix: str = 's') -> dict`
  - Loads and processes JSON data from multiple files
  - **Parameters:**
    - `json_paths`: List of JSON file paths
    - `link_suffix`: Suffix for link identifiers
  - **Returns:** Dictionary of loaded data

- `get_node_names() -> list`
  - Extracts node names from file paths
  - **Returns:** List of node names

- `return_data(node: str) -> dict`
  - Retrieves data for a specific node
  - **Parameters:**
    - `node`: Name of the node
  - **Returns:** Data for the specified node

### ParseXlsxMetadata

Parses Excel files containing metadata templates and converts them to Gen3-compatible format.

#### Methods

- `__init__(xlsx_path: str, link_suffix: str = 's', skip_rows: int = 0)`
  - Initializes the Excel metadata parser
  - **Parameters:**
    - `xlsx_path`: Path to the Excel file
    - `link_suffix`: Suffix for link identifiers
    - `skip_rows`: Number of rows to skip at the beginning of each sheet

- `process_sheet(sheet_name: str, pk: str, fk: str = None, fk_name: str = None) -> list`
  - Processes a single sheet from the Excel file
  - **Parameters:**
    - `sheet_name`: Name of the sheet to process
    - `pk`: Primary key column name
    - `fk`: Foreign key column name (optional)
    - `fk_name`: Name to use for the foreign key relationship
  - **Returns:** List of processed records

## Example Usage

```python
from gen3_data_validator.parsers import ParseData, ParseXlsxMetadata

# Parse JSON data from a directory
data_parser = ParseData(data_folder_path="path/to/data/directory")
print(f"Loaded nodes: {data_parser.data_nodes}")

# Get data for a specific node
sample_data = data_parser.return_data("sample")
print(f"Sample data: {sample_data}")

# Parse Excel metadata
excel_parser = ParseXlsxMetadata("path/to/metadata.xlsx")
records = excel_parser.process_sheet("Samples", pk="sample_id", fk="subject_id", fk_name="subjects")
print(f"Processed {len(records)} records")
```
