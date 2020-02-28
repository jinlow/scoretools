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
