import pandas as pd
import numpy as np

df = pd.read_csv("data/train.csv")
df["Cabin"] = df["Cabin"].str.slice(0, 1)
df = df.drop(labels=["PassengerId", "Name", "Ticket"], axis=1)
char_vars = df.select_dtypes("object").columns
df.loc[:, char_vars] = df.loc[:, char_vars].apply(
    lambda x: x.astype("category").cat.codes)
df = df.fillna(value=-1)
df = df.apply(lambda x: x.replace({-1: np.around(x[x.ge(0)].mean())}))

# Create Secondary Performance Field
np.random.seed(123)
r_mask_1 = np.random.uniform(size=df.shape[0]) < 0.05

df["Survived2"] = np.where(r_mask_1 == 1, 1, df["Survived"])

print(df["Survived"].value_counts())
print(df["Survived2"].value_counts())

df.to_csv("data/data_for_scores.csv", index=False)
