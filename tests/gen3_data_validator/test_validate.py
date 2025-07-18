import pytest
import pandas as pd
import json
from gen3_data_validator.validate import Validate, ValidateStats, ValidateSummary
from unittest.mock import patch, MagicMock, mock_open
import os


@pytest.fixture
def mock_data_map_fail():
    with open('tests/data/data_maps/fail_test_data_map.json') as f:
        return json.load(f)


@pytest.fixture
def mock_data_map_pass():
    with open('tests/data/data_maps/pass_test_data_map.json') as f:
        return json.load(f)


@pytest.fixture
def mock_resolved_schema():
    with open('tests/schema/gen3_test_schema_resolved.json') as f:
        return json.load(f)


@pytest.fixture
def validator_pass_fixture(mock_data_map_pass, mock_resolved_schema):
    return Validate(data_map=mock_data_map_pass, resolved_schema=mock_resolved_schema)


@pytest.fixture
def validator_fail_fixture(mock_data_map_fail, mock_resolved_schema):
    return Validate(data_map=mock_data_map_fail, resolved_schema=mock_resolved_schema)


def test_init_Validate(validator_pass_fixture, mock_data_map_pass, mock_resolved_schema):
    validate = validator_pass_fixture
    assert validate.data_map == mock_data_map_pass
    assert validate.resolved_schema == mock_resolved_schema
    assert validate.validation_result is None
    assert validate.key_map is None

