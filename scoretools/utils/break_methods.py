import numpy as np
import pandas as pd
from . import utils


def breaks(x, breaks, exceptions=None, **kwargs):
    """
    Break variable at specific values

    Parameters
    ----------
    x: pandas Series
    
    breaks: iterable(values).
        Specify an iterable of scalar values that define
        the bin edges of `x` to break on.
    
    exceptions: iterable.
        Exception values to be held out from `x`.

    Returns
    -------
    x_cut: pandas Series
    """
    if exceptions:
        assert any(
            [i in exceptions for i in breaks]
        ), "breaks present in exceptions"

    x_cut = pd.cut(
        x, bins=breaks, duplicates="drop", include_lowest=True, **kwargs
    )

    try:
        cat_levs = x_cut.cat.categories
    except AttributeError:
        x_cut = pd.Series(x_cut)
        cat_levs = x_cut.cat.categories

    if utils.all_integers(x):
        new_cat_levs = [_make_label(ct_i) for ct_i in cat_levs]
        x_cut.cat.categories = new_cat_levs

    if exceptions is not None:
        exceptions_sort = np.sort(exceptions)
        x_cut = x_cut.cat.add_categories(exceptions_sort)
        for excp in exceptions_sort:
            x_cut[x == excp] = excp

    return x_cut


def bins(x, bins, exceptions=None, **kwargs):
    """
    Break variable into even bins

    Parameters
    ----------
    x: pandas Series
    
    bins: int.
        Specify number of even bins to break `x` into.
    
    exceptions: iterable.
        Exception values to be held out from `x`.

    **kwargs: 
        Additional key-word arguments to pass to the pd.Cut 
        function that is used to bin the data.
        
    Returns
    -------
    x_cut: pandas Series
    """
    pctls = np.linspace(0, 1, bins + 1)
    x_cut = percentile(x, pctls * 100, exceptions=exceptions, **kwargs)
    return x_cut


def percentile(x, percentiles, exceptions=None, **kwargs):
    """
    Break variable by percentile

    Parameter
    ---------
    x: pandas Series
    
    percentiles: iterable(values).
        Specify an iterable of scalar variables which
        are the percentiles to cut the variable at.
        Must be values in the interval [0,100].
    
    exceptions: iterable.
        Exception values to be held out from `x`.

    Returns
    -------
    x_cut: pandas Series

    """
    clean_percentiles = np.concatenate((percentiles, [0, 100]))
    clean_percentiles = np.sort(np.unique(clean_percentiles))
    brks = np.nanpercentile(x, percentiles)
    x_cut = breaks(x, breaks=brks, exceptions=exceptions, **kwargs)
    return x_cut


def _make_label(interval):
    """
    Clean categorical labels if data is integer type.
    """
    int_idx = (interval.left, interval.right)
    left = np.floor(int_idx[0]) + 1
    right = np.floor(int_idx[1])
    # If labels are equal, set to same value
    if left == right:
        new_lab = f"{left:0.0f}"
    else:
        new_lab = f"{left:0.0f}-{right:0.0f}"
    return new_lab
