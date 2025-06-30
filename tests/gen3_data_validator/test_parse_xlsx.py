import pytest
import pandas as pd
import json
from gen3_data_validator.parsers.parse_xlsx import ParseXlsxMetadata
from unittest.mock import patch, MagicMock

def test_init_ParseXlsxMetadata():
    xlsx_path = "test.xlsx"
    link_suffix = "s"
    skip_rows = 0
    parse_xlsx = ParseXlsxMetadata(xlsx_path, link_suffix, skip_rows)
    assert parse_xlsx.xlsx_path == xlsx_path
    assert parse_xlsx.skip_rows == skip_rows
    assert parse_xlsx.link_suffix == link_suffix


def test_parse_metadata_template():
    xlsx_path = "test.xlsx"
    skip_rows = 0
    # mock dfs
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    
    with patch('pandas.read_excel', return_value=fake_pd_dict) as mock_read_excel:
        parse_xlsx = ParseXlsxMetadata(xlsx_path, skip_rows=skip_rows)
        result = parse_xlsx.parse_metadata_template()
        mock_read_excel.assert_called_once_with(xlsx_path, sheet_name=None)

    assert result == fake_pd_dict

def test_parse_metadata_template_skip_1_row():
    xlsx_path = "test.xlsx"
    skip_rows = 1
    # mock dfs
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    
    with patch('pandas.read_excel', return_value=fake_pd_dict) as mock_read_excel:
        parse_xlsx = ParseXlsxMetadata(xlsx_path, skip_rows=skip_rows)
        result = parse_xlsx.parse_metadata_template()
        mock_read_excel.assert_called_once_with(xlsx_path, sheet_name=None)
        
        # check that the first row of each df was removed
        assert result["sheet1"].iloc[0, 0] == 2
        assert result["sheet2"].iloc[0, 0] == 6

    assert result == fake_pd_dict

def test_get_sheet_names():
    xlsx_path = "test.xlsx"
    skip_rows = 0
    # mock dfs
    df1 = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame({"col1": [5, 6], "col2": [7, 8]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    expected = ['sheet1', 'sheet2']
    parse_xlsx = ParseXlsxMetadata(xlsx_path, skip_rows=skip_rows)
    parse_xlsx.xlsx_data_dict = fake_pd_dict
    result = parse_xlsx.get_sheet_names()
    assert set(result) == set(expected)


def test_get_pk_fk_pairs():
    xlsx_path = "test.xlsx"
    skip_rows = 0
    sheet_name = "sheet1"
    df1 = pd.DataFrame({"pk_col": [1, 2], "fk_col": [3, 4]})
    df2 = pd.DataFrame({"pk_col": [5, 6], "fk_col": [1, 2]})
    fake_pd_dict = {"sheet1": df1, "sheet2": df2}
    parse_xlsx = ParseXlsxMetadata(xlsx_path, skip_rows=skip_rows)
    result = parse_xlsx.get_pk_fk_pairs(xlsx_data_dict=fake_pd_dict, sheet_name=sheet_name)
    assert result == ("pk_col", "fk_col")
