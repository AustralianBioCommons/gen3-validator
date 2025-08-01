import pytest
import pandas as pd
import json
from gen3_data_validator.validate import Validate, ValidateStats, ValidateSummary
from unittest.mock import patch, MagicMock, mock_open
import os
from jsonschema import Draft4Validator


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

@pytest.fixture
def index_0_validator_sample_fail_result():
    return [
        {
            'index': 0,
            'validation_result': 'FAIL',
            'invalid_key': 'freeze_thaw_cycles',
            'schema_path': 'properties.freeze_thaw_cycles.type',
            'validator': 'type',
            'validator_value': 'integer',
            'validation_error': "'10' is not of type 'integer'"
        },
        {
            'index': 0,
            'validation_result': 'FAIL',
            'invalid_key': 'sample_provider',
            'schema_path': 'properties.sample_provider.enum',
            'validator': 'enum',
            'validator_value': ['Baker', 'USYD', 'UMELB', 'UQ'],
            'validation_error': "45 is not one of ['Baker', 'USYD', 'UMELB', 'UQ']"
        },
        {
            'index': 0,
            'validation_result': 'FAIL',
            'invalid_key': 'sample_storage_method',
            'schema_path': 'properties.sample_storage_method.enum',
            'validator': 'enum',
            'validator_value': [
                'not stored',
                'ambient temperature',
                'cut slide',
                'fresh',
                'frozen, -70C freezer',
                'frozen, -150C freezer',
                'frozen, liquid nitrogen',
                'frozen, vapor phase',
                'paraffin block',
                'RNAlater, frozen',
                'TRIzol, frozen'
            ],
            'validation_error': "'Autoclave' is not one of ['not stored', 'ambient temperature', 'cut slide', 'fresh', 'frozen, -70C freezer', 'frozen, -150C freezer', 'frozen, liquid nitrogen', 'frozen, vapor phase', 'paraffin block', 'RNAlater, frozen', 'TRIzol, frozen']"
        }
    ]


def test_init_Validate_pass(validator_pass_fixture, mock_data_map_pass, mock_resolved_schema):
    validate = validator_pass_fixture
    assert validate.data_map == mock_data_map_pass
    assert validate.resolved_schema == mock_resolved_schema
    assert validate.validation_result is None
    assert validate.key_map is None

def test_init_Validate_fail(validator_fail_fixture, mock_data_map_fail, mock_resolved_schema):
    validate = validator_fail_fixture
    assert validate.data_map == mock_data_map_fail
    assert validate.resolved_schema == mock_resolved_schema
    assert validate.validation_result is None
    assert validate.key_map is None

def test_validate_object(validator_fail_fixture, index_0_validator_sample_fail_result):
    validate = validator_fail_fixture
    idx = 0
    obj = validate.data_map['sample'][idx]
    validator = Draft4Validator(validate.resolved_schema['sample.yaml'])
    validate_result = validate.validate_object(obj, idx, validator)
    assert validate_result == index_0_validator_sample_fail_result


def test_validate_schema_fail(validator_fail_fixture, mock_data_map_fail):
    validate = validator_fail_fixture
    validate_result = validate.validate_schema()
    assert 'index_0' == list(validate_result['sample'][0].keys())[0]
    assert len(validate_result['sample'][0]['index_0']) == 3

    expected_error = {
        'index': 0,
        'validation_result': 'FAIL',
        'invalid_key': 'freeze_thaw_cycles',
        'schema_path': 'properties.freeze_thaw_cycles.type',
        'validator': 'type',
        'validator_value': 'integer',
        'validation_error': "'10' is not of type 'integer'"
    }
    assert validate_result['sample'][0]['index_0'][0] == expected_error


