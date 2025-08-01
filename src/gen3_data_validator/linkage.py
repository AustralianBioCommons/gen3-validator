from typing import Dict, Any, List
from pydantic import create_model


class TestLinkage:
    def __init__(self, root_node: List[str] = None):
        """
        Initializes the TestLinkage class with injected dependencies.

        Args:
            schema_resolver (ResolveSchema): An instance of ResolveSchema for
                schema-related operations.
            data_parser (ParseData): An instance of ParseData for data parsing
                operations.
            root_node (list[str], optional): List of root node names. Defaults
                to ['subject'].
        """
        if root_node is None:
            root_node = ['subject']
        self.root_node = root_node
        

    def _find_fk(self, data: dict) -> str:
        """
        Identifies the foreign key in a given data dictionary.

        This method iterates over the key-value pairs in the provided data dictionary
        and checks if any value is a dictionary containing a 'submitter_id' key. If such
        a dictionary is found, the corresponding key is returned as the foreign key.

        Args:
            data (dict): A dictionary representing a single data record.

        Returns:
            str: The key corresponding to the foreign key if found, otherwise None.
        """
        for key, value in data.items():
            if isinstance(value, dict) and 'submitter_id' in value:
                return key
        return None

    def generate_config(self, data_map, link_suffix: str = 's') -> dict:
        """
        Generates a configuration dictionary for entities based on the data map.

        This method creates a configuration dictionary where each key is an entity name
        and the value is a dictionary containing 'primary_key' and 'foreign_key' for that
        entity. The primary key is constructed using the entity name and the provided link
        suffix. The foreign key is determined by searching for a key in the data that
        contains a 'submitter_id'.

        Args:
            data_map (dict): A dictionary where each key is an entity name and the value
                is a list of data records for that entity.
            link_suffix (str, optional): A suffix to append to the primary key. Defaults to 's'.

        Returns:
            dict: A configuration dictionary with primary and foreign keys for each entity.
        """
        config = {}
        for node, data in data_map.items():
            fk = self._find_fk(data[0])
            if fk:
                config[node] = {
                    "primary_key": f"{node}{link_suffix}",
                    "foreign_key": f"{fk}"
                }
            else:
                config[node] = {
                    "primary_key": f"{node}{link_suffix}",
                    "foreign_key": None
                }
        return config

    def test_config_links(self, config_map: Dict[str, Any], root_node: List[str] = None) -> dict:
        """
        Validates the configuration map by checking the foreign key links between entities.

        This method checks if the foreign key of each entity in the config map matches
        the primary key of any other entity. If a match is not found and the entity is
        not a root node, it records the broken link. Root nodes are allowed to have
        unmatched foreign keys.

        Args:
            config_map (Dict[str, Any]): A dictionary containing the configuration of entities,
                where each key is an entity name and the value is a dictionary with 'primary_key'
                and 'foreign_key'.
            root_node (List[str], optional): A list of root node names that are allowed to have
                unmatched foreign keys. Defaults to ['subject'].

        Returns:
            dict: A dictionary of entities with broken links and their foreign keys if any are found.
                  Returns "valid" if no broken links are detected.
        """
        if root_node is None:
            root_node = ['subject']
        broken_links = {}

        print("=== Validating Config Map ===")
        print(f"Root Node = {root_node}")

        for key, value in config_map.items():
            fk = value['foreign_key']

            # Check if fk of the current key matches with the primary key of any
            # of the other entities
            match_found = any(
                fk == v['primary_key']
                for k, v in config_map.items() if k != key
            )

            if not match_found and fk is not None:
                # If the key is a root node, ignore the broken link
                if key not in root_node:
                    broken_links[key] = fk
                else:
                    print(
                        f"WARNING: Ignoring broken link for root node '{key}' "
                        f"with foreign key '{fk}'"
                    )

        if len(broken_links) == 0:
            print("Config Map Validated")
            return "valid"
        else:
            print("Config Map Invalid ('entity': 'foreign_key')")
            print("Broken links:", broken_links)
            return broken_links

    def get_foreign_keys(
        self, data_map: Dict[str, List[Dict[str, Any]]], config: Dict[str, Any]
    ) -> dict:
        """
        Uses the config to read the entity data from the data_map, and then
        uses the FK key outlined in the config to find the foreign key values.

        Args:
            data_map (Dict[str, List[Dict[str, Any]]]): The data map containing
                the entity data
            config (Dict[str, Any]): The config dictionary

        Returns:
            dict: dictionary of entities and their foreign key values
        """
        fk_entities = {}

        for config_entity, config_keys in config.items():
            entity_data = data_map[config_entity]
            records_list = []

            for record in entity_data:
                fk = record.get(config_keys['foreign_key'])
                if fk:
                    if 'submitter_id' in fk:
                        records_list.append(fk['submitter_id'])
                    else:
                        records_list.append(fk)

            fk_entities[config_entity] = records_list
        return fk_entities

    def get_primary_keys(
        self, data_map: Dict[str, List[Dict[str, Any]]], config: Dict[str, Any]
    ) -> dict:
        """
        Uses the config to read the entity data from the data_map, and then
        uses the PK key outlined in the config to find the primary key values.

        Args:
            data_map (Dict[str, List[Dict[str, Any]]]): The data map containing
                the entity data
            config (Dict[str, Any]): The config dictionary

        Returns:
            dict: dictionary of entities and their primary key values
        """
        pk_entities = {}

        for config_entity, config_keys in config.items():
            entity_data = data_map[config_entity]
            records_list = []

            for record in entity_data:
                pk = record.get(config_keys['primary_key'])
                if pk:
                    if 'submitter_id' in pk:
                        records_list.append(pk['submitter_id'])
                    else:
                        records_list.append(pk)

            pk_entities[config_entity] = records_list
        return pk_entities

    def validate_links(
        self, data_map: Dict[str, List[Dict[str, Any]]], config: Dict[str, Any],
        root_node: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Verifies Config file, then extracts primary and foreign key values
        from the data map. Then uses the foreign key values to validate the
        primary key values.

        Args:
            data_map (Dict[str, List[Dict[str, Any]]]): Contains the data for
                each entity
            config (Dict[str, Any]): The entity linkage configx

        Returns:
            Dict[str, List[str]]: Dictionary of entities and their validation
                results
        """
        if root_node is None:
            root_node = ['subject']

        # validating config map
        valid_config = self.test_config_links(config, root_node=root_node)
        if valid_config != "valid":
            print("Invalid Config Map")
            print(config)
            return valid_config

        fk_entities = self.get_foreign_keys(data_map, config)
        pk_entities = self.get_primary_keys(data_map, config)

        print("=== Validating Links ===")

        validation_results = {}
        for entity, fk_values in fk_entities.items():
            invalid_keys = [
                fk for fk in fk_values if all(
                    fk not in pk_values for pk_values in pk_entities.values()
                )
            ]
            validation_results[entity] = invalid_keys
            print(
                f"Entity '{entity}' has {len(invalid_keys)} invalid foreign keys: "
                f"{invalid_keys}"
            )
        return validation_results
