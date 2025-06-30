import pytest
import pandas as pd
import json
from gen3_data_validator.parsers.parse_xlsx import ParseXlsxMetadata
from unittest.mock import patch, MagicMock


@pytest.fixture
def xlsx_path():
    return "test.xlsx"

@pytest.fixture
def skip_rows():
    return 0

@pytest.fixture
def ParseXlsx(xlsx_path, skip_rows):
    return ParseXlsxMetadata(xlsx_path, skip_rows=skip_rows)

@pytest.fixture
def ParseXlsx_skip1row(xlsx_path):
    return ParseXlsxMetadata(xlsx_path, skip_rows=1)


def test_init_ParseXlsxMetadata(ParseXlsx, xlsx_path, skip_rows):
    assert ParseXlsx.xlsx_path == xlsx_path
    assert ParseXlsx.skip_rows == skip_rows
    assert ParseXlsx.link_suffix == 's'


def test_parse_metadata_template(ParseXlsx, xlsx_path):
    # mock dfs
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    
    with patch('pandas.read_excel', return_value=fake_pd_dict) as mock_read_excel:
        result = ParseXlsx.parse_metadata_template()
        mock_read_excel.assert_called_once_with(xlsx_path, sheet_name=None)

    assert result == fake_pd_dict

def test_parse_metadata_template_skip_1_row(ParseXlsx_skip1row, xlsx_path):
    # mock dfs
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    
    with patch('pandas.read_excel', return_value=fake_pd_dict) as mock_read_excel:
        result = ParseXlsx_skip1row.parse_metadata_template()
        mock_read_excel.assert_called_once_with(xlsx_path, sheet_name=None)
        # check that the first row of each df was removed
        assert result["sheet1"].iloc[0, 0] == 2
        assert result["sheet2"].iloc[0, 0] == 6

    assert result == fake_pd_dict

def test_get_sheet_names(ParseXlsx):
    # mock dfs
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    expected = ['sheet1', 'sheet2']

    ParseXlsx.xlsx_data_dict = fake_pd_dict
    result = ParseXlsx.get_sheet_names()
    assert set(result) == set(expected)


def test_get_pk_fk_pairs(ParseXlsx):
    df1 = pd.DataFrame({"pk_col": [1, 2], "fk_col": [3, 4]})
    df2 = pd.DataFrame({"pk_col": [5, 6], "fk_col": [1, 2]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    
    result = ParseXlsx.get_pk_fk_pairs(xlsx_data_dict=fake_pd_dict, sheet_name="sheet1")
    assert result == ("pk_col", "fk_col")
