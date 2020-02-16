import pandas as pd
import xlsxwriter as xlsx
import os


class TableWriter:
    """
    A Class For Writing Tabular Data to an Excel File

    Parameters
    ----------
    workbook: str.
        Path to write excel file to.

    overwrite: bool.
        If a file exists at filename, should it be overwritten?
        Default is set to False.
    """

    def __init__(self, filename: str, overwrite: bool = False, **kwargs):
        if overwrite:
            not_file = True
        else:
            not_file = not os.path.isfile(filename)
        assert not_file, f"{filename} exists in directory, and overwrite = False"

        self.workbook = xlsx.Workbook(filename=filename, **kwargs)

    def close(self):
        """
        Close workbook, and output contents.
        """
        self.workbook.close()

    def _add_worksheet(self, sheetname: str):
        """
        Add worksheet to workbook.
        """
        self.workbook.worksheet(sheetname)

    def _write_index(self, tbl, worksheet, row, col, frmt=None):
        """
        Write index as first column
        """
        worksheet.write(row, col, "", frmt)
        for rs, d_row in enumerate(tbl.index):
            worksheet.write((rs + row + 1), (col), d_row, frmt)

    def write_table(
        self,
        tbl: pd.DataFrame,
        row: int = 0,
        col: int = 0,
        sheetname: str = None,
        index: bool = True,
    ):
        """
        Write a single pandas DataFrame.

        Parameters
        ----------
        tbl: Pandas DataFrame.
            Table to write to excel sheet.

        row: int.
            The starting row to write the table to. Zero indexed.

        col: int.
            The starting column to write the table to. Zero indexed.
        
        sheetname: str.
            The name of the sheet to write the table to. If the
            worksheet does not exist, it will be created. If no sheet
            name is provided the first worksheet in the workbook will
            be used. If the workbook has no worksheets, a default one
            will be created titled "Tables".
        
        index: bool,
            Indicates if the table index should be written as the first
            row. Default is set to True.
        """
        frmt_f = {
            "bold": True,
            "font_name": "calibri",
            "border": 1,
            "bg_color": "#e5d9fc",
        }

        frmt = self.workbook.add_format(frmt_f)

        # Create Data format
        dfrmt_f = {
            "font_name": "calibri",
            "border": 1,
        }

        dfrmt = self.workbook.add_format(dfrmt_f)
        print("working4")
        if sheetname is None:
            try:
                worksheet = self.workbook.worksheets()[0]
            except IndexError:
                worksheet = self.workbook.add_worksheet()
        elif sheetname not in [ws.get_name() for ws in self.workbook.worksheets()]:
            worksheet = self._add_worksheet(sheetname)
        else:
            worksheet = self.workbook.get_worksheet_by_name(sheetname)

        if index:
            self._write_index(tbl, worksheet, row, col, frmt)
            col += 1

        # Write header
        for cs, d_col in enumerate(tbl.columns):
            worksheet.write((row), (cs + col), d_col, frmt)

        # Write out data
        for cs in range(len(tbl.columns)):
            for rs in range(len(tbl.index)):
                worksheet.write(rs + row + 1, cs + col, tbl.iloc[cs, rs], dfrmt)

