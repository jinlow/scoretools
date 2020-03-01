# Scoretools
This package houses simple, commonly used functions for creating analytic reports.

## Writing Output to Excel  
Excel documents are a common method of delivering results across business verticals. Being able to output tables and results to excel needs to be easy and reproducible. Part of this package is aimed specifically at being able to quickly output pandas DataFrames to excel with flexible formatting options.

The main tool for writing tables is the `TableWriter` class.  
For example...
```python
import scoretools
import pandas as pd

tbl = pd.DataFrame({"A": [1, 2], "B": [4, 3]}, index=["R1", "R2"])

# Initialize table writer object.
wb = scoretools.TableWriter()
wb.write_table(tbl, 1, 1)

# Open excel document
wb.open_file()
```
In addition the package offers flexibility to customize formats, as well 
helper functions for easily making simple tables for analysis.

```python
import seaborn as sns
import scoretools as sts

df = sns.load_dataset("titanic")

pclass_freq = sts.freq_tab(df.pclass)
pclass_bivar = sts.single_bivar(data=df, main_var="deck", bivar="survived")

wb = sts.TableWriter()

# Write tables... If several tables are written to the
# same sheet, no row column indexes are needed, the tables
# will be written one after the other below one another.
wb.write_table(pclass_freq)
wb.write_table(pclass_bivar)

# Change options for the default format
wb.default_format(header_color="#e5d9fc", font="Times New Roman")

# If the row column index is changed for the first table,
# the subsequent tables will be written below from that point.
wb.write_table(pclass_freq, row=1, col=1, sheetname="New Sheet")
wb.write_table(pclass_bivar, sheetname="New Sheet")

# Open workbook
wb.open_file()
```
As you can see, percent and rate columns are automatically detected and 
formatted appropriately. This behavior can be changed by using the `pct_keys=`
parameter in the `write_table()` method.
