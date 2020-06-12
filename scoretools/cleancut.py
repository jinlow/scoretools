import numpy as np
import pandas as pd
from typing import Union, Iterable, List, Optional


def _proc_cuts(cuts, divisor, threshold=10):
    cuts = np.array(cuts)
    chng = np.mod(cuts, divisor)
    clean_cuts = np.where(
        cuts < threshold,
        cuts,
        np.where(chng < (divisor / 2), cuts - chng, cuts + (divisor - chng)),
    )
    return clean_cuts


def _make_labels(breaks, digits):
    breaks_c1, breaks_c2 = map(np.copy, (breaks, breaks))
    if digits == 0:
        breaks_c1, breaks_c2 = map(lambda x: x.astype(int), (breaks_c1, breaks_c2))
    to_add = list(
        map(lambda x: 1 if (x % 1) == 0 else 1 / (10 ** digits), breaks_c2[1:])
    )
    breaks_c1[1:] = breaks_c1[1:] + to_add
    labs = [
        f"{a_}-{b_}" if a_ != b_ else str(a_)
        for a_, b_ in zip(breaks_c1, breaks_c2[1:])
    ]
    return labs


def cleancut(
    variable,
    bins: Union[Iterable[float], int],
    exceptions: List = None,
    exceptions_last: bool = False,
    missing: Optional[str] = "Missing",
    missing_last: bool = False,
    digits: int = 0,
    clean_cuts: bool = False,
    cuts_divisor: int = 5,
    cuts_threshold: int = 10,
    **kwargs,
):
    """
    A cut function that allows for exceptions and pretty bin values.

    The variable is cut using the provided parameters. The min and max of the field is
    automatically included in cut variable.

    Parameters
    ----------
    variable: Pandas Series to be binned.

    bins: int or Iterable[float]
        If an integer is passed, the variable will be cut into that many even bins, if there are enough
        unique values to do so. If an iterable of floats is passed, those values will be used as unique
        breaks to cut the variable.

    exceptions: List
        Exception values to hold out of the binning of variable.

    exceptions_last: bool
        Should the ordered categorical that is returned have the exception values first or last.

    missing: str or None
        Value to use to fill missing values in the returned field. If None is passed missing values
        are untouched. The default value is "Missing".

    missing_last: bool
        Should the ordered categorical that is returned have the missing fillvalue first or last.

    digits: int
        The number of digits used in the bin labels.

    clean_cuts: bool
        Should the cut variables labels be displayed clean integers?

    cuts_divisor: int
        If the labels are cleaned, this will be the divisor to use to round them to.

    cuts_threshold: int
        The minum value to apply the cuts_divisor to.
    
    """
    if exceptions is not None:
        exceptions = np.unique(np.sort(exceptions))
        variable_le = variable.where(~variable.isin(exceptions), np.nan)
    else:
        variable_le = variable

    if isinstance(bins, int):
        bins = variable_le.quantile(np.linspace(0, 1, bins + 1)).round()

    if clean_cuts:
        bins = _proc_cuts(cuts=bins, divisor=cuts_divisor, threshold=cuts_threshold)

    bins = np.append(bins, [variable_le.min(), variable_le.max()])
    bins = np.round(np.sort(np.unique(bins)), digits)

    labs = _make_labels(bins, digits)

    cut_variable = pd.cut(variable_le, bins, labels=labs, include_lowest=True, **kwargs)

    # Handle Exceptions
    if exceptions is not None:
        cut_variable = cut_variable.cat.add_categories(exceptions)

        for ex in exceptions:
            cut_variable[variable.eq(ex)] = ex
        # Move exceptions to the beggining
        variable_cats = cut_variable.cat.categories

        if exceptions_last:
            cut_variable = cut_variable.cat.reorder_categories(
                variable_cats[-len(exceptions) :].append(
                    variable_cats[: -len(exceptions)]
                )
            )

    if missing is not None:
        cut_variable = cut_variable.cat.add_categories(missing)
        cut_variable[variable.isna()] = missing
        variable_cats = cut_variable.cat.categories
        if missing_last:
            cut_variable = cut_variable.cat.reorder_categories(
                variable_cats[-1:].append(variable_cats[:-1])
            )

    return cut_variable
