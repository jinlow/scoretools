import pandas as pd
import scoretools as sts
import numpy as np

# Read data
df = pd.read_csv("data/score_test_dat_raw.csv")
tbl = sts.single_bivar(df, "Embarked", "Survived", fillna="Missing")

df_scr = pd.read_csv("data/score_test_dat.csv")

# gplot example
sts.gplot(df_scr, "Survived", ["scr2", "scr1"])
sts.gplot(df_scr, ["Survived", "Survived2"], ["scr2", "scr1"])
sts.gplot(df_scr, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)
sts.gplot(df_scr, ["Survived", "Survived2"], ["scr2", "scr1"], dof=0.2)

# Freq tab
sts.freq_tab("Survived", data=df)

# df.loc[[2, 10, 50], "Survived"] = np.nan

sts.freq_tab("Embarked", data=df, fillna=None)

sts.freq_tab("Embarked", data=df, fillna="Missing")

sts.freq_tab("Embarked", data=df, fillna="", na_last=True)

# Break Methods
sts.utils.break_methods.bins(x=df["Age"], bins=4).value_counts(
    sort=False, dropna=False
)

sts.utils.break_methods.breaks(x=df.Age, breaks=[1, 22, 50, 100]).value_counts(
    sort=False, dropna=False
)

sts.utils.break_methods.percentile(
    x=df.Age, percentiles=[1, 25, 50, 100], precision=0
).value_counts(sort=False)

sts.utils.break_methods.percentile(
    x=df.Fare, percentiles=[1, 25, 50, 100]
).value_counts(sort=False)

sts.single_bivar(df, "Embarked", "Survived", fillna=None)
sts.single_bivar(df, "Embarked", "Survived", fillna="Missing")
sts.single_bivar(df, "Sex", "Survived", fillna="Missing")
sts.single_bivar(df, "Sex", "Survived", fillna=None)

import scoretools
import pandas as pd
from importlib import reload

reload(scoretools.excel)
reload(scoretools)


df = pd.read_csv("data/score_test_dat_raw.csv")
tbl = scoretools.single_bivar(df, "Embarked", "Survived", fillna="Missing")
tbl2 = df.groupby(["Pclass", "Survived"])[["Fare", "Age"]].sum()

# wb = scoretools.TableWriter("test2.xlsx")
# wb = xlsxwriter.Workbook("test.xlsx")
# wb = scoretools.TableWriter(options={"nan_inf_to_errors": True})
wb = scoretools.TableWriter()
wb.write_table(tbl2, 9, 1)
hfmrt = wb.create_format(
    {"bold": True, "font_name": "calibri", "border": 1, "bg_color": "#e5d9fc"}
)
wb.write_table(tbl, 1, 1, header_fmt=hfmrt, pct_keys=None)

# dfrmt = wb.create_format({"font_name": "Times New Roman", "border": 1})
# new_frmt = wb._copy_format(dfrmt)
# new_frmt.set_num_format(10)
wb.write_table(tbl2, 9, 1, cond_fmt_cols=[0])
wb.write_table(tbl, 9, 6, cond_fmt_cols=[0, 4], conditional_type="scale")
wb.write_table(
    tbl, cond_fmt_cols=[0, 4], conditional_type={"type": "3_color_scale"}
)

# Add another worksheet
worksheet = wb.add_worksheet("AnotherSheet")
wb.write_table(tbl, 1, 1, sheetname="AnotherSheet")
wb.write_table(tbl, sheetname="AnotherSheet")
wb.write_table(tbl2, sheetname="AnotherSheet")
wb.write_table(tbl2, sheetname="AnotherSheet", index=False)
wb.write_table(tbl, sheetname="AnotherSheet", cond_fmt_cols=[0, 4])

wb.default_format(header_color="#e5d9fc", font="Times New Roman")

wb.write_table(tbl, sheetname="newSheet")
wb.write_table(tbl2, sheetname="newSheet")
wb.write_table(tbl2, sheetname="newSheet", index=False)
wb.write_table(tbl, sheetname="newSheet", cond_fmt_cols=[0, 4])

wb.write_table(tbl, 2, 2, sheetname="newSheet1")
wb.write_table(tbl, sheetname="newSheet1")

wb.start_col = 1
wb.start_row = 1
wb.write_table(tbl, sheetname="newSheet3")
wb.write_table(tbl, sheetname="newSheet3")


wb.open_file()

# Multi-index table
test = df.groupby(["Survived", "Pclass"]).sum()

wb = scoretools.TableWriter()
wb.write_table(test, 1, 1)
wb.open_file()

wb2 = scoretools.TableWriter()
# wb2.start_col = 1
# wb2.start_row = 1
wb2.write_table(tbl)
wb2.write_table(tbl2)
wb2.write_table(tbl, sheetname="newSheet")
wb2.write_table(tbl2, sheetname="newSheet")
wb2.write_table(tbl2, sheetname="newSheet", index=False)
wb2.write_table(tbl, sheetname="newSheet", cond_fmt_cols=[0, 4])
wb2.open_file()
