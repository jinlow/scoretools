import pandas as pd


def freq_tab(variable, data=None, na_remove=False, na_last=False):
    """
    Create a Simple Frequency table

    Parameters
    ----------
    variable: names of variables in data or pandas Series.

    data: pandas Series.
        If variable is a name of a variable, data must be supplied.

    na_remove: bool.
        Indicator for if NA values should be included in table if they
        are present in the data.
    
    na_last: bool.
        Indicator for if NA values should be placed first or last in the
        table.
    """
    if data is None:
        var_series = variable
        variable = variable.name
    else:
        var_series = data[variable]
    na_last = "last" if na_last else "first"
    freq_tab = var_series.value_counts(
        dropna=na_remove).rename("Frequency").sort_index(
            na_position=na_last).to_frame()
    freq_tab["Percent"] = freq_tab["Frequency"] / freq_tab["Frequency"].sum()
    freq_tab["Cumulative Frequency"] = freq_tab["Frequency"].cumsum()
    freq_tab["Cumulative Percent"] = freq_tab["Percent"].cumsum()
    freq_tab = freq_tab.rename_axis(variable)
    return freq_tab
