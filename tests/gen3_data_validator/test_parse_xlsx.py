import pytest
import pandas as pd
import json
from io import BytesIO
from gen3_data_validator.parsers.parse_xlsx import ParseXlsxMetadata

@pytest.fixture
def mock_xlsx_file():
    # Create a mock Excel file in memory
    excel_data = {
        'Sheet1': pd.DataFrame({
            'pk_uid': [1, 2, 3],
            'fk_uid': ['a', 'b', 'c'],
            'data': [10, 20, 30]
        }),
        'Sheet2': pd.DataFrame({
            'pk_uid': [4, 5, 6],
            'fk_uid': ['d', 'e', 'f'],
            'data': [40, 50, 60]
        })
    }
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for sheet_name, data in excel_data.items():
            data.to_excel(writer, sheet_name=sheet_name, index=False)
    excel_buffer.seek(0)
    return excel_buffer

def test_initialization(mock_xlsx_file):
    # Test the initialization of the class
    parser = ParseXlsxMetadata(mock_xlsx_file)
    assert parser.xlsx_path == mock_xlsx_file
    assert parser.skip_rows == 0
    assert parser.link_suffix == 's'
    assert isinstance(parser.xlsx_data_dict, dict)
    assert 'Sheet1' in parser.xlsx_data_dict
    assert 'Sheet2' in parser.xlsx_data_dict

def test_parse_metadata_template(mock_xlsx_file):
    # Test parsing of the Excel file
    parser = ParseXlsxMetadata(mock_xlsx_file)
    assert 'Sheet1' in parser.xlsx_data_dict
    assert 'Sheet2' in parser.xlsx_data_dict
    assert len(parser.xlsx_data_dict['Sheet1']) == 3  # No rows skipped

def test_get_pk_fk_pairs(mock_xlsx_file):
    # Test extraction of primary and foreign keys
    parser = ParseXlsxMetadata(mock_xlsx_file)
    pk, fk = parser.get_pk_fk_pairs('Sheet1')
    assert pk == 'pk_uid'
    assert fk == 'fk_uid'

def test_pd_to_json(tmp_path, mock_xlsx_file):
    # Test conversion of a sheet to JSON
    parser = ParseXlsxMetadata(mock_xlsx_file)
    json_path = tmp_path / "Sheet1.json"
    parser.pd_to_json('Sheet1', json_path)
    assert json_path.exists()
    with open(json_path, 'r') as f:
        data = json.load(f)
    assert len(data) == 3
    assert data[0]['submitter_id'] == 1
    assert data[0]['key_fk'] == 'a'

def test_write_dict_to_json(tmp_path, mock_xlsx_file):
    # Test writing all sheets to JSON files
    parser = ParseXlsxMetadata(mock_xlsx_file)
    parser.write_dict_to_json(tmp_path)
    assert (tmp_path / "Sheet1.json").exists()
    assert (tmp_path / "Sheet2.json").exists()
