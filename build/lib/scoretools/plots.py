import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import itertools


def calc_ks(data, performance, score, ascending):
    scr_dat = data[[score, performance]].sort_values(score,
                                                     ascending=ascending)
    tot_perf = scr_dat[performance].sum()
    cuml_gd = (scr_dat[performance].eq(0).cumsum() /
               scr_dat[performance].eq(0).sum())
    cuml_bd = (scr_dat[performance].eq(1).cumsum() /
               scr_dat[performance].sum())
    return np.max(cuml_bd - cuml_gd)


def _prep_inputs_gplot(data, perf, score, ascending):
    """
    Format score performance and ascending inputs for easy use in gplot function.
        Convert inputs to list of tuples, that can be iterated over.
    """
    if isinstance(perf, str):
        perf = [perf]
    if isinstance(score, str):
        score = [score]
    if isinstance(ascending, bool):
        scr_asc = zip(score, itertools.repeat(ascending))
    else:
        assert len(score) == len(ascending), (
            "ascending must be the same length as score, or of length 1")
        scr_asc = zip(score, itertools.cycle(ascending))
    scr_perf = [(i, *j) for i, j in itertools.product(perf, scr_asc)]
    ks_list = map(lambda x: calc_ks(data, *x), scr_perf)
    ks_order = [
        i for (v, i) in sorted(((v, i) for (i, v) in enumerate(ks_list)),
                               reverse=True)
    ]
    return [scr_perf[i] for i in ks_order]


def _prep_data_gplot(data, dof, exceptions, perf, score, ascending):
    ps = data[[perf, score]]
    if exceptions is not None:
        ps = ps[~ps[score].isin(exceptions)]
    ps = ps.sort_values(score, ascending=ascending)
    ps["pct_file"] = np.arange(1, ps.shape[0] + 1) / ps.shape[0]
    ps["cuml_perf"] = ps[perf].cumsum() / ps[perf].sum()
    if dof is not None:
        assert (dof > 0) & (dof <= 1), "dof of file must be in range (0,1]"
        ps = ps[ps["pct_file"] <= dof]
    return ps


def gplot(data, performance, score, ascending=True, exceptions=None, dof=None):
    """
    Create a Gplot or Cumulative Gains chart
    
    Parameters
    ----------
    data : pandas DataFrame.  
        A dataframe that contains the performance, and score fields
        that will be plotted.

    performance : string or iterable.  
        The names of the performance fields that will be used to create
        the plot. These should be binary variables where 1 is the target
        label.

    score : string or iterable.  
        The names of the score fields that will be used to create
        the plot.

    ascending : bool or list of bool, default True.    
        Sort data by scores in ascending order. Specify list for multiple sort 
        orders. If this is a list of bools, it must match the length of
        score.

    exceptions : iterable, default None.    
        An iterable of exception values that should be excluded from the scores
        when calculating the capture rate.

    dof : float in range (0,1] or None, default None.  
        Specify the maximum depth of file that should be displayed in the plot.
        The value None is the same as specifying a depth of file of 1.

    Returns
    -------
    ax: matplotlib Axes.  
        Returns the Axes object with the plot drawn onto it.

    """
    inpts = _prep_inputs_gplot(data, performance, score, ascending)
    fig, ax = plt.subplots()
    for inpt in inpts:
        pdat = _prep_data_gplot(data, dof, exceptions, *inpt)
        ax.plot("pct_file",
                "cuml_perf",
                data=pdat,
                label=f"{inpt[1]}<>{inpt[0]}")
    ax.plot("pct_file", "pct_file", ":", data=pdat, label='', color='gray')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.xlabel("Cuml % of File")
    plt.ylabel("Cuml % of Bad")
    if dof is not None:
        plt.gca().set_aspect("auto", adjustable='box')
    else:
        plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True, alpha=0.40)
    return ax
