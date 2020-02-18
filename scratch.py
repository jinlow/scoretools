import pandas as pd
import scoretools as sts
import numpy as np

# Read data
df = pd.read_csv("data/score_test_dat_raw.csv")
tbl = sts.single_bivar(df, "Embarked", "Survived", fillna="Missing")


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
sts.utils.break_methods.bins(x=df["Age"], bins=4).value_counts(sort=False, dropna=False)

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

# Testing excel output...
tbl = sts.single_bivar(df, "Embarked", "Survived", fillna="Missing")

import xlsxwriter

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook("Expenses01.xlsx")
worksheet = workbook.add_worksheet("tables")

# Make formates
font = "calibri"

# Create format dictionaries
header_fd = {"bold": True, "font_name": font, "border": 1, "bg_color": "#e5d9fc"}

content_fd = {
    "font_name": font,
    "border": 1,
}

# Start from the first cell. Rows and columns are zero indexed.
start_r = 2
start_c = 2

header = workbook.add_format(header_fd)
content = workbook.add_format(content_fd)
# Iterate over the table wrie out content
# Write out header
for cs, col in enumerate(tbl.columns):
    worksheet.write((start_r - 1), (cs + start_c), col, header)

# Write out index
worksheet.write(start_r - 1, start_c - 1, "", header)
for rs, row in enumerate(tbl.index):
    worksheet.write((rs + start_r), (start_c - 1), row, header)

col_widths = [len(cn) if len(cn) > 8 else 8 for cn in tbl.columns]
for cs in range(len(tbl.columns)):
    print(cs)
    # print(cs + start_c)
    for rs in range(len(tbl.index)):
        worksheet.write(cs + start_c, rs + start_r, tbl.iloc[cs, rs], content)
    worksheet.set_column((cs + start_c), (cs + start_c), col_widths[cs])

workbook.close()

open_file(workbook)

import scoretools
import pandas as pd
from importlib import reload

reload(scoretools.excel)
reload(scoretools)


df = pd.read_csv("data/score_test_dat_raw.csv")
tbl = scoretools.single_bivar(df, "Embarked", "Survived", fillna="Missing")
tbl2 = df.groupby(["Pclass", "Survived"])[["Fare", "Age"]].sum()

# wb = scoretools.TableWriter("test2.xlsx")
# twb = xlsxwriter.Workbook("test.xlsx")
wb = scoretools.TableWriter()
wb.write_table(tbl, 1, 1)
wb.write_table(tbl2, 9, 1)
wb.write_table(tbl2, 9, 6)
# Add another worksheet
wb.add_worksheet("AnotherSheet")
wb.write_table(tbl, 1, 1, sheetname="AnotherSheet")

wb.open_file()

# Multi-index table
test = df.groupby(["Survived", "Pclass"]).sum()

wb = scoretools.TableWriter("test.xlsx", overwrite=True)
wb.write_table(test, 1, 1)
wb.open_file()
