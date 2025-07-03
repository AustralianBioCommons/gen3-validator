# Gen3 Data Validator Documentation

Welcome to the Gen3 Data Validator documentation. This tool is designed to help validate data against Gen3 data models and schemas.

## Getting Started

- [Overview](README.md) - Introduction to the Gen3 Data Validator
- [Installation](README.md#installation) - How to install the package
- [Quick Start](README.md#usage) - Basic usage examples

## Module Reference

- [Validate](validate.md) - Core validation functionality
- [ResolveSchema](resolve_schema.md) - Schema loading and processing
- [Parsers](parsers.md) - Data file parsers (JSON, Excel)
- [Linkage](linkage.md) - Relationship validation between entities

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
print(f"Validation complete. Found {len(results)} issues.")
```

### Advanced Usage

```python
from gen3_data_validator import ValidateStats, ValidateSummary

# Get statistics
stats = ValidateStats(validator)
print(f"Total validation errors: {stats.total_validation_errors()}")

# Generate detailed report
summary = ValidateSummary(validator)
df = summary.flattened_results_to_pd()
df.to_csv("validation_report.csv", index=False)
```

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