def test_validate_schema_pass(validator_pass_fixture, mock_data_map_pass):
    validate = validator_pass_fixture
    validate_result = validate.validate_schema()
    assert 'index_0' == list(validate_result['sample'][0].keys())[0]
    assert len(validate_result['sample'][0]['index_0'][0]) == 7

    expected_error = {
        'index': 0,
        'validation_result': 'PASS',
        'invalid_key': None,
        'schema_path': None,
        'validator': None,
        'validator_value': None,
        'validation_error': None
    }
    assert validate_result['sample'][0]['index_0'][0] == expected_error


def test_list_entities(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    entities = validate.list_entities()
    expected = ['metabolomics_file', 'medical_history', 'metabolomics_assay', 'sample', 'subject']
    assert entities == expected


def test_list_index_by_entity(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    index_by_entity = validate.list_index_by_entity('sample')
    expected = ['index_0', 'index_1', 'index_2']
    assert index_by_entity == expected


def test_make_keymap(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    key_map = validate.make_keymap()['sample']
    expected = ['index_0', 'index_1', 'index_2']
    assert key_map == expected


def test_pull_entity(validator_fail_fixture, index_0_validator_sample_fail_result):
    validate = validator_fail_fixture
    validate.validate_schema()
    pull = validate.pull_entity('sample')[0]['index_0'][0]
    expected = index_0_validator_sample_fail_result[0]
    assert pull == expected


def test_pull_index_of_entity_success(validator_fail_fixture, index_0_validator_sample_fail_result):
    validate = validator_fail_fixture
    validate.validate_schema()
    pull = validate.pull_index_of_entity('sample', 0)
    assert isinstance(pull, list)
    assert len(pull) > 0
    expected = index_0_validator_sample_fail_result[0]
    assert pull[0] == expected

def test_pull_index_of_entity_invalid_entity(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    # Should return [] and log error if entity does not exist
    result = validate.pull_index_of_entity('not_an_entity', 0)
    assert result == []

def test_pull_index_of_entity_invalid_index_type(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    # Should return [] and log error if index_key is not int
    result = validate.pull_index_of_entity('sample', 'not_an_int')
    assert result == []

def test_pull_index_of_entity_index_out_of_range(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    # Should return [] and log error if index_key is out of range
    result = validate.pull_index_of_entity('sample', 100)
    assert result == []

def test_pull_index_of_entity_data_not_list(monkeypatch, validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    # Patch validation_result to make data not a list
    validate.validation_result['sample'] = {"foo": "bar"}
    result = validate.pull_index_of_entity('sample', 0)
    assert result == []


def test_init_ValidateStats(validator_fail_fixture):
    validate = validator_fail_fixture
    stats = ValidateStats(validate)
    assert stats.validation_result == validate.validation_result


@pytest.fixture
def validate_stats_fail_fixture(validator_fail_fixture):
    validate = validator_fail_fixture
    validate.validate_schema()
    stats = ValidateStats(validate)
    return stats

@pytest.fixture
def validate_stats_pass_fixture(validator_pass_fixture):
    validate = validator_pass_fixture
    validate.validate_schema()
    stats = ValidateStats(validate)
    return stats

def test_n_rows_with_errors(validate_stats_fail_fixture):
    stats = validate_stats_fail_fixture
    result = stats.n_rows_with_errors('sample')
    assert result == 2

def test_n_rows_with_errors_pass(validate_stats_pass_fixture):
    stats = validate_stats_pass_fixture
    result = stats.n_rows_with_errors('sample')
    assert result == 0


def test_count_results_by_index(validate_stats_fail_fixture):
    stats = validate_stats_fail_fixture
    assert stats.count_results_by_index(entity="sample", index_key=0, result_type="ALL") == 3
    assert stats.count_results_by_index(entity="sample", index_key=0, result_type="FAIL") == 3
    assert stats.count_results_by_index(entity="sample", index_key=0, result_type="PASS") == 0
    assert stats.count_results_by_index(entity="sample", index_key=2, result_type="PASS") == 1
    assert stats.count_results_by_index(entity="sample", index_key=2, result_type="FAIL") == 0
    assert stats.count_results_by_index(entity="sample", index_key=2, result_type="ALL") == 1
