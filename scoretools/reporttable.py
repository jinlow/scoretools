import pandas as pd
import numpy as np
from typing import Iterable, List, Optional, Union, Callable, Any
from .utils import coerce_to_iterable
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
    
    break_method: string {'bins', 'percentiles', 'breaks'} or callable.
        Specify the method to use to break the `main_var` argument. This can
        be a string indicating one of the predefined break methods, or a
        callable function supplied by the user where the first argument takes
        a pandas Series and returns pandas Series.
        The following methods are available, .
            * If `None` no bins are used and all levels will be returned.
            * If `bins` the `main_var` will be broken into a specified number
              of even bins.
            * If `percentiles` the `main_var` will be broken into specified
              percentiles.
            * If `breaks` the `main_var` will be broken at the cut points
              specified.

    break_args: `break_method` parameters, default None.
        The parameters that will be passed into the `break_method` function.
        This argument is ignored if a user defined function is supplied for
        break_method.
        The builtin `break_methods` {'bins', 'percentiles', 'breaks'}
        have the following corresponding arguments.
            * If `None` no paramters are necessary leave as None.
            * If `bins` (int): Specify a single int value to specify the
              desired number of even bins.
            * If `percentiles` (iterable[float]): Specify an iterable of floats
              of the percentiles at which to break the `main_var`. The values
              must be in the range [0,1]
            * If `breaks` (iterable[scalars]): Specify an iterable of scalar values
              that define the bin edges of the `main_var` to break on.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        index: Union[str, List[str]],
        columns: Union[str, List[str]],
        fillna: Optional[str] = "Missing",
        na_last: bool = False,
        break_method: Optional[str] = None,
        break_args: Optional[Any] = None,
        exceptions: Optional[Iterable] = None,
    ):
        # Process inputs
        self.index = coerce_to_iterable(index)
        self.columns = coerce_to_iterable(columns)
        self.data = data[self.index + self.columns].copy()

        # NA Handling
        self.fillna = fillna
        self.na_last = na_last

        # Break method
        break_dict = {
            "bins": brk.bins,
            "percentiles": brk.percentile,
            "breaks": brk.breaks,
        }

        if not callable(break_method):
            self.break_method = break_dict.get(break_method, None)
            assert (
                break_args is not None
            ), "break_args cannot be None if predefined break_method used."
            self.break_args = break_args
            self.exceptions = exceptions

    # TODO: Implement functionality for dictionary of break methods and dictionary of break args
    def _apply_break_method(self):
        if self.break_method is not None:
            self.data[self.index] = self.data[self.index].apply(
                lambda x: self.break_method(
                    x, self.break_args, exceptions=self.exceptions
                )
            )
