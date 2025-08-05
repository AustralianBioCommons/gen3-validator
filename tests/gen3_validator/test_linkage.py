import pytest
from gen3_validator.linkage import Linkage

@pytest.fixture
def fixture_root_node():
    return ['subject']

def test_init_Linkage(fixture_root_node):
    LinkageInstance = Linkage()
    assert LinkageInstance.root_node == fixture_root_node
    assert LinkageInstance.link_validation_results is None

@pytest.fixture
def fixture_Linkage(fixture_root_node):
    return Linkage(root_node=fixture_root_node)

@pytest.fixture
def fixture_data_dict_pass():
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
                'type': 'subject',
                'subjects': 'subject_e5616257f8'
            }
        ],
        "genomics_assay": [
            {
                'submitter_id': 'genomics_assay_1',
                'samples': {'submitter_id': 'sample_efdbe56d20'},
                'type': 'genomics_assay',
                'genomics_assays': 'genomics_assay_1'
            }
        ]
    }

@pytest.fixture
def fixture_data_dict_fail():
    return {
        "sample": [
            {
                'storage_location': 'UMELB',
                'subjects': {'submitter_id': 'subject_e5616257f1'},  # subject_e5616257f1 is not in subject
                'submitter_id': 'sample_efdbe56d20',
                'type': 'sample',
                'samples': 'sample_efdbe56d20'
            }
        ],
        "subject": [
            {
                'submitter_id': 'subject_e5616257f8',
                'type': 'subject',
                'subjects': 'subject_e5616257f8'
            }
        ],
        "genomics_assay": [
            {
                'submitter_id': 'genomics_assay_1',
                'samples': {'submitter_id': 'sample_efdbe56d21'},  # sample_efdbe56d21 is not in sample
                'type': 'genomics_assay',
                'genomics_assays': 'genomics_assay_1'
            }
        ]
    }

