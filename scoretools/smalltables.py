import pandas as pd


def freq_tab(variable, data=None, fillna="Missing", na_last=False, use_name=True):
    """
    Create a Simple Frequency table

    Parameters
    ----------
    variable: names of variables in data or pandas Series.

    data: pandas Series.
        If variable is a name of a variable, data must be supplied.

    fillna: string or None.
        A string to use to fill missing values in the main_var, if
        None missing values will be ignored in the table. 
        Default is "Missing".
    
    na_last: bool.
        Indicator for if NA values should be placed first or last in the
        table.

    use_name: bool.
        Use the name of the series to name the table.

    Returns
    -------
    freq_tab: pandas DataFrame
    """
    if data is None:
        var_series = variable
        variable = variable.name
    else:
        var_series = data[variable]
    na_last = "last" if na_last else "first"
    dropna = True if fillna is None else False
    freq_tab = (
        var_series.value_counts(dropna=dropna)
        .rename("Frequency")
        .sort_index(na_position=na_last)
        .to_frame()
    )
    freq_tab["Percent"] = freq_tab["Frequency"] / freq_tab["Frequency"].sum()
    freq_tab["Cumulative Frequency"] = freq_tab["Frequency"].cumsum()
    freq_tab["Cumulative Percent"] = freq_tab["Percent"].cumsum()
    freq_tab = freq_tab.rename_axis(variable)
    freq_tab.index = freq_tab.index.fillna(fillna)
    if use_name:
        freq_tab.index = freq_tab.index.rename(variable)
    return freq_tab


def bivar(
    data,
    main_var,
    bivars=None,
    extra_vars=None,
    dropna=False,
    na_last=False,
    break_method="none",
    break_args="none",
    exceptions=None,
):
    """
    Create a bivariate table

    Parameters
    ----------
    data: pandas DataFrame.
        A DataFrame that contains the variable, bivar, and extra_vars field
        if included in the table.

    main_var: string.
        The variable which to distribute the bivar along.
    
    bivars: string or iterable of strings.
        The name of a binary variable, or list of names, to distribute along
        the breaks chosen for the `main_var` argument. Values in the fields
        must be in the set {1, 0}.

    extra_vars: string or iterable of strings.
        The name of a variable, or list of variable names, to distribute along
        the main_var. These `extra_vars` are treated as continous fields.
    
    break_method: string {'none', 'bins', 'percentiles', 'breaks'} or callable.
        Specify the method to use to break the `main_var` argument. This can
        be a string indicating one of the predefined break methods, or a
        callable function supplied by the user where the first argument takes
        a pandas Series and returns pandas Series.
        The following methods are available, .
            * If `none` no bins are used and all levels will be returned.
            * If `bins` the `main_var` will be broken into a specified number
              of even bins.
            * If `percentiles` the `main_var` will be broken into specified
              percentiles.
            * If `breaks` the `main_var` will be broken at the cut points
              specified.
    
    break_args: `break_method` parameters, default None.
        The parameters that will be passed into the `break_method` function.
        If a user defined function needs multiple arguments to be input, pass
        in an unpacked tuple of parameters, i.e. `*params_tuple`.
        The builtin `break_methods` {'none', 'bins', 'percentiles', 'breaks'}
        have the following corresponding arguments.
            * If `none` no paramters are necessary leave as None.
            * If `bins` (int): Specify a single int value to specify the
              desired number of even bins.
            * If `percentiles` (iterable[float]): Specify an iterable of floats
              of the percentiles at which to break the `main_var`. The values
              must be in the range [0,1]
            * If `breaks` (iterable[scalars]): Specify an iterable of scalar values
              that define the bin edges of the `main_var` to break on.

    """
    ...


def single_bivar(
    data: pd.DataFrame, main_var, bivar, fillna="Missing", na_last=False, use_name=True
):
    """
    Single Bivar function
    
    Function to create a bivariate with a single performance field.

    Parameters
    ----------
    data: pandas DataFrame.
        A DataFrame that contains the variable, and bivar.

    main_var: string.
        The variable which to distribute the bivar along.
    
    bivars: string or iterable of strings.
        The name of a binary variable to distribute along
        the breaks chosen for the `main_var` argument. Values in the 
        fields must be in the set {1, 0}.
    
    fillna: string or None.
        A string to use to fill missing values in the main_var, if
        None missing values will be ignored in the table. 
        Default is "Missing".

    na_last: boolean.
        A boolean value that specifies if the missing value should
        be placed first or last in the table.

    use_name: bool.
        Use the name of the series to name the table.

    Returns
    -------

    """
    gdat = data[[main_var, bivar]]
    if fillna is not None:
        gdat = gdat.fillna(value={main_var: fillna})
    else:
        gdat = gdat.dropna(subset=[main_var]).copy()

    r_cnt = gdat[main_var].count()
    b_cnt = gdat[bivar].sum()
    gdat = gdat.groupby(main_var)
    bdat = gdat[main_var].count().rename("N").to_frame()
    bdat[f"Pct N"] = bdat["N"] / r_cnt
    bdat[f"{bivar} sum"] = gdat[bivar].sum()
    bdat[f"{bivar} Rate"] = gdat[bivar].mean()
    bdat[f"{bivar} Pct"] = bdat[f"{bivar} sum"] / b_cnt
    # Adjust and Sort for Missing value
    if fillna is not None:
        bdat = bdat.rename(index={fillna: None})
    # Sort data
    na_last = "last" if na_last else "first"
    bdat = bdat.sort_index(na_position=na_last)
    bdat.index = bdat.index.fillna(fillna)
    tab_tot = bdat.sum().to_frame().T.rename(index={0: "Total"})
    tab_tot[f"{bivar} Rate"] = data[bivar].mean()
    bdat_f = pd.concat([bdat, tab_tot])
    if use_name:
        bdat_f.index = bdat_f.index.rename(main_var)
    return bdat_f
