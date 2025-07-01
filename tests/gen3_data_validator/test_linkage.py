import pytest
import pandas as pd
import json
from gen3_data_validator.resolve_schema import ResolveSchema
from unittest.mock import patch, MagicMock, mock_open
import os


@pytest.fixture
def test_schema_path():
    return "../../schema/gen3_test_schema.json"


@pytest.fixture
def ResolveSchema_instance(test_schema_path):
    return ResolveSchema(test_schema_path)


@pytest.fixture
def schema():
    return {
        "_settings.yaml": {
            "_dict_version": "3.1.0"
        },
        "_definitions.yaml": {
            "some_def": {"type": "string"}
        },
        "_terms.yaml": {
            "term1": "definition"
        },
        "sample.yaml": {
            "id": "sample",
            "links": [
                {
                    "backref": "samples",
                    "label": "taken_from",
                    "multiplicity": "many_to_one",
                    "name": "subjects",
                    "required": True,
                    "target_type": "subject"
                }
            ],
            "properties": {
                "sample_id": {"type": "string"}
            }
        },
        "subject.yaml": {
            "id": "subject",
            "properties": {
                "subject_id": {"type": "string"}
            }
        }
    }





def test_did_ResolveSchema_produce_outputs(monkeypatch, ResolveSchema_instance, schema):
    # Patch read_json to return our schema
    monkeypatch.setattr(ResolveSchema_instance, "read_json", lambda path: schema)
    # Patch get_nodes to return the node keys
    monkeypatch.setattr(ResolveSchema_instance, "get_nodes", lambda: list(schema.keys()))
    # Patch get_all_node_pairs to use the real method (it uses self.schema and self.nodes)
    # Patch split_json to return a list of node dicts (excluding _definitions.yaml and _terms.yaml)
    def fake_split_json():
        return [schema[k] for k in schema if k.endswith(".yaml") and not k.startswith("_")]
    monkeypatch.setattr(ResolveSchema_instance, "split_json", fake_split_json)
    # Patch return_schema to return the relevant dict
    monkeypatch.setattr(ResolveSchema_instance, "return_schema", lambda k: schema.get(k))
    # Patch resolve_references to just return the input schema for simplicity
    monkeypatch.setattr(ResolveSchema_instance, "resolve_references", lambda s, t: s)
    # Patch schema_list_to_json to just return the input list
    monkeypatch.setattr(ResolveSchema_instance, "schema_list_to_json", lambda l: l)

    # Now call resolve_schema
    ResolveSchema_instance.resolve_schema()

    # Check that the attributes are set as expected
    assert ResolveSchema_instance.schema == schema
    assert set(ResolveSchema_instance.nodes) == set(schema.keys())
    assert isinstance(ResolveSchema_instance.node_pairs, list)
    assert isinstance(ResolveSchema_instance.node_order, list)
    assert isinstance(ResolveSchema_instance.schema_list, list)
    assert ResolveSchema_instance.schema_def == schema["_definitions.yaml"]
    assert ResolveSchema_instance.schema_term == schema["_terms.yaml"]
    assert ResolveSchema_instance.schema_def_resolved == schema["_definitions.yaml"]
    assert isinstance(ResolveSchema_instance.schema_list_resolved, list)
    assert ResolveSchema_instance.schema_resolved == ResolveSchema_instance.schema_list_resolved
    assert ResolveSchema_instance.schema_version == "3.1.0"

# Still need to add more tests