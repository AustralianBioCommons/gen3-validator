# ResolveSchema Module

## Overview
The `resolve_schema` module provides functionality to load, process, and resolve Gen3 JSON schemas. It handles schema resolution, node relationship mapping, and schema validation.

## Classes

### ResolveSchema

Main class for handling schema resolution and processing.

#### Methods

- `__init__(schema_path: str)`
  - Initializes the schema resolver with the path to the schema file
  - **Parameters:**
    - `schema_path`: Path to the JSON schema file

- `read_json(path: str) -> dict`
  - Reads and parses a JSON file
  - **Parameters:**
    - `path`: Path to the JSON file
  - **Returns:** Parsed JSON data as a dictionary

- `get_nodes() -> list`
  - Retrieves all node names from the schema
  - **Returns:** List of node names

- `get_node_link(node_name: str) -> tuple`
  - Retrieves links and ID for a given node
  - **Parameters:**
    - `node_name`: Name of the node
  - **Returns:** Tuple containing node ID and its links

- `get_node_category(node_name: str) -> tuple`
  - Retrieves category and ID for a given node
  - **Parameters:**
    - `node_name`: Name of the node
  - **Returns:** Tuple containing node ID and category

- `get_node_properties(node_name: str) -> tuple`
  - Retrieves properties for a given node
  - **Parameters:**
    - `node_name`: Name of the node
  - **Returns:** Tuple containing node ID and its properties

- `generate_node_lookup() -> dict`
  - Generates a lookup dictionary for all nodes
  - **Returns:** Dictionary mapping nodes to their categories and properties

- `find_upstream_downstream(node_name: str) -> list`
  - Finds upstream and downstream nodes for a given node
  - **Parameters:**
    - `node_name`: Name of the node
  - **Returns:** List of tuples representing upstream and downstream nodes

- `schema_list_to_json(schema_list: list) -> dict`
  - Converts a list of schemas to a dictionary
  - **Parameters:**
    - `schema_list`: List of schema dictionaries
  - **Returns:** Dictionary of schemas keyed by schema ID

## Example Usage

```python
from gen3_data_validator import ResolveSchema

# Initialize schema resolver
schema_resolver = ResolveSchema("path/to/schema.json")

# Get all nodes
nodes = schema_resolver.get_nodes()
print(f"Available nodes: {nodes}")

# Get node properties
for node in nodes:
    node_id, properties = schema_resolver.get_node_properties(node)
    print(f"Node: {node}, ID: {node_id}, Properties: {properties}")

# Generate node lookup
node_lookup = schema_resolver.generate_node_lookup()
print(node_lookup)
```
