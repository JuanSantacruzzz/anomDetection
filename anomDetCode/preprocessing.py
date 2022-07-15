from sklearn.preprocessing import StandardScaler
import pandas as pd


def standarize(df, columns):
    for i in columns:
        df[i] = StandardScaler().fit_transform(df[i].values.reshape(-1,1))
    return df


def dencoding(df, columns):
    for i in columns:
        dataEncoded = pd.get_dummies(data=df[i], drop_first=True)
        df = pd.concat([df, dataEncoded], axis=1)
        df = df.drop(columns=i, axis=1)

    return df