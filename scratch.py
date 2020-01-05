import pandas as pd
import scoretools as sts

# Read data
df = pd.read_csv("data/score_test_dat.csv")

# gplot example
sts.gplot(df, "Survived", ["scr2", "scr1"])
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"])
sts.gplot(df, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)
