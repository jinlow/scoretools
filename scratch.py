import pandas as pd
import scoretools as sts
import numpy as np

# Read data
df = pd.read_csv("data/score_test_dat.csv")

# gplot example
sts.gplot(df, "Survived", ["scr2", "scr1"])
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"])
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)

# Freq tab
sts.freq_tab("Survived", data=df)

df.loc[[2, 10, 50], "Survived"] = np.nan

sts.freq_tab("Survived", data=df)
