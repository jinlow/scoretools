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
        header_color="#d3daea",
        font="calibri",
        header_fmt=None,
        data_fmt=None,
    ):
        self.workbook = workbook
        self.header_color = header_color
        self.font = font
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

    def sub_header_format(self):
        ...

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
