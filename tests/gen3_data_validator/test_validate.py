import pytest
import pandas as pd
import json
from gen3_data_validator.validate import Validate, ValidateStats, ValidateSummary
from unittest.mock import patch, MagicMock, mock_open
import os


@pytest.fixture
def mock_data_map():
    return {
        'lipidomics_assay': [{'key1': 'value1'}, {'key2': 'value2'}],
        'sample': [{'key3': 'value3'}, {'key4': 'value4'}]
    }


@pytest.fixture
def mock_resolved_schema():
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "key1": {"type": "string"},
            "key2": {"type": "string"},
        },
        "additionalProperties": False,
        "required": []
    }


def test_init_Validate(mock_data_map, mock_resolved_schema):
    validate = Validate(data_map=mock_data_map, resolved_schema=mock_resolved_schema)
    assert validate.data_map == mock_data_map
    assert validate.resolved_schema == mock_resolved_schema
    assert validate.validation_result is None
    assert validate.key_map is None

# TODO - Create data folder in tests dir containing schema, resolved schema, and some example data file, maybe two data nodes, with two objects each