@pytest.fixture
def fixture_link_config():
    return {
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

def test_generate_config(fixture_data_dict_pass, fixture_link_config):
    LinkageInstance = Linkage()
    config = LinkageInstance.generate_config(fixture_data_dict_pass)
    expected_config = fixture_link_config
    assert config == expected_config

def test_validate_links_fail(fixture_data_dict_fail, fixture_link_config, fixture_Linkage):
    Linkage = fixture_Linkage
    result = Linkage.validate_links(fixture_data_dict_fail, fixture_link_config)
    expected = {
        "sample": ["subject_e5616257f1"],
        "genomics_assay": ["sample_efdbe56d21"],
        "subject": []
    }
    assert result == expected

def test_validate_links_pass(fixture_data_dict_pass, fixture_link_config, fixture_Linkage):
    Linkage = fixture_Linkage
    result = Linkage.validate_links(fixture_data_dict_pass, fixture_link_config)
    expected = {
        "sample": [],
        "genomics_assay": [],
        "subject": []
    }
    assert result == expected


@pytest.fixture
def fixture_find_fk_cases():
    return [
        (
            # Case: dict with a foreign key
            {"id": "sample_1", "subjects": {"submitter_id": "subject_1"}, "foo": 123},
            "subjects"
        ),
        (
            # Case: dict with no foreign key
            {"id": "subject_1", "name": "John Doe"},
            None
        ),
        (
            # Case: dict with multiple keys, only one is a dict with submitter_id
            {"id": "genomics_assay_1", "samples": {"submitter_id": "sample_1"}, "other": {"not_submitter_id": "foo"}},
            "samples"
        ),
    ]

def test_find_fk(fixture_Linkage, fixture_find_fk_cases):
    linkage = fixture_Linkage
    for data, expected in fixture_find_fk_cases:
        assert linkage._find_fk(data) == expected

@pytest.fixture
def fixture_data_map_no_fk():
    return {
        "subject": [
            {"subjects": "subject_1", "name": "Alice"}
        ],
        "sample": [
            {"samples": "sample_1", "bar": 123}
        ]
    }

def test_generate_config_handles_no_fk(fixture_Linkage, fixture_data_map_no_fk):
    linkage = fixture_Linkage
    config = linkage.generate_config(fixture_data_map_no_fk)
    assert config["subject"]["foreign_key"] is None
    assert config["sample"]["foreign_key"] is None
    assert config["subject"]["primary_key"] == "subjects"
    assert config["sample"]["primary_key"] == "samples"


@pytest.fixture
def fixture_config_valid():
    return {
        "subject": {"primary_key": "subjects", "foreign_key": None},
        "sample": {"primary_key": "samples", "foreign_key": "subjects"},
        "genomics_assay": {"primary_key": "genomics_assays", "foreign_key": "samples"},
    }

@pytest.fixture
def fixture_config_invalid():
    return {
        "subject": {"primary_key": "subjects", "foreign_key": None},
        "sample": {"primary_key": "samples", "foreign_key": "not_a_real_pk"},
        "genomics_assay": {"primary_key": "genomics_assays", "foreign_key": "samples"},
    }

@pytest.fixture
def fixture_config_root_broken():
    return {
        "subject": {"primary_key": "subjects", "foreign_key": "not_a_real_pk"},
        "sample": {"primary_key": "samples", "foreign_key": "subjects"},
    }

def test_test_config_links_valid(fixture_Linkage, fixture_config_valid):
    linkage = fixture_Linkage
    result = linkage.test_config_links(fixture_config_valid, root_node=["subject"])
    assert result == "valid"

def test_test_config_links_invalid(fixture_Linkage, fixture_config_invalid):
    linkage = fixture_Linkage
    # Should not raise, but should return a dict with the broken link
    result = linkage.test_config_links(fixture_config_invalid, root_node=["subject"])
    assert isinstance(result, dict)
    assert "sample" in result
    assert result["sample"] == "not_a_real_pk"

def test_test_config_links_root_node_broken_link_ignored(fixture_Linkage, fixture_config_root_broken):
    linkage = fixture_Linkage
    result = linkage.test_config_links(fixture_config_root_broken, root_node=["subject"])
    assert result == "valid"



def test_test_config_links_missing_foreign_key_raises(fixture_Linkage):
    linkage = fixture_Linkage
    config = {
        "subject": {"primary_key": "subjects"},  # missing 'foreign_key'
        "sample": {"primary_key": "samples", "foreign_key": "subjects"},
    }
    with pytest.raises(KeyError):
        linkage.test_config_links(config, root_node=["subject"])

def test_test_config_links_missing_primary_key_raises(fixture_Linkage):
    linkage = fixture_Linkage
    config = {
        "subject": {"foreign_key": None},  # missing 'primary_key'
        "sample": {"primary_key": "samples", "foreign_key": "subjects"},
    }
    with pytest.raises(KeyError):
        linkage.test_config_links(config, root_node=["subject"])

def test_test_config_links_non_dict_config_raises(fixture_Linkage):
    linkage = fixture_Linkage
    config = [
        {"primary_key": "subjects", "foreign_key": None},
        {"primary_key": "samples", "foreign_key": "subjects"},
    ]
    with pytest.raises(TypeError):
        linkage.test_config_links(config, root_node=["subject"])

def test_test_config_links_non_dict_value_raises(fixture_Linkage):
    linkage = fixture_Linkage
    config = {
        "subject": ["subjects", None],  # not a dict
        "sample": {"primary_key": "samples", "foreign_key": "subjects"},
    }
    with pytest.raises(TypeError):
        linkage.test_config_links(config, root_node=["subject"])


@pytest.fixture
def fixture_data_map_for_keys():
    return {
        "subject": [
            {"subjects": "subject_1", "name": "Alice"},
            {"subjects": {"submitter_id": "subject_2"}, "name": "Bob"},
            {"name": "NoPK"},  # missing primary key field
            {"subjects": None, "name": "NullPK"},  # primary key is None
        ],
        "sample": [
            {"samples": "sample_1", "subjects": {"submitter_id": "subject_1"}},
            {"samples": {"submitter_id": "sample_2"}, "subjects": "subject_2"},
            {"samples": None, "subjects": "subject_3"},  # primary key is None
            {"subjects": "subject_4"},  # missing primary key field
        ],
        "genomics_assay": [
            {"genomics_assays": "ga_1", "samples": {"submitter_id": "sample_1"}},
            {"genomics_assays": {"submitter_id": "ga_2"}, "samples": "sample_2"},
            {"samples": "sample_3"},  # missing primary key field
            {"genomics_assays": None, "samples": "sample_4"},  # primary key is None
        ]
    }

@pytest.fixture
def fixture_config_for_keys():
    return {
        "subject": {"primary_key": "subjects", "foreign_key": None},
        "sample": {"primary_key": "samples", "foreign_key": "subjects"},
        "genomics_assay": {"primary_key": "genomics_assays", "foreign_key": "samples"},
    }

def test_get_primary_keys(fixture_Linkage, fixture_data_map_for_keys, fixture_config_for_keys):
    linkage = fixture_Linkage
    pk_result = linkage.get_primary_keys(fixture_data_map_for_keys, fixture_config_for_keys)
    assert pk_result["subject"] == ["subject_1", "subject_2"]
    assert pk_result["sample"] == ["sample_1", "sample_2"]
    assert pk_result["genomics_assay"] == ["ga_1", "ga_2"]

def test_get_primary_keys_missing_entity(fixture_Linkage, fixture_data_map_for_keys, fixture_config_for_keys):
    linkage = fixture_Linkage
    config = dict(fixture_config_for_keys)
    config["not_in_data"] = {"primary_key": "foo", "foreign_key": None}
    with pytest.raises(KeyError):
        linkage.get_primary_keys(fixture_data_map_for_keys, config)

def test_get_primary_keys_none_pk_field(fixture_Linkage, fixture_data_map_for_keys, fixture_config_for_keys):
    linkage = fixture_Linkage
    config = dict(fixture_config_for_keys)
    config["subject"]["primary_key"] = None
    pk_result = linkage.get_primary_keys(fixture_data_map_for_keys, config)
    assert pk_result["subject"] == []

def test_get_foreign_keys(fixture_Linkage, fixture_data_map_for_keys, fixture_config_for_keys):
    linkage = fixture_Linkage
    fk_result = linkage.get_foreign_keys(fixture_data_map_for_keys, fixture_config_for_keys)
    # subject has no foreign key
    assert fk_result["subject"] == []
    # sample foreign key is "subjects"
    assert fk_result["sample"] == ["subject_1", "subject_2", "subject_3", "subject_4"]
    # genomics_assay foreign key is "samples"
    assert fk_result["genomics_assay"] == ["sample_1", "sample_2", "sample_3", "sample_4"]

def test_get_foreign_keys_missing_entity(fixture_Linkage, fixture_data_map_for_keys, fixture_config_for_keys):
    linkage = fixture_Linkage
    config = dict(fixture_config_for_keys)
    config["not_in_data"] = {"primary_key": "foo", "foreign_key": "bar"}
    with pytest.raises(KeyError):
        linkage.get_foreign_keys(fixture_data_map_for_keys, config)

def test_get_foreign_keys_none_fk_field(fixture_Linkage, fixture_data_map_for_keys, fixture_config_for_keys):
    linkage = fixture_Linkage
    config = dict(fixture_config_for_keys)
    config["sample"]["foreign_key"] = None
    fk_result = linkage.get_foreign_keys(fixture_data_map_for_keys, config)
    assert fk_result["sample"] == []

def test_get_primary_keys_and_foreign_keys_empty_data(fixture_Linkage, fixture_config_for_keys):
    linkage = fixture_Linkage
    empty_data = {
        "subject": [],
        "sample": [],
        "genomics_assay": [],
    }
    pk_result = linkage.get_primary_keys(empty_data, fixture_config_for_keys)
    fk_result = linkage.get_foreign_keys(empty_data, fixture_config_for_keys)
    assert pk_result == {"subject": [], "sample": [], "genomics_assay": []}
    assert fk_result == {"subject": [], "sample": [], "genomics_assay": []}

def test_get_primary_keys_and_foreign_keys_missing_key_in_record(fixture_Linkage, fixture_config_for_keys):
    linkage = fixture_Linkage
    data_map = {
        "subject": [{"name": "NoPK"}],  # missing "subjects"
        "sample": [{"bar": 123}],       # missing "samples"
        "genomics_assay": [{"foo": "bar"}],  # missing "genomics_assays"
    }
    pk_result = linkage.get_primary_keys(data_map, fixture_config_for_keys)
    fk_result = linkage.get_foreign_keys(data_map, fixture_config_for_keys)
    assert pk_result == {"subject": [], "sample": [], "genomics_assay": []}
    assert fk_result == {"subject": [], "sample": [], "genomics_assay": []}


