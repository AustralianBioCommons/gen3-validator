from jsonschema import Draft4Validator
from functools import wraps
from datetime import datetime
from functools import wraps
from time import time
import pandas as pd
import json
import uuid
import logging

logger = logging.getLogger(__name__)

class Validate:
    
    def __init__(self, data_map, resolved_schema):
        self.data_map = data_map
        self.resolved_schema = resolved_schema
        logger.info("Initializing Validate class with data map and resolved schema.")
        self.validation_result = self.validate_schema(self.data_map, self.resolved_schema)
    
    
    def validate_object(self, obj, idx, validator) -> list:
        """
        Validates a single JSON object against a provided JSON schema validator.

        Parameters:
        - obj (dict): The JSON object to validate.
        - idx (int): The index of the object in the dataset.
        - validator (Draft4Validator): The JSON schema validator to use for validation.

        Returns:
        - list: A list of dictionaries containing validation results and log messages.
        """
        validation_results = []
        try:
            errors = list(validator.iter_errors(obj))
            logger.debug(f"Object at index {idx} validated with {len(errors)} errors.")
        except Exception as e:
            logger.error(f"Error in validate_object during object validation at index {idx}: {e}")
            return validation_results

        if len(errors[1:]) == 0:
            result = {
                "index": idx,
                "validation_result": "PASS",
                "invalid_key": None,
                "schema_path": None,
                "validator": None,
                "validator_value": None,
                "validation_error": None
            }
            validation_results.append(result)
        else:
            for error in errors[1:]:
                invalid_key = ".".join(str(k) for k in error.path) if error.path else "root"
                schema_path = ".".join(str(k) for k in error.schema_path)

                result = {
                    "index": idx,
                    "validation_result": "FAIL",
                    "invalid_key": invalid_key,
                    "schema_path": schema_path,
                    "validator": error.validator,
                    "validator_value": error.validator_value,
                    "validation_error": error.message
                }
                validation_results.append(result)

        return validation_results

    def validate_schema(self, data_map: dict, resolved_schema: dict) -> dict:
        """
        Takes in a dictionary of data, where the key is the entity name, and the value is a list of jsons containing the data.
        The function then validates the data against the resolved schema.
        
        Args:
        - data_map (dict): A dictionary where keys are entity names and values are lists of JSON objects to be validated.
        - resolved_schema (dict): A dict of resolved JSON schema objects to validate against.

        Returns:
        - dict: A dictionary containing validation results for each entity.
        """
        validation_results = {}
        
        try:
            logger.info("Validating Data with Schema...")
            data_nodes = list(data_map.keys())
            logger.info(f"Data nodes: {data_nodes}")
            schema_keys = [key[:-5] if key.endswith('.yaml') else key for key in resolved_schema.keys()]
            logger.info(f"Schema keys: {schema_keys}")
        except Exception as e:
            logger.error(f"Error in validate_schema accessing data or schema keys: {e}")
            return validation_results
        
        for node in data_nodes:
            if node not in schema_keys:
                logger.warning(f"Warning: {node} not found in resolved schema keys.")
                continue
        
            try:
                data = data_map[node]
                schema = resolved_schema[f"{node}.yaml"]
                validator = Draft4Validator(schema)
                logger.info(f"Validator set up for node {node}.")
            except Exception as e:
                logger.error(f"Error in validate_schema setting up validator for node {node}: {e}")
                continue

            node_results = []
            for idx, obj in enumerate(data):
                try:
                    result = self.validate_object(obj, idx, validator)
                    result = {"index_" + str(idx): result}
                    node_results.append(result)
                except Exception as e:
                    logger.error(f"Error in validate_schema validating object at index {idx} for node {node}: {e}")
                
            validation_results[node] = node_results
        
        return validation_results
    
    def list_entities(self) -> list:
        """
        Lists all entities present in the validation results.

        Returns:
            list: A list of entity names.
        """
        try:
            entities = list(self.validation_result.keys())
            logger.info(f"Entities listed: {entities}")
            return entities
        except Exception as e:
            logger.error(f"Error in list_entities: {e}")
            return []
    
    def list_index_by_entity(self, entity: str) -> list:
        """
        Lists all index keys for a specified entity.

        Args:
            entity (str): The name of the entity to list index keys for.

        Returns:
            list: A list of index keys for the specified entity.
        """
        index_list = []
        try:
            logger.info(f"Generating list of indexes for {entity}")
            for obj in self.validation_result[entity]:
                index_list.append(list(obj.keys())[0])
        except Exception as e:
            logger.error(f"Error in list_index_by_entity for entity {entity}: {e}")
        return index_list
    
    def make_keymap(self) -> dict:
        """
        Creates a dictionary that maps entities to their corresponding index keys.

        Returns:
            dict: A dictionary where each key is an entity name and each value is a list of index keys for that entity.
        """
        try:
            entities = self.list_entities()
            key_map = {}
            for entity in entities:
                key_map[entity] = self.list_index_by_entity(entity)
            logger.info(f"Keymap created: {key_map}")
            return key_map
        except Exception as e:
            logger.error(f"Error in make_keymap: {e}")
            return {}
        
    def pull_entity(self, entity: str, result_type: str = "FAIL") -> list:
        """
        Retrieves the validation results for a specified entity.

        Args:
            entity (str): The name of the entity to retrieve validation results for.
            result_type (str, optional): The type of validation result to return. Either ["PASS", "FAIL", "ALL"]

        Returns:
            list: A list of validation results for the specified entity, or None if no results are found.
        """
        return_objects = []
        try:
            if len(self.validation_result.get(entity, [])) == 0:
                logger.info(f"No validation results found for entity {entity}.")
                return None

            for obj in self.validation_result[entity]:
                obj_values = list(obj.values())
                val_result = obj_values[0][0]["validation_result"]
                
                if result_type == "ALL":
                    return_objects.append(obj)
                    continue
                
                if val_result == result_type:
                    return_objects.append(obj)
            logger.info(f"Pulled {result_type} results for entity {entity}: {len(return_objects)} results found.")
        except Exception as e:
            logger.error(f"Error in pull_entity for entity {entity}: {e}")

        return return_objects

    def pull_index_of_entity(self, entity: str, index_key: int, result_type: str = "FAIL", return_failed: bool = True) -> dict:
        """
        Retrieves the validation result for a specified entity and index key.

        Args:
            entity (str): The name of the entity to retrieve validation results for.
            index_key (int): The index key of the validation result to retrieve.
            result_type (str, optional): The type of validation result to return. Either ["PASS", "FAIL", "ALL"]
            return_failed (bool, optional): Flag to determine if only failed results should be returned.

        Returns:
            dict: The validation result for the specified entity and index key, or None if not found.
        """
        try:
            data = self.validation_result[entity]
            index_data = next((item[index_key] for item in data if index_key in item), None)
            
            return_list = []
            for obj in index_data:
                val_result = obj.get("validation_result")
                
                if result_type == "ALL":
                    return_list.append(obj)
                    continue
                
                if val_result == result_type:
                    return_list.append(obj)
            
            return return_list
        except Exception as e:
            logger.error(f"Error in pull_index_of_entity for entity {entity} at index {index_key}: {e}")
            return []
    


