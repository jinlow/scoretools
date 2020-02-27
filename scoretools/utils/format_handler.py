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
        header_fmt=None,
        data_fmt=None,
    ):
        self.workbook = workbook
        self.header_color = header_color
        self.font = font
        self.pct_keys = pct_keys.lower()
        self.header_fmt = header_fmt
        self.data_fmt = data_fmt

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
