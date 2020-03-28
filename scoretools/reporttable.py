import pandas as pd
import numpy as np
from typing import Iterable, List, Optional, Union, Callable, Any
from .utils import coerce_to_iterable, is_dict_like
from .utils import break_methods as brk


class ReportTable:
    """
    Base Class for Tables

    Houses an interfacing for applying different types 
    of cut functions, and dealing with missing values.

    Parameters
    ----------
    data: pandas DataFrame.
        A DataFrame that contains the index, and columns.

    index: string or list of strings.
        The variables which to use as the index of the table.
    
    columns: string or iterable of strings.
        The name of a binary variable, or list of names, to distribute along
        the breaks chosen for the `main_var` argument.

    extra_vars: string or iterable of strings.
        The name of a variable, or list of variable names, to distribute along
        the main_var. These `extra_vars` are treated as continous fields.
    
    break_method: function, optional
        A function to use to break the index data.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        index: Union[str, List[str]],
        columns: Union[str, List[str]],
        fillna: Optional[str] = "Missing",
        na_last: bool = False,
        break_method: Optional[str] = None,
    ):
        # Process inputs
        self.index = coerce_to_iterable(index)
        self.columns = coerce_to_iterable(columns)
        self.data = data[self.index + self.columns].copy()

        # NA Handling
        self.fillna = fillna
        self.na_last = na_last

    # TODO: Implement functionality for dictionary of break methods
    #       and dictionary of break args
    def _apply_break_method(self):
        if self.break_method is not None:
            self.data[self.index] = self.data[self.index].apply(
                self.break_method
            )
