import pytest
import pandas as pd
import json
from gen3_data_validator.resolve_schema import ResolveSchema
from unittest.mock import patch, MagicMock, mock_open


@pytest.fixture
def test_schema_path():
    return "../../schema/gen3_test_schema.json"

def test_init_ResolveSchema(test_schema_path):
    schema = ResolveSchema(test_schema_path)
    assert schema.schema_path == test_schema_path

@pytest.fixture
def ResolveSchema_instance(test_schema_path):
    return ResolveSchema(test_schema_path)

@pytest.fixture
def example_node_name():
    return 'sample'


@pytest.fixture
def base_jsonschema():
    return {
        "sample.yaml": {
            "$schema": "http://json-schema.org/draft-04/schema#",
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
                "$ref": "_definitions.yaml#/ubiquitous_properties",
                "sample_id": {
                    "description": "A unique sample identifier",
                    "type": "string"
                }
            },
            "required": [
                "type",
                "submitter_id",
                "sample_id"
            ]
        },
        "medication.yaml": {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "id": "medication",
            "links": [
                {
                    "backref": "medications",
                    "label": "taken_by",
                    "multiplicity": "one_to_one",
                    "name": "subjects",
                    "required": True,
                    "target_type": "subject"
                }
            ],
            "properties": {
                "$ref": "_definitions.yaml#/ubiquitous_properties",
                "antithrombotic_meds": {
                    "description": "Self-reported / measured use of antithrobotic medication ",
                    "enum": [
                        "yes",
                        "no"
                    ]
                },
                "subjects": {
                    "$ref": "_definitions.yaml#/to_one"
                }
            },
            "required": [
                "type",
                "submitter_id",
                "subjects"
            ]
        },
        "_definitions.yaml": None
        
    }

def test_read_json(ResolveSchema_instance, test_schema_path):
    mock_data = [{"submitter_id": "subject-example-990910001"}]
    with patch("gen3_data_validator.resolve_schema.open",
               mock_open(read_data=json.dumps(mock_data))):
        result = ResolveSchema_instance.read_json(test_schema_path)
        assert result == mock_data


def test_get_nodes(ResolveSchema_instance, example_node_name):
    schema = {
        "sample": "schema_content",
        "medication": "schema_content"
    }
    ResolveSchema_instance.schema = schema
    result = ResolveSchema_instance.get_nodes()
    assert result == ["sample", "medication"]


def test_get_node_link(ResolveSchema_instance):
    schema = {
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
            ]
        }
    }
    links = [
                {
                    "backref": "samples",
                    "label": "taken_from",
                    "multiplicity": "many_to_one",
                    "name": "subjects",
                    "required": True,
                    "target_type": "subject"
                }
            ]
    ResolveSchema_instance.schema = schema
    result = ResolveSchema_instance.get_node_link("sample.yaml")
    assert result == ("sample", links)


def test_get_node_category(ResolveSchema_instance):
    schema = {
        "demographic.yaml": {
            "id": "demographic",
            "category": "clinical"
        }
    }
    ResolveSchema_instance.schema = schema
    node_id, category = ResolveSchema_instance.get_node_category("demographic.yaml")
    assert node_id == "demographic"
    assert category == "clinical"


def test_get_node_properties(ResolveSchema_instance):
    schema = {
        "demographic.yaml": {
            "id": "demographic",
            "properties": {
                "sex": {
                    "description": "Sex of the participant",
                    "enum": ["male", "female", "other"]
                }
            }
        }
    }
    ResolveSchema_instance.schema = schema
    node_id, property_keys = ResolveSchema_instance.get_node_properties("demographic.yaml")
    assert node_id == "demographic"
    assert set(property_keys) == {"sex"}


def test_generate_node_lookup(ResolveSchema_instance):
    # Prepare a mock schema with multiple nodes, including excluded ones
    schema = {
        "demographic.yaml": {
            "id": "demographic",
            "category": "clinical",
            "properties": {
                "sex": {
                    "description": "Sex of the participant",
                    "enum": ["male", "female", "other"]
                }
            }
        },
        "_definitions.yaml": None
    }

    expected = {
        'demographic.yaml': {
            'category': 'clinical',
            'properties': ('demographic', ['sex'])
        }
    }

    ResolveSchema_instance.schema = schema
    ResolveSchema_instance.nodes = ['demographic.yaml', '_definitions.yaml']
    node_lookup = ResolveSchema_instance.generate_node_lookup()
    assert node_lookup == expected


def test_find_upstream_downstream(ResolveSchema_instance):
    schema = {
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
            ]
        }
    }
    ResolveSchema_instance.schema = schema
    node_pairs = ResolveSchema_instance.find_upstream_downstream("sample.yaml")
    assert node_pairs == [("subject", "sample")]

def test_get_all_node_pairs(ResolveSchema_instance):
    schema = {
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
            ]
        },
        "medication.yaml": {
            "id": "medication",
            "links": [
                {
                    "backref": "medications",
                    "label": "taken_from",
                    "multiplicity": "many_to_one",
                    "name": "subjects",
                    "required": True,
                    "target_type": "subject"
                }
            ]
        }
    }
    ResolveSchema_instance.schema = schema
    ResolveSchema_instance.nodes = ["sample.yaml", "medication.yaml"]
    node_pairs = ResolveSchema_instance.get_all_node_pairs()
    assert node_pairs == [("subject", "sample"), ("subject", "medication")]

