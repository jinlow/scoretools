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
    filename: str.
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

    If no filename is provided, a temporary file will be created to write to.
    >>> tab_wb = sts.TableWriter()

    Create a new workbook
    >>> tab_wb = sts.TableWriter("Example_file.xlsx")

    Using a pre-existing workbook object
    >>> wb = xlsxwriter.Workbook(filename="Example_file.xlsx")
    >>> tab_wb = sts.TableWriter(workbook=wb)

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
        self._is_temporary = False
        if workbook is not None:
            assert (
                not workbook.fileclosed
            ), "Workbook supplied must not be closed."
            self._workbook = workbook
        # Create temporary file if no filename is given
        else:
            if filename is None:
                self._is_temporary = True
                tmp_filename = tempfile.NamedTemporaryFile(
                    prefix="TableWriter_Temp_", suffix=".xlsx"
                )
                self._workbook = xlsx.Workbook(
                    filename=tmp_filename.name, **kwargs
                )
            else:
                assert (
                    True if overwrite else not os.path.isfile(filename)
                ), f"{filename} exists in directory, and overwrite = False"
                self._workbook = xlsx.Workbook(filename=filename, **kwargs)

        # Create standard formats for index and data
        fmt_handler = FormatHandler(workbook=self._workbook)
        self.frmt = fmt_handler.header_format()
        self.dfrmt = fmt_handler.data_format()
        self.dfrmt_pct = self._create_pct_fmt(self.dfrmt)

        # Initial rows and column
        self._start_row = 0
        self._start_col = 0
        self.row = self.start_row
        self.col = self.start_col
        self.between = 2
        self.closed = False
        self.old_sheetname = None

    def default_format(
        self,
        header_color="#e5d9fc",
        font="calibri",
        header_fmt=None,
        data_fmt=None,
    ):
        """
        Create default format to be used in tables

        Allows user to specify easily defined format options to be used in 
        the tables, or a custom format created with TableWriter.create_format.

        Parameters
        ----------
        header_color: string.
            Specify the color to use for the background of the index
            and header. This can be a string name of the color, i.e. blue,
            or the color as a hex value, for example "#e5d9fc" for purple.
            Default is set to blue, "#d3daea".

        font: string.
            Specify the font to be used. This is the name of any font
            allowable by excel.
            Default is set to "calibri".

        header_fmt: XlsxWriter Format.
            Alternativly a format can be set directly to use as the default
            format for the header data. If this is set, the above 
            parameters are ignored.
            Default is set to None.

        data_fmt: XlsxWriter Format.
            Alternativly a format can be set directly to use as the default
            format for the table content data. If this is set, the above 
            parameters are ignored.
            Default is set to None.

        """
        fmt_handler = FormatHandler(
            workbook=self._workbook,
            header_color=header_color,
            font=font,
            header_fmt=header_fmt,
            data_fmt=data_fmt,
        )

        self.frmt = fmt_handler.header_format()
        self.dfrmt = fmt_handler.data_format()
        # Set pct format
        self.dfrmt_pct = self._create_pct_fmt(self.dfrmt)

    def create_format(self, properties=None):
        """
        Create format to be used in tables.

        Parameters
        ----------
        properties: dict.
            The format properties to be passed to the XlsxWriter function
            add_format. Reference XlsxWriter add_format() documentation
            for details.

        Returns
        -------
        Reference to the Format object.
        """
        return self._workbook.add_format(properties)

    @property
    def start_row(self):
        """
        Workbook Start Row

        Set the starting row to write to when a new worksheet
        is used.
        """
        return self._start_row

    @start_row.setter
    def start_row(self, value):
        assert (value >= 0) & isinstance(
            value, int
        ), "Start row must be an posotive integer."
        self._start_row = value

    @property
    def start_col(self):
        """
        Workbook Start Column

        Set the starting column to write to when a new worksheet
        is used.
        """
        return self._start_col

    @start_col.setter
    def start_col(self, value):
        assert (value >= 0) & isinstance(
            value, int
        ), "Start row must be an posotive integer."
        self._start_col = value

    @staticmethod
    def _apply_conditional_fmts(tbl, cond_fmt_cols, col, row, worksheet):
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

    @staticmethod
    def _get_percent_cols(tbl, pct_keys):
        """
        Get the indexes of the percent columns
        """
        if pct_keys is None:
            pct_idx = np.array([])
        else:
            pct_bool = pd.Series(tbl.columns).str.contains(pct_keys, case=False)
            pct_idx = np.where(pct_bool)[0]
        return pct_idx

    def _copy_format(self, fmt):
        properties = [f[4:] for f in dir(fmt) if f[0:4] == "set_"]
        dft_fmt = self._workbook.add_format()
        return self._workbook.add_format(
            {
                k: v
                for k, v in fmt.__dict__.items()
                if k in properties and dft_fmt.__dict__[k] != v
            }
        )

    def _create_pct_fmt(self, fmt):
        dfrmt_pct = self._copy_format(fmt)
        dfrmt_pct.set_num_format(10)
        return dfrmt_pct

    def add_worksheet(self, name=None):
        """
        Add a worksheet to the workbook.

        Parameters
        ----------
        name: Str.
            Optional worksheet name, defaults to Sheet1.
        """
        self._workbook.add_worksheet(name)

    # Table Writing
    def write_table(
        self,
        tbl: pd.DataFrame,
        row: Optional[int] = None,
        col: Optional[int] = None,
        sheetname: str = None,
        index: bool = True,
        cond_fmt_cols: Optional[Iterable] = None,
        pct_keys=r"percent|pct|%|rate",
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

        cond_fmt_cols: iterable.
            Column indexes that conditional formating should be applied to.

        pct_keys: regular expression or stirng.
            A regular expression used to search
            the column names to automatically format strings as
            percents. Case is ignored. Set to None to ignore percent
            formatting for all columns.
            Default is set to r"percent|pct|%|rate".

        data_fmt: xlsxwriter.format.
            Format used when writing out the data of the table.
        
        header_fmt: xlsxwriter.format.
            Format used for writing out the header and index.
        """
        worksheet = self._handle_worksheet(sheetname=sheetname)

        row = self.row if row is None else row
        col = self.col if col is None else col

        # Process format
        data_fmt = self.dfrmt if data_fmt is None else data_fmt
        header_fmt = self.frmt if header_fmt is None else header_fmt

        # Add percent version of data format
        if pct_keys is not None and data_fmt is not None:
            data_fmt_pct = self._create_pct_fmt(data_fmt)
        else:
            data_fmt_pct = self.dfrmt_pct

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
            pct_keys=pct_keys,
            data_fmt_pct=data_fmt_pct,
        )

        self.old_sheetname = worksheet.get_name()

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
        pct_keys,
        data_fmt_pct,
    ):
        self.col = col
        if index:
            self._write_index(tbl, worksheet, row, col, header_fmt)
            col += tbl.index.nlevels

        # Handle conditional format column
        if cond_fmt_cols is not None:
            self._apply_conditional_fmts(
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

        # Get percent columns
        pct_idxs = self._get_percent_cols(tbl=tbl, pct_keys=pct_keys)
        # Write out data
        for cs in range(len(tbl.columns)):
            for rs in range(len(tbl.index)):
                if cs in pct_idxs:
                    worksheet.write(
                        rs + row, cs + col, tbl.iat[rs, cs], data_fmt_pct
                    )
                else:
                    worksheet.write(
                        rs + row, cs + col, tbl.iat[rs, cs], data_fmt
                    )

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

        # Reset default rows and column if new worksheet.
        if (self.old_sheetname != worksheet.get_name()) and (
            self.old_sheetname is not None
        ):
            self.row = self.start_row
            self.col = self.start_row

        return worksheet

    # Output workbook
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
        elif sys_platform == "win32":
            open_cmd = self._workbook.filename
            os.startfile(os.path.normpath(open_cmd))
        else:
            warnings.warn("open_file() not supported on this OS.")

    def close(self):
        """
        Close workbook, and output contents.
        """
        self._workbook.close()
        if self._is_temporary:
            atexit.register(os.remove, self._workbook.filename)
        self.closed = True
