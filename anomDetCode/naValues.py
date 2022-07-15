import pandas as pd
import numpy as np


# change some values to na to be able to find them
def changeNA(df):
    df = df.replace('-', np.nan)
    df = df.replace('?', np.nan)
    df = df.replace(' ', np.nan)
    return df


# get some general information about the data
def naDataGeneralInfo(df):
    ncolumns = df.shape[1]
    nrows = df.shape[0]
    totalNA = df.isna().sum().sum()
    columnsWithNA = []

    for column in df:
        if df[column].isna().sum() > 0:
            columnsWithNA.append(column)

    columnsWithNastr=''
    for i in range(len(columnsWithNA)):
        if i+1 == len(columnsWithNA):
            columnsWithNastr = columnsWithNastr + columnsWithNA[i] + "."
        elif i + 2 == len(columnsWithNA):
            columnsWithNastr = columnsWithNastr + columnsWithNA[i] + " and "
        else:
            columnsWithNastr = columnsWithNastr + columnsWithNA[i]+", "
    lenColwN=len(columnsWithNA)
    result = [totalNA, ncolumns, nrows, columnsWithNastr, lenColwN]
    return result


# information about each column
def naDataColumn(df, columns, nrows):
    result = []
    for column in columns:
        totalNA = df[column].isna().sum()
        i = []
        i.append(totalNA)
        i.append(totalNA/nrows*100)
        result.append(i)
    return result


#change the na values of numeric columns to the value desired (univariate)
def changeNAvaluesNum(df, method, columns):
    for i in columns:
        if method == 'median':
            df[i].fillna(df[i].median(), inplace=True)
        elif method == 'mean':
            df[i].fillna(df[i].mean(), inplace=True)
        elif method == 'mode':
            df[i].fillna(df[i].mode(dropna=True)[0],inplace=True)
        elif method == 'backfill':
            df[i].fillna(method="backfill", inplace=True)
            df[i].fillna(method="ffill", inplace=True)
        elif method == 'ffill':
            df[i].fillna(method="ffill", inplace=True)
            df[i].fillna(method="backfill", inplace=True)
    return df


#change the na values of categorical columns to the value desired (univariate)
def changeNAvaluesCat(df, method, columns):
    for i in columns:
        if method == 'mode':
            df[i].fillna(df[i].mode(dropna=True)[0],inplace=True)
        elif method == 'backfill':
            df[i].fillna(method="backfill", inplace=True)
            df[i].fillna(method="ffill", inplace=True)
        elif method == 'ffill':
            df[i].fillna(method="ffill", inplace=True)
            df[i].fillna(method="backfill", inplace=True)
        else:
            df[i].fillna(str(method), inplace=True)
    return df

