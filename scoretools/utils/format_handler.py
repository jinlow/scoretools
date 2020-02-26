import xlsxwriter as xlsx
import pandas as pd
import numpy as np


class FormatHandler:
    """
    Class for dealing with formats while writing tables to excel

    """

    def __init__(
        self,
        header_color="#e5d9fc",
        pct_keys=r"percent|pct|%|rate",
        cond_fmt_cols=None,
        header_fmt=None,
        data_fmt=None,
    ):
        self.header_color = header_color
        self.pct_keys = pct_keys.lower()
        self.cond_fmt_cols = None
        self.header_fmt = header_fmt
        self.data_fmt = data_fmt

    def apply_conditional_fmt(self, row, col, tbl):
        # Get column index's
        cond_cols = self.cond_fmt_cols + col

        # Get rows indexes
        cond_row_start = row
        cond_row_end = tbl.shape[0] + row

