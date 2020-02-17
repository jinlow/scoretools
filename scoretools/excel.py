import pandas as pd
import xlsxwriter as xlsx
import sys
import os
import shlex
import warnings


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

    **kwargs: other arguments to be passed to xlsxwriter.Workbook.
    """

    def __init__(self, filename: str, overwrite: bool = False, **kwargs):
        if overwrite:
            not_file = True
        else:
            not_file = not os.path.isfile(filename)
        assert not_file, f"{filename} exists in directory, and overwrite = False"

        self.workbook = xlsx.Workbook(filename=filename, **kwargs)
        # Create standard formats for index and data
        self.frmt = self.workbook.add_format(
            {"bold": True, "font_name": "calibri", "border": 1, "bg_color": "#e5d9fc"}
        )
        self.dfrmt = self.workbook.add_format({"font_name": "calibri", "border": 1})
        self.closed = False

    def close(self):
        """
        Close workbook, and output contents.
        """
        self.workbook.close()
        self.closed = True

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
        data_fmt=None,
        header_fmt=None,
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
            column. Default is set to True.

        data_fmt: xlsxwriter Format.
            Format used when writing out the data of the table.
        
        header_fmt: xlsxwriter Format.
            Format used for writing out the header and index.
        """

        # Create Data format

        if sheetname is None:
            try:
                worksheet = self.workbook.worksheets()[0]
            except IndexError:
                worksheet = self.workbook.add_worksheet()
        elif sheetname not in [ws.get_name() for ws in self.workbook.worksheets()]:
            worksheet = self.workbook.add_worksheet(sheetname)
        else:
            worksheet = self.workbook.get_worksheet_by_name(sheetname)
        if index:
            self._write_index(tbl, worksheet, row, col, self.frmt)
            col += 1

        # Write header
        for cs, d_col in enumerate(tbl.columns):
            worksheet.write((row), (cs + col), d_col, self.frmt)

        # Write out data
        for cs in range(len(tbl.columns)):
            for rs in range(len(tbl.index)):
                worksheet.write(rs + row + 1, cs + col, tbl.iloc[cs, rs], self.dfrmt)

    def open_file(self):
        """
        Open the created workbook.

        If the workbook has not been closed it will be closed and 
        written by default. Currently supported for windows or macOS.
        """
        if not self.closed:
            self.close()
            self.closed = True

        sys_plaform = sys.platform.lower()

        if sys_plaform == "darwin":
            open_cmd = "open " + shlex.quote(self.workbook.filename)
            os.system(open_cmd)
        elif sys_plaform == "windows":
            open_cmd = self.workbook.filename
            os.system(open_cmd)
        else:
            warnings.warn("open_file() not supported on this OS.")
