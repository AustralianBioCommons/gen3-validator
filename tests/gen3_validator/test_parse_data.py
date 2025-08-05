import pytest
import pandas as pd
import json
from gen3_validator.parsers.parse_data import ParseData
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_data_folder_path():
    return "/data"

@pytest.fixture
def mock_data_file_path():
    return 'path/to/data/file.json'


@pytest.fixture
def example_json_sample():
    return [
        {
            "alternate_timepoint": None,
            "baseline_timepoint": True,
            "freeze_thaw_cycles": "The samples were freezer thawed not all the same number of times, due to the different volumes that were in the tubes.",
            "volume_or_mass": "150ul",
            "sample_collection_method": "blood draw",
            "sample_id": 101,
            "sample_in_preservation": " frozen",
            "sample_in_storage": "yes",
            "sample_provider": "Baker",
            "sample_source": None,
            "sample_storage_method": "frozen, -80C freezer",
            "sample_type": "plasma",
            'samples': 'sample-example-0000101',
            "storage_location": "Baker",
            "type": "sample",
            "key_fk": "subject-example-990910001",
            "key_pk": "sample-example-0000101",
            "subjects": {
                "submitter_id": "subject-example-990910001"
            },
            "submitter_id": "sample-example-0000101"
        }
    ]

@pytest.fixture
def example_json_subject():
    return [
        {
            "cohort_id": "example",
            "patient_id": 990910001,
            "Essay.id": "AD01_012  #01-004-990910001",
            "type": "subject",
            "key_fk": "project-example-001",
            "key_pk": "subject-example-990910001",
            "projects": {
                "submitter_id": "project-example-001"
            },
            'subjects': 'subject-example-990910001',
            "submitter_id": "subject-example-990910001"
        }
    ]

@pytest.fixture
def dictionary_of_data(example_json_sample, example_json_subject):
    return {
        "sample": example_json_sample,
        "subject": example_json_subject
    }

@pytest.fixture
def mock_json_folder(fs, example_json_sample, example_json_subject):
    fs.create_dir("/data")
    fs.create_file("/data/sample.json", contents=f"{json.dumps(example_json_sample)}")
    fs.create_file("/data/subject.json", contents=f"{json.dumps(example_json_subject)}")
    fs.create_file("/data/notes.txt", contents="This should be skipped")
    return "/data"



def test_init_ParseData(dictionary_of_data, mock_json_folder):
    parse_data = ParseData(data_folder_path=mock_json_folder)
    assert parse_data.data_dict == dictionary_of_data
    assert parse_data.folder_path == '/data'
    assert parse_data.link_suffix == 's'
    assert parse_data.file_path_list == ['/data/sample.json', '/data/subject.json']
    assert set(parse_data.data_nodes) == set(["sample", "subject"])


def test_read_json(mock_json_folder):
    parse_data = ParseData(data_folder_path=mock_json_folder)
    assert parse_data.read_json('/data/sample.json') == parse_data.data_dict['sample']


def test_list_data_files(mock_json_folder):
    parse_data = ParseData(data_folder_path=mock_json_folder)
    assert parse_data.file_path_list == ['/data/sample.json', '/data/subject.json']


def test_load_json_data(dictionary_of_data, mock_json_folder):
    parse_data = ParseData(data_folder_path=mock_json_folder)
    assert parse_data.data_dict == dictionary_of_data


def test_get_node_names(mock_json_folder):
    parse_data = ParseData(data_folder_path=mock_json_folder)
    assert parse_data.data_nodes == ['sample', 'subject']


def test_return_data(dictionary_of_data, mock_json_folder):
    parse_data = ParseData(data_folder_path=mock_json_folder)
    assert parse_data.return_data('sample') == dictionary_of_data['sample']
