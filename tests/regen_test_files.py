import json
import os
import gen3_data_validator

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))


def remove_file_if_exists(file_path):
    if os.path.exists(file_path):
        print(f"Removing existing file: {file_path}")
        os.remove(file_path)


def main():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")

    # Remove old resolved schema and data maps before running
    resolved_schema_path = os.path.join(
        script_dir, "schema", "gen3_test_schema_resolved.json"
    )
    fail_data_map_path = os.path.join(
        script_dir, "data", "data_maps", "fail_test_data_map.json"
    )
    pass_data_map_path = os.path.join(
        script_dir, "data", "data_maps", "pass_test_data_map.json"
    )

    # Define schema and data folder paths as separate variables
    schema_path = os.path.join(script_dir, "schema", "gen3_test_schema.json")
    fail_data_folder = os.path.join(script_dir, "data", "fail")
    pass_data_folder = os.path.join(script_dir, "data", "pass")

    print(f"Schema path: {schema_path}")
    print(f"Fail data folder: {fail_data_folder}")
    print(f"Pass data folder: {pass_data_folder}")
    print(f"Resolved schema output path: {resolved_schema_path}")
    print(f"Fail data map output path: {fail_data_map_path}")
    print(f"Pass data map output path: {pass_data_map_path}")

    remove_file_if_exists(resolved_schema_path)
    remove_file_if_exists(fail_data_map_path)
    remove_file_if_exists(pass_data_map_path)

    # Resolve schema and write resolved schema to file
    print("Resolving schema...")
    resolver = gen3_data_validator.ResolveSchema(schema_path=schema_path)
    resolver.resolve_schema()
    os.makedirs(os.path.dirname(resolved_schema_path), exist_ok=True)
    with open(resolved_schema_path, "w") as f:
        json.dump(resolver.schema_resolved, f)
    print(f"Resolved schema written to: {resolved_schema_path}")

    # Parse fail data and write data map to file
    print("Parsing fail data...")
    data_fail = gen3_data_validator.ParseData(data_folder_path=fail_data_folder)
    os.makedirs(os.path.dirname(fail_data_map_path), exist_ok=True)
    with open(fail_data_map_path, "w") as f:
        json.dump(data_fail.data_dict, f)
    print(f"Fail data map written to: {fail_data_map_path}")

    # Parse pass data and write data map to file
    print("Parsing pass data...")
    data_pass = gen3_data_validator.ParseData(data_folder_path=pass_data_folder)
    os.makedirs(os.path.dirname(pass_data_map_path), exist_ok=True)
    with open(pass_data_map_path, "w") as f:
        json.dump(data_pass.data_dict, f)
    print(f"Pass data map written to: {pass_data_map_path}")


if __name__ == "__main__":
    main()