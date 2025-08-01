import pytest
import pandas as pd
import json
from gen3_data_validator.linkage import TestLinkage
from unittest.mock import patch, MagicMock, mock_open
import os


def test_init_TestLinkage():
    Linkage = TestLinkage()
    assert Linkage.root_node == ['subject']


@pytest.fixture
def fixture_data_dict():
    return {
        "sample": [
            {
                'storage_location': 'UMELB',
                'subjects': {'submitter_id': 'subject_e5616257f8'},
                'submitter_id': 'sample_efdbe56d20',
                'type': 'sample',
                'samples': 'sample_efdbe56d20'
            }
        ],
        "subject": [
            {
                'submitter_id': 'subject_e5616257f8',
                'type': 'subject'
            }
        ],
        "genomics_assay": [
            {
                'submitter_id': 'genomics_assay_1',
                'samples': {'submitter_id': 'sample_efdbe56d20'},
                'type': 'genomics_assay'
            }
        ]
    }


def test_generate_config(fixture_data_dict):
    Linkage = TestLinkage()
    config = Linkage.generate_config(fixture_data_dict)
    
    expected_config = {
        "sample": {
            "primary_key": "samples",
            "foreign_key": "subjects"
        },
        "subject": {
            "primary_key": "subjects",
            "foreign_key": None
        },
        "genomics_assay": {
            "primary_key": "genomics_assays",
            "foreign_key": "samples"
        }
    }
    assert config == expected_config