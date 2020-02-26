import xlsxwriter as xlsx
import pandas as pd
import numpy as np
import re


class FormatHandler:
    """
    Class for dealing with formats while writing tables to excel
    """

    def __init__(
        self,
        workbook: xlsx.Workbook,
        header_color="#e5d9fc",
        font="calibri",
        pct_keys=r"percent|pct|%|rate",
        cond_fmt_cols=None,
        header_fmt=None,
        data_fmt=None,
    ):
        self.workbook = workbook
        self.header_color = header_color
        self.font = font
        self.pct_keys = pct_keys.lower()
        self.cond_fmt_cols = None
        self.header_fmt = header_fmt
        self.data_fmt = data_fmt

    def apply_conditional_fmts(self, tbl, row, col, worksheet):
        """
        Apply conditional formats
        """
        cond_cols = self.cond_fmt_cols + col

        for cond_col in cond_cols:
            # Get rows indexes
            cond_row_start = row
            cond_row_end = tbl.shape[0] + row

            # Write out conditional format
            worksheet.conditional_format(
                cond_row_start,
                cond_col,
                cond_row_end,
                cond_col,
                {"type": "3_color_scale"},
            )

    def header_format(self):
        """
        Create header format
        """
        if self.header_fmt is not None:
            fmt = self.header_fmt
        else:
            fmt = self.workbook.add_format(
                {
                    "bold": True,
                    "font_name": self.font,
                    "border": 1,
                    "bg_color": self.header_color,
                }
            )
        return fmt

    def data_format(self):
        """
        Create format for data
        """
        if self.data_fmt is not None:
            fmt = self.data_fmt
        else:
            fmt = self.workbook.add_format(
                {"font_name": self.font, "border": 1,}
            )
        return fmt

    def get_percent_cols(self, tbl):
        """
        Get the indexes of the percent columns
        """
        pct_bool = pd.Series(tbl.columns).str.contains(self.pct_keys)
        pct_idx = np.where(pct_bool)[0]
        return pct_idx
