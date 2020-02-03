import pandas as pd
import scoretools as sts
import numpy as np

# Read data
df = pd.read_csv("data/score_test_dat_raw.csv")

# gplot example
sts.gplot(df, "Survived", ["scr2", "scr1"])
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"])
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)

# Freq tab
sts.freq_tab("Survived", data=df)

# df.loc[[2, 10, 50], "Survived"] = np.nan

sts.freq_tab("Embarked", data=df, fillna=None)

sts.freq_tab("Embarked", data=df, fillna="Missing")

sts.freq_tab("Embarked", data=df, fillna="", na_last=True)

# Break Methods
sts.utils.break_methods.bins(x=df['Age'], bins=4).value_counts(sort=False,
                                                               dropna=False)

sts.utils.break_methods.breaks(x=df.Age,
                               breaks=[1, 22, 50,
                                       100]).value_counts(sort=False,
                                                          dropna=False)

sts.utils.break_methods.percentile(x=df.Age,
                                   percentiles=[1, 25, 50, 100],
                                   precision=0).value_counts(sort=False)

sts.utils.break_methods.percentile(x=df.Fare,
                                   percentiles=[1, 25, 50,
                                                100]).value_counts(sort=False)

sts.single_bivar(df, "Embarked", "Survived", fillna=None)
sts.single_bivar(df, "Embarked", "Survived", fillna="Missing")
sts.single_bivar(df, "Sex", "Survived", fillna="Missing")
sts.single_bivar(df, "Sex", "Survived", fillna=None)
