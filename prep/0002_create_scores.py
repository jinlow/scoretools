import pandas as pd
import numpy as np
import sklearn.linear_model as lm

df = pd.read_csv("data/data_for_scores.csv")

X = df.drop(columns=["Survived2", "Survived"]).to_numpy()
y = df["Survived"].values

# Scale data
mean_x = np.mean(X, axis=0)
sd_x = np.std(X, axis=0)
X = X - mean_x
X = X / sd_x

# First Model
m1 = lm.LogisticRegression(penalty="none")
np.random.seed(123)
dat_mask = np.random.uniform(size=df.shape[0]) < 0.05
m1.fit(X[dat_mask, :], y[dat_mask])

scr1 = m1.predict_log_proba(X)[:, 0]

# Second Score
m2 = lm.LogisticRegression(penalty="l1", solver="liblinear")
m2.fit(X, y)

scr2 = m2.predict_log_proba(X)[:, 0]


# Scale Scores [300 to 900]
def scale_dat(vals, vmin, vmax, digit=0):
    svals = (vals - np.min(vals)) / (np.max(vals) - np.min(vals))
    svals = svals * (vmax - vmin) + vmin
    svals = np.around(svals, decimals=digit)
    if digit == 0:
        svals = svals.astype(int)
    return (svals)


scr1 = scale_dat(scr1, 300, 999)
scr2 = scale_dat(scr2, 300, 999)

import matplotlib.pyplot as plt
import seaborn as sns
sns.kdeplot(scr1, label="Scr1")
sns.kdeplot(scr2, label="Scr2")
plt.legend()
plt.show()

# Write out score data
df["scr1"] = scr1
df["scr2"] = scr2

df.to_csv("data/score_test_dat.csv", index=False)

# Write out raw data with scores
dfr = pd.read_csv("data/train.csv")
dfr = dfr.drop(labels=["Ticket", "Name"], axis=1)
dfr.to_csv("data/score_test_dat_raw.csv", index=False)