class ValidateStats(Validate):
    def __init__(self, validate_instance: Validate):
        self.data_map = validate_instance.data_map
        self.resolved_schema = validate_instance.resolved_schema
        self.validation_result = validate_instance.validation_result
        logger.info("Initializing ValidateStats class.")
        
    
    def n_rows_with_errors(self, entity: str) -> int:
        """
        Returns the number of rows that have validation errors for a given entity.

        Args:
            entity (str): The name of the entity to check for validation errors.

        Returns:
            int: The number of rows with validation errors.
        """
        try:
            n_rows = len(self.pull_entity(entity))
            logger.info(f"Number of rows with errors for entity {entity}: {n_rows}")
            return n_rows
        except Exception as e:
            logger.error(f"Error in n_rows_with_errors for entity {entity}: {e}")
            return 0
    
    def count_results_by_index(self, entity: str, index_key: str, result_type: str = "FAIL", print_results: bool = False):
        """
        Counts the number of validation results based on a specified entity and index_key.
        For example the entity 'sample' will have an error in row 1 / index 1, which contains
        5 validation errors due to errors in 5 columns for that row. So the method will return
        5 validation errors.

        Args:
            entity (str): The name of the entity to count validation results for.
            index_key (str): The key/index to count validation results for.
            result_type (str, optional): The type of validation result to count. Either ["PASS", "FAIL", "ALL"]
            print_results (bool, optional): Flag to print the results.

        Returns:
            int: The number of validation results for the specified key/index.
        """
        validation_count = 0
        val_result = None
        try:
            index_data = self.pull_index_of_entity(entity = entity, index_key = index_key, result_type = result_type)
            for obj in index_data:
                val_result = obj.get("validation_result", None)
                if result_type == "ALL":
                    validation_count += 1
                    continue

            if val_result == result_type:
                validation_count += 1

            if print_results:
                print(f"Number of {result_type} validations for {entity} at {index_key}': {validation_count}")
        except Exception as e:
            logger.error(f"Error in count_results_by_index for entity {entity} at index {index_key}: {e}")
        return validation_count


    def count_results_by_entity(self, entity: str, result_type: str = "FAIL", print_results: bool = False) -> int:
        """
        Counts the number of validation results for a specified entity. Each entry in the 
        entity may produce more than one validation error, which will be counted. For 
        example, one entry, in 'sample' may result in 5 validation errors. This function counts
        the total number of validation errors for a whole entity.

        Args:
            entity (str): The name of the entity to count failed validation results for.
            result_type (str, optional): The type of validation result to count. Either ["PASS", "FAIL", "ALL"]
            print_results (bool, optional): Flag to print the results.

        Returns:
            int: The number of failed validation results for the specified entity.
        """
        validation_count = 0
        try:
            index_keys = self.list_index_by_entity(entity=entity)
            
            for index_key in index_keys:
                count = self.count_results_by_index(entity=entity, index_key=index_key, result_type=result_type)
                validation_count += count
            
            if print_results:
                logger.info(f"Number of total {result_type} validations for '{entity}': {validation_count}")
        except Exception as e:
            logger.error(f"Error in count_results_by_entity for entity {entity}: {e}")
        return validation_count
    
    def n_errors_per_entity(self, entity: str) -> int:
        """
        Returns the number of errors that have validation errors for a given entity.

        Args:
            entity (str): The name of the entity to check for validation errors.

        Returns:
            int: The number of rows with validation errors.
        """
        try:
            n_errors = len(self.pull_entity(entity, return_failed=True))
            logger.info(f"Number of errors per entity {entity}: {n_errors}")
            return n_errors
        except Exception as e:
            logger.error(f"Error in n_errors_per_entity for entity {entity}: {e}")
            return 0
    
    
    def n_errors_per_entry(self, entity: str, index_key: int) -> int:
        """
        Returns the number of validation errors for a given entity and index.

        Args:
            entity (str): The name of the entity to check for validation errors.
            index_key (int): The index of the row to check for validation errors.

        Returns:
            int: The number of validation errors for the given entity and index.
        """
        try:
            n_errors = len(self.pull_index_of_entity(entity, index_key))
            logger.info(f"Number of errors per entry for entity {entity} at index {index_key}: {n_errors}")
            return n_errors
        except Exception as e:
            logger.error(f"Error in n_errors_per_entry for entity {entity} at index {index_key}: {e}")
            return 0
    
    def total_validation_errors(self) -> int:
        """
        Calculates the total number of validation errors across all entities.

        Returns:
            int: The total number of validation errors.
        """
        error_count = 0
        try:
            for entity in self.list_entities():
                error_count += self.count_results_by_entity(entity=entity, result_type="FAIL")
            logger.info(f"Total validation errors: {error_count}")
            print(f"Total validation errors: {error_count}")
        except Exception as e:
            logger.error(f"Error in total_validation_errors: {e}")
        return error_count
    
    
    def summary_stats(self) -> pd.DataFrame:
        """
        Generates and prints a summary of validation statistics.

        This method calculates the total number of validation errors across all entities
        and provides detailed statistics for each entity, including the number of rows
        with errors and the total number of errors per entity. The results are printed
        to the console and returned as a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the summary statistics with columns
            'entity', 'number_of_rows_with_errors', and 'number_of_errors_per_entity'.
        """
        import pandas as pd

        try:
            total_errors = self.total_validation_errors()
            logger.info(f"Total validation errors: {total_errors}")
            
            summary_data = []
            for entity in self.list_entities():
                n_rows_with_errors = self.n_rows_with_errors(entity)
                n_errors_per_entity = self.count_results_by_entity(entity, result_type='FAIL')
                
                summary_data.append({
                    "entity": entity,
                    "number_of_rows_with_errors": n_rows_with_errors,
                    "number_of_errors_per_entity": n_errors_per_entity
                })
            
            summary_df = pd.DataFrame(summary_data)
            logger.info("Summary statistics generated.")
            return summary_df
        except Exception as e:
            logger.error(f"Error in summary_stats: {e}")
            return pd.DataFrame()
    

