# Gen3 Data Validator

A Python package for validating data against Gen3 data models and schemas.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Modules](#modules)
   - [validate](#validate)
   - [resolve_schema](#resolveschema)
   - [parsers](#parsers)
   - [linkage](#linkage)
5. [Examples](#examples)
6. [License](#license)

## Overview

The Gen3 Data Validator is designed to validate data against Gen3 data models and schemas. It provides functionality to parse data files, resolve schemas, and validate data against those schemas.

## Installation

```bash
# Clone the repository
git clone https://github.com/AustralianBioCommons/gen3-data-validator.git
cd gen3-data-validator

# Install the package
pip install -e .
```

## Usage

```python
from gen3_data_validator import ResolveSchema, ParseData, Validate

# Initialize schema resolver
schema_resolver = ResolveSchema("path/to/schema.json")

# Parse data files
data_parser = ParseData(data_folder_path="path/to/data/folder")

# Validate data
validator = Validate(data_parser.data_dict, schema_resolver.resolved_schema)
validation_results = validator.validate_schema()
```

## Modules

### Validate

The `Validate` class provides functionality to validate data against resolved JSON schemas.

**Key Features:**
- Validates data objects against JSON schemas
- Provides detailed validation results
- Supports filtering and summarizing validation results

**Main Classes:**
- `Validate`: Main validation class
- `ValidateStats`: Provides statistical information about validation results
- `ValidateSummary`: Generates summaries of validation results

### ResolveSchema

The `ResolveSchema` class handles loading and processing of Gen3 JSON schemas.

**Key Features:**
- Loads and parses JSON schema files
- Resolves schema references
- Provides methods to navigate schema structure
- Generates node lookups and relationships

### Parsers

#### ParseData

Parses JSON data from files or folders and prepares it for validation.

**Key Features:**
- Loads data from JSON files
- Handles both single files and directories
- Provides data in a format suitable for validation

#### ParseXlsxMetadata

Parses Excel files containing metadata templates.

**Key Features:**
- Reads Excel files with metadata templates
- Converts data to Gen3-compatible format
- Handles primary and foreign key relationships

### Linkage

The `TestLinkage` class validates relationships between different data entities.

**Key Features:**
- Validates foreign key relationships
- Generates configuration maps for data relationships
- Provides detailed validation of data linkages

## Examples

### Basic Validation

```python
from gen3_data_validator import ResolveSchema, ParseData, Validate

# Initialize components
schema_resolver = ResolveSchema("schema.json")
data_parser = ParseData(data_folder_path="data/")

# Validate data
validator = Validate(data_parser.data_dict, schema_resolver.resolved_schema)
results = validator.validate_schema()

# Get summary statistics
stats = ValidateStats(validator)
print(stats.summary_stats())
```

### Advanced Usage

```python
# Get detailed validation results
summary = ValidateSummary(validator)
flattened_results = summary.flatten_validation_results()
df = summary.flattened_results_to_pd()

# Analyze validation errors
error_summary = summary.collapse_flatten_results_to_pd()
print(error_summary)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
