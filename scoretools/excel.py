import pandas as pd
import xlsxwriter as xlsx
import sys
import os
import shlex
import warnings
import tempfile
import atexit
import numpy as np
from typing import Optional, Iterable
from .utils import FormatHandler


class TableWriter:
    """
    A Class For Writing Tabular Data to an Excel File

    Parameters
    ----------
    workbook: str.
        Path to write excel file to.
        Default is set to None, in which case a temporary file is created 
        to write to.

    overwrite: bool.
        If a file exists at filename, should it be overwritten?
        Default is set to False.

    workbook: xlsxwriter.WorkBook.
        Alternativly to creating a workbook object, the table writer
        class could be initialized with a pre-existing xlsxwriter 
        workbook object.

    **kwargs: other arguments to be passed to xlsxwriter.Workbook.

    Examples
    --------
    Create a new workbook
    >>> tab_wb = TableWriter("Example_file.xlsx")

    Using a pre-existing workbook object
    >>> wb = xlsxwriter.Workbook(filename="Example_file.xlsx")
    >>> tab_wb = TableWriter(workbook=wb)

    Write out a pandas dataframe
    >>> import pandas as pd
    >>> df = pd.DataFrame({"A": [1, 2, 3], "B": [1, 2, 3]})
    >>> tab_wb.write_table(df, 1, 1)

    Open excel document
    >>> tab_wb.open_file()
    """

    def __init__(
        self,
        filename: Optional[str] = None,
        overwrite: bool = False,
        workbook: Optional[xlsx.Workbook] = None,
        **kwargs,
    ):
        if workbook is not None:
            assert (
                not workbook.fileclosed
            ), "Workbook supplied must not be closed."
            self._workbook = workbook
        # Create temporary file if no filename is given
        else:
            if filename is None:
                tmp_filename = tempfile.NamedTemporaryFile(
                    prefix="TableWriter_Temp_", suffix=".xlsx"
                )
                self._workbook = xlsx.Workbook(
                    filename=tmp_filename.name, **kwargs
                )
            else:
                if overwrite:
                    not_file = True
                else:
                    not_file = not os.path.isfile(filename)
                assert (
                    not_file
                ), f"{filename} exists in directory, and overwrite = False"
                self._workbook = xlsx.Workbook(filename=filename, **kwargs)

        # Create standard formats for index and data
        self.frmt = self._workbook.add_format(
            {
                "bold": True,
                "font_name": "calibri",
                "border": 1,
                "bg_color": "#d3daea",
            }
        )
        self.dfrmt = self._workbook.add_format(
            {"font_name": "calibri", "border": 1}
        )
        self.row = 0
        self.col = 0
        self.between = 2
        self.closed = False
        self.old_sheetname = None

    def create_format(self, properties=None):
        """
        Create format to be used in tables.

        Parameters
        ----------
        properties: dict.
            The format properties.

        Returns
        -------
        Reference to the Format object.
        """
        return self._workbook.add_format(properties)

    def add_worksheet(self, name=None):
        """
        Add a worksheet to the workbook.

        Parameters
        ----------
        name: Str.
            Optional worksheet name, defaults to Sheet1.
        """
        self._workbook.add_worksheet(name)

    def close(self):
        """
        Close workbook, and output contents.
        """
        self._workbook.close()
        atexit.register(os.remove, self._workbook.filename)
        self.closed = True

    def _write_index(self, tbl, worksheet, row, col, frmt=None):
        """
        Write index as first column, if multi-index, write out
        each index.
        """
        if tbl.index.nlevels > 1:
            for i, nm in enumerate(tbl.index.names):
                worksheet.write(row, (col + i), nm, frmt)
            for rs, d_row in enumerate(tbl.index):
                for i, idx in enumerate(d_row):
                    worksheet.write((rs + row + 1), (col + i), idx, frmt)
        else:
            worksheet.write(row, col, tbl.index.name, frmt)
            for rs, d_row in enumerate(tbl.index):
                worksheet.write((rs + row + 1), (col), d_row, frmt)

    def write_table(
        self,
        tbl: pd.DataFrame,
        row: Optional[int] = None,
        col: Optional[int] = None,
        sheetname: str = None,
        index: bool = True,
        cond_fmt_cols: Optional[Iterable] = None,
        data_fmt: xlsx.format = None,
        header_fmt: xlsx.format = None,
    ):
        """
        Write a single pandas DataFrame.

        Parameters
        ----------
        tbl: Pandas DataFrame.
            Table to write to excel sheet.

        row: int.
            The starting row to write the table to. Zero indexed. Default
            is zero. When one table is written, the default will change
            to one cell below the written table

        col: int.
            The starting column to write the table to. Zero indexed. Default
            is zero.
        
        sheetname: str.
            The name of the sheet to write the table to. If the
            worksheet does not exist, it will be created. If no sheet
            name is provided the first worksheet in the workbook will
            be used. If the workbook has no worksheets, a default one
            will be created titled "Tables".
        
        index: bool,
            Indicates if the table index should be written as the first
            column. Default is set to True.

        data_fmt: xlsxwriter.format.
            Format used when writing out the data of the table.
        
        header_fmt: xlsxwriter.format.
            Format used for writing out the header and index.
        """

        worksheet = self._handle_worksheet(sheetname=sheetname)

        if (self.old_sheetname != worksheet.get_name()) and (
            self.old_sheetname is not None
        ):
            self.row = 0
            self.col = 0

        row = self.row if row is None else row
        col = self.col if col is None else col

        # Process format
        data_fmt = self.dfrmt if data_fmt is None else data_fmt
        header_fmt = self.frmt if header_fmt is None else header_fmt

        # Write data
        self._write_data(
            tbl=tbl,
            row=row,
            col=col,
            index=index,
            worksheet=worksheet,
            header_fmt=header_fmt,
            data_fmt=data_fmt,
            cond_fmt_cols=cond_fmt_cols,
        )

        self.old_sheetname = worksheet.get_name()

    def _write_data(
        self,
        tbl,
        row,
        col,
        index,
        worksheet,
        header_fmt,
        data_fmt,
        cond_fmt_cols,
    ):
        self.col = col
        if index:
            self._write_index(tbl, worksheet, row, col, header_fmt)
            col += tbl.index.nlevels

        # Handle conditional format column
        if cond_fmt_cols is not None:
            self.apply_conditional_fmts(
                tbl=tbl,
                cond_fmt_cols=cond_fmt_cols,
                col=col,
                row=row,
                worksheet=worksheet,
            )

        # Write header
        for cs, d_col in enumerate(tbl.columns):
            worksheet.write(row, (cs + col), d_col, header_fmt)
        # Increment row number
        row += 1

        # Write out data
        for cs in range(len(tbl.columns)):
            for rs in range(len(tbl.index)):
                worksheet.write(rs + row, cs + col, tbl.iat[rs, cs], data_fmt)

        row += tbl.shape[0]
        self.row = row + self.between

    def _handle_worksheet(self, sheetname):
        """
        Handle creation or selection of worksheet.
        """
        if sheetname is None:
            try:
                worksheet = self._workbook.worksheets()[0]
            except IndexError:
                worksheet = self._workbook.add_worksheet()
        elif sheetname not in [
            ws.get_name() for ws in self._workbook.worksheets()
        ]:
            worksheet = self._workbook.add_worksheet(sheetname)
        else:
            worksheet = self._workbook.get_worksheet_by_name(sheetname)
        return worksheet

    def open_file(self):
        """
        Open the created workbook.

        If the workbook has not been closed it will be closed and 
        written by default. Currently supported for windows or macOS.
        """
        if not self.closed:
            self.close()
            self.closed = True

        sys_platform = sys.platform.lower()

        if sys_platform == "darwin":
            open_cmd = "open " + shlex.quote(self._workbook.filename)
            os.system(open_cmd)
        elif sys_platform == "windows":
            open_cmd = self._workbook.filename
            os.system(open_cmd)
        else:
            warnings.warn("open_file() not supported on this OS.")

    @staticmethod
    def apply_conditional_fmts(tbl, cond_fmt_cols, col, row, worksheet):
        """
        Apply conditional formats
        """
        cond_cols = np.array(cond_fmt_cols) + col
        cond_row_start = row
        cond_row_end = tbl.shape[0] + row
        for cond_col in cond_cols:
            worksheet.conditional_format(
                cond_row_start,
                cond_col,
                cond_row_end,
                cond_col,
                {"type": "3_color_scale"},
            )
