import scoretools as sts
import pandas as pd
import pytest


@pytest.fixture
def small_table():
    stbl = pd.DataFrame(
        {"A": ["a", "b"], "B": [1, 2]}, index=["Small", "Large"]
    ).rename_axis("Value")
    return stbl


@pytest.fixture
def small_table_multidx():
    stbl = pd.DataFrame({"A": ["a", "b"], "B": [1, 2]})
    stbl.index = pd.MultiIndex.from_frame(
        pd.DataFrame({"value": ["small", "large"], "other": [4, 3]})
    )
    return stbl


def test_table_w_axis(small_table):
    wb = sts.TableWriter()
    wb.write_table(small_table)
    path = wb._workbook.filename
    wb.close()
    file_read: pd.DataFrame = pd.read_excel(path, engine="openpyxl")
    small_table = small_table.reset_index()
    assert file_read.equals(small_table)
    assert (
        file_read.columns.to_series().eq(small_table.columns.to_series()).all()
    )


def test_table_wo_axis(small_table):
    wb = sts.TableWriter()
    wb.write_table(small_table, index=False)
    path = wb._workbook.filename
    wb.close()
    file_read: pd.DataFrame = pd.read_excel(path, engine="openpyxl")
    small_table = small_table.reset_index(drop=True)
    assert file_read.equals(small_table)
    assert (
        file_read.columns.to_series().eq(small_table.columns.to_series()).all()
    )


def test_table_w_multidx(small_table_multidx):
    wb = sts.TableWriter()
    wb.write_table(small_table_multidx)
    path = wb._workbook.filename
    wb.close()
    file_read: pd.DataFrame = pd.read_excel(path, engine="openpyxl")
    small_table_multidx = small_table_multidx.reset_index()
    assert file_read.equals(small_table_multidx)
    assert (
        file_read.columns.to_series()
        .eq(small_table_multidx.columns.to_series())
        .all()
    )


def test_worksheet_names(small_table):
    wb = sts.TableWriter()
    wb.add_worksheet("newsheet1")
    wb.add_worksheet("newsheet2")
    wb.add_worksheet("newsheet3")
    assert wb.worksheet_names() == ["newsheet1", "newsheet2", "newsheet3"]
