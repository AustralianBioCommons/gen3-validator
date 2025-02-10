import json
from collections import defaultdict, deque


class ResolveSchema:
    def __init__(self, schema_path: str):
        """
        Initialize the ResolveSchema class.

        Parameters:
        - schema_path (str): The path to the JSON schema file.
        """
        self.schema_path = schema_path
        self.schema = self.read_json(self.schema_path)
        self.nodes = self.get_nodes()
        self.node_pairs = self.get_all_node_pairs()
        self.node_order = self.get_node_order(edges=self.node_pairs)
        self.schema_list = self.split_json()
        self.schema_def = self.return_schema("_definitions.yaml")
        self.schema_term = self.return_schema("_terms.yaml")
        self.schema_def_resolved = self.resolve_references(
            self.schema_def, self.schema_term
        )
        self.schema_list_resolved = self.resolve_all_references()

    def read_json(self, path: str) -> dict:
        """
        Read a JSON file and return its contents as a dictionary.

        Parameters:
        - path (str): The path to the JSON file.

        Returns:
        - dict: The contents of the JSON file.
        """
        with open(path) as f:
            return json.load(f)

    def get_nodes(self) -> list:
        """
        Retrieve all node names from the schema.

        Returns:
        - list: A list of node names.
        """
        nodes = list(self.schema.keys())
        return nodes

    def get_node_link(self, node_name: str) -> tuple:
        """
        Retrieve the links and ID for a given node.

        Parameters:
        - node_name (str): The name of the node.

        Returns:
        - tuple: A tuple containing the node ID and its links.
        """
        links = self.schema[node_name]["links"]
        node_id = self.schema[node_name]["id"]
        if "subgroup" in links[0]:
            return node_id, links[0]["subgroup"]
        else:
            return node_id, links

    def find_upstream_downstream(self, node_name: str) -> list:
        """
        Takes a node name and returns the upstream and downstream nodes.

        Parameters:
        - node_name (str): The name of the node.

        Returns:
        - list: A list of tuples representing upstream and downstream nodes.
        """
        node_id, links = self.get_node_link(node_name)

        # Ensure links is a list
        if isinstance(links, dict):
            links = [links]

        results = []

        for link in links:
            target_type = link.get("target_type")

            if not node_id or not target_type:
                print("Missing essential keys in link:", link)
                results.append((None, None))
                continue

            results.append((target_type, node_id))

        return results

    def get_all_node_pairs(
        self,
        excluded_nodes=[
            "_definitions.yaml",
            "_terms.yaml",
            "_settings.yaml",
            "program.yaml",
        ],
    ) -> list:
        """
        Retrieve all node pairs, excluding specified nodes.

        Parameters:
        - excluded_nodes (list): A list of node names to exclude.

        Returns:
        - list: A list of node pairs.
        """
        node_pairs = []
        for node in self.nodes:
            if node not in excluded_nodes:
                node_pairs.extend(self.find_upstream_downstream(node))
            else:
                continue
        return node_pairs

    def get_node_order(self, edges: list) -> list:
        """
        Determine the order of nodes based on their dependencies.

        Parameters:
        - edges (list): A list of tuples representing node dependencies.

        Returns:
        - list: A list of nodes in topological order.
        """
        # Build graph representation
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        for upstream, downstream in edges:
            graph[upstream].append(downstream)
            in_degree[downstream] += 1
            if upstream not in in_degree:
                in_degree[upstream] = 0

        # Perform Topological Sorting (Kahn's Algorithm)
        sorted_order = []
        zero_in_degree = deque([node for node in in_degree if in_degree[node] == 0])

        while zero_in_degree:
            node = zero_in_degree.popleft()
            sorted_order.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    zero_in_degree.append(neighbor)

        # Ensure core_metadata_collection is last
        sorted_order.remove("core_metadata_collection")
        sorted_order.append("core_metadata_collection")

        return sorted_order

    def split_json(self) -> list:
        """
        Split the schema into a list of individual node schemas.

        Returns:
        - list: A list of node schemas.
        """
        schema_list = []
        for node in self.nodes:
            schema_list.append(self.schema[node])
        return schema_list

    def return_schema(self, target_id: str) -> dict:
        """
        Retrieves the first dictionary from a list where the 'id' key matches the target_id.

        Parameters:
        - target_id (str): The value of the 'id' key to match.

        Returns:
        - dict: The dictionary that matches the target_id, or None if not found.
        """
        if target_id.endswith(".yaml"):
            target_id = target_id[:-5]

        result = next(
            (item for item in self.schema_list if item.get("id") == target_id), None
        )
        if result is None:
            print(f"{target_id} not found")
        return result

    def resolve_references(self, schema: dict, reference: dict) -> dict:
        """
        Takes a gen3 jsonschema draft 4 as a dictionary and recursively
        resolves any references using a reference schema which has no
        references.

        Parameters:
        - schema (dict): The JSON node to resolve references in.
        - reference (dict): The schema containing the references.

        Returns:
        - dict: The resolved JSON node with references resolved.
        """
        ref_input_content = reference

        def resolve_node(node, manual_ref_content=ref_input_content):
            if isinstance(node, dict):
                if "$ref" in node:
                    ref_path = node["$ref"]
                    ref_file, ref_key = ref_path.split("#")
                    ref_file = ref_file.strip()
                    ref_key = ref_key.strip("/")

                    # if a reference file is in the reference, load the pre-defined reference, if no file exists, then use the schema itself as reference
                    if ref_file:
                        ref_content = manual_ref_content
                    else:
                        ref_content = schema

                    for part in ref_key.split("/"):
                        ref_content = ref_content[part]

                    resolved_content = resolve_node(ref_content)
                    # Merge resolved content with the current node, excluding the $ref key
                    return {
                        **resolved_content,
                        **{k: resolve_node(v) for k, v in node.items() if k != "$ref"},
                    }
                else:
                    return {k: resolve_node(v) for k, v in node.items()}
            elif isinstance(node, list):
                return [resolve_node(item) for item in node]
            else:
                return node

        return resolve_node(schema)

    def resolve_all_references(self) -> list:
        """
        Resolves references in all other schema dictionaries using the resolved definitions schema.

        Returns:
        - list: A list of resolved schema dictionaries.
        """

        print("=== Resolving Schema References ===")

        resolved_schema_list = []
        for node in self.nodes:
            if node == "_definitions.yaml" or node == "_terms.yaml":
                continue

            try:
                resolved_schema = self.resolve_references(
                    self.schema[node], self.schema_def_resolved
                )
                resolved_schema_list.append(resolved_schema)
                print(f"Resolved {node}")
            except KeyError as e:
                print(f"Error resolving {node}: Missing key {e}")
            except Exception as e:
                print(f"Error resolving {node}: {e}")

        return resolved_schema_list

    def return_resolved_schema(self, target_id: str) -> dict:
        """
        Retrieves the first dictionary from a list where the 'id' key matches the target_id.

        Parameters:
        - target_id (str): The value of the 'id' key to match.

        Returns:
        - dict: The dictionary that matches the target_id, or None if not found.
        """
        if target_id.endswith(".yaml"):
            target_id = target_id[:-5]

        result = next(
            (item for item in self.schema_list_resolved if item.get("id") == target_id),
            None,
        )
        if result is None:
            print(f"{target_id} not found")
        return result
