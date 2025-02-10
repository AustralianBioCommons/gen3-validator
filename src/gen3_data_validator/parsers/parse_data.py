import json
import os


class ParseData:
    """Parses JSON data from a specified folder or a single file, and constructs a dictionary representation of the data."""

    def __init__(
        self, data_folder_path: str = None, data_file_path: str = None, link_suffix: str = 's'
    ):
        self.folder_path = data_folder_path
        self.file_path = data_file_path
        self.link_suffix = link_suffix
        self.file_path_list = self.list_data_files()
        self.data_dict = self.load_json_data(
            self.file_path_list, link_suffix=self.link_suffix
        )
        self.data_nodes = self.get_node_names()

    def read_json(self, path: str) -> dict:
        try:
            with open(path) as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print(f"Error: The file {path} was not found.")
        except json.JSONDecodeError:
            print(f"Error: The file {path} could not be decoded as JSON.")
        except Exception as e:
            print(f"An unexpected error occurred while reading {path}: {e}")

    def list_data_files(self) -> list:
        """
        Lists all JSON data files in the specified folder or returns the single file path.

        This method checks if a folder path is provided. If so, it lists all files in the folder
        that have a '.json' extension and returns their absolute paths. If no folder path is provided,
        it returns the single file path specified during initialization.

        Returns:
        - list: A list of absolute file paths to JSON files.
        """
        if self.folder_path:
            json_paths = [
                os.path.abspath(os.path.join(self.folder_path, f))
                for f in os.listdir(self.folder_path)
                if f.endswith(".json")
            ]
        else:
            json_paths = [self.file_path]
        return json_paths

    def load_json_data(self, json_paths: list, link_suffix: str = 's') -> dict:
        json_files = {}
        for file in json_paths:
            json_data = self.read_json(file)
            file_basename = os.path.basename(file)
            file_basename = file_basename.replace('.json', '')
            for entry in json_data:
                entry[f"{file_basename}{link_suffix}"] = entry['submitter_id']
            json_files[file_basename] = json_data
        return json_files

    def get_node_names(self) -> list:
        """
        Retrieves the names of nodes from the JSON files.

        This method iterates over the list of file paths and extracts the node names
        by removing the '.json' extension from each file name.

        Returns:
        - list: A list of node names extracted from the JSON file paths.
        """
        node_names = []
        for node in self.file_path_list:
            if node.endswith('.json'):
                last_item = os.path.basename(node)
                node_names.append(last_item[:-5])
            else:
                node_names.append(node)
        return node_names

    def return_data(self, node: str) -> dict:
        """
        Retrieves data for a specified node.

        This method accesses the data dictionary and returns the data
        associated with the given node name.

        Parameters:
        - node (str): The name of the node for which data is to be retrieved.

        Returns:
        - dict: A dictionary containing the data for the specified node.
        """
        return self.data_dict[node]