class ValidateSummary(Validate):
    def __init__(self, validate_instance: Validate):
        self.data_map = validate_instance.data_map
        self.resolved_schema = validate_instance.resolved_schema
        self.validation_result = validate_instance.validation_result
        super().__init__(validate_instance.data_map, validate_instance.resolved_schema)
        self.flattened_validation_results = None
        logger.info("Initializing ValidateSummary class.")
    
    
    
    def flatten_validation_results(self, result_type: str = "FAIL") -> dict:
        """
        Flattens the validation results created when initializing the Validate class.
        
        This method extracts all the validation results for each entity, each index row, 
        and each entry in the index row. It effectively pulls all the entries for a 
        particular entity, row, and column, where one row can produce validation errors 
        in multiple columns.

        Args:
            result_type (str): The type of validation result to filter by, default is "FAIL".

        Returns:
            dict: A dictionary containing flattened validation results with a unique GUID 
            for each entry, along with the entity and other relevant validation details.
        """
        try:
            key_map = self.make_keymap()
            
            flattened_results = []
            for entity, index_list in key_map.items():
                for index in index_list:
                    index_obj = self.pull_index_of_entity(entity=entity, index_key=index, result_type=result_type)
                    flattened_results.extend(
                        {"row": index.strip("index_"),
                         "entity": entity,
                         "guid": str(uuid.uuid4()), 
                         **obj} for obj in index_obj
                    )
            
            self.flattened_validation_results = flattened_results
            logger.info(f"Flattened '{result_type}' validation results: {len(flattened_results)}")
            return flattened_results
        except Exception as e:
            logger.error(f"Error in flatten_validation_results: {e}")
            return {}
    
    def flattened_results_to_pd(self) -> pd.DataFrame:
        """
        Transforms the flattened validation results into a pandas DataFrame.

        This function retrieves the flattened validation results stored in the instance
        and converts them into a pandas DataFrame. The DataFrame is then sorted by 
        'entity' and 'row' for organized analysis or processing.

        Returns:
            pd.DataFrame: A DataFrame containing the sorted and indexed flattened 
            validation results.
        """
        try:
            logger.info("Converting flattened results to pandas dataframe...")
            pd_df = pd.json_normalize(self.flattened_validation_results)
            pd_df.sort_values(by=['entity', 'row'], inplace=True)
            pd_df.reset_index(drop=True, inplace=True)
            return pd_df
        except Exception as e:
            logger.error(f"Error in flattened_results_to_pd: {e}")
            return pd.DataFrame()
    
    def collapse_flatten_results_to_pd(self) -> pd.DataFrame:
        """
        Collapses the flattened validation results into a summarized pandas DataFrame.

        This method groups the flattened validation results by 'validation_error' and
        aggregates other columns to provide a summary of the validation errors, including
        the count of occurrences for each error type.

        Returns:
            pd.DataFrame: A DataFrame containing the collapsed summary of validation errors,
            sorted by entity, validation error, and count.
        """
        try:
            logger.info("Collapsing flattened results to pandas dataframe...")
            pd_df = pd.json_normalize(self.flattened_validation_results)
            collapsed_df = pd_df.groupby('validation_error').agg({
                'entity': 'first',
                'row': 'count'
            }).rename(columns={'row': 'count'}).reset_index()
            collapsed_df = collapsed_df[['entity', 'count', 'validation_error']]
            collapsed_df = collapsed_df.sort_values(by=['entity', 'validation_error', 'count']).reset_index(drop=True)
            return collapsed_df
        except Exception as e:
            logger.error(f"Error in collapse_flatten_results_to_pd: {e}")
            return pd.DataFrame()
