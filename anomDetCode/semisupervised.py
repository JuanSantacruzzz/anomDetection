import numpy as np
import pandas as pd
from pyod.models.iforest import IForest
from pyod.models.ocsvm import OCSVM
from pyod.models.sos import SOS
from pyod.models.xgbod import XGBOD
from xgboost.sklearn import XGBClassifier


def iforestAd(df, form):
    # Default parameters
    x1 = 0.1
    x2 = 'False'
    x4 = 100

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('bootstrap') is not None:
        x2 = form.get('bootstrap')
    if form.get('estimators') is not None:
        x4 = int(form.get('estimators'))

    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'IForest'
    clf = IForest(contamination=x1, bootstrap=x2,n_estimators=x4)
    clf.fit(listOfDFRows)
    # get the prediction labels and outlier scores of the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
    #y_train_scores = clf.decision_scores_  # raw outlier scores, puntuacion de una row para ser anomalia
                                            # cuanto mayor mas probable es
    anomDetected = []
    for i in range(len(y_train_pred)):
        if y_train_pred[i] == 1:
            anomDetected.append(listOfDFRows[i])

    dfResult = pd.DataFrame(anomDetected, columns=df.columns)
    return dfResult


# FALTA METER EL GROUND TRUE EN EL FIT, ELIMINAR O METERLO ELEGIR
def xgbodAd(df, form):
    # Default parameters
    x1 = 3
    x2 = 100
    x3 = 'gbtree'

    # Change the parameters if the user wants to do it
    if form.get('depth') is not None:
        x1 = int(form.get('depth'))
    if form.get('estimators') is not None:
        x2 = int(form.get('estimators'))
    if form.get('booster') is not None:
        x3 = form.get('booster')

    listOfDFRows = df.to_numpy().tolist()

    buckets = []
    for i in range(0, len(listOfDFRows)):
        buckets.append(0)
    clf_name = 'XGBOD'
    clf = XGBOD(max_depth=x1, n_estimators=x2,booster=x3)
    clf.fit_predict_score(listOfDFRows, buckets)
    # get the prediction labels and outlier scores o f the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
    #y_train_scores = clf.decision_scores_  # raw outlier scores, puntuacion de una row para ser anomalia
                                            # cuanto mayor mas probable es
    anomDetected = []
    for i in range(len(y_train_pred)):
        if y_train_pred[i] == 1:
            anomDetected.append(listOfDFRows[i])

    dfResult = pd.DataFrame(anomDetected, columns=df.columns)
    return dfResult


def ocsvmAd(df, form):
    # Default parameters
    x1 = 0.1
    x2 = 'rbf'
    x3 = 0.5
    x4 = 3
    x5 = 0.001
    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('kernel') is not None:
        x2 = form.get('kernel')
    if form.get('nu') is not None:
        x3 = float(form.get('nu'))
    if form.get('degree') is not None:
        x4 = int(form.get('degree'))
    if form.get('tol') is not None:
        x5 = float(form.get('tol'))


    listOfDFRows = df.to_numpy().tolist()

    clf_name = 'OCSVM'
    clf = OCSVM(contamination=x1, kernel=x2, nu=x3, degree=x4, tol=x5)
    clf.fit(listOfDFRows)
    # get the prediction labels and outlier scores of the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
    #y_train_scores = clf.decision_scores_  # raw outlier scores, puntuacion de una row para ser anomalia
                                            # cuanto mayor mas probable es
    anomDetected = []
    for i in range(len(y_train_pred)):
        if y_train_pred[i] == 1:
            anomDetected.append(listOfDFRows[i])

    dfResult = pd.DataFrame(anomDetected, columns=df.columns)
    return dfResult


def sosAd(df,form):
    # Default parameters
    x1 = 0.1
    x2 = 4.5
    x3 = 'euclidean'
    x4 = 0.00005
    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('perplexity') is not None:
        x2 = float(form.get('perplexity'))
    if form.get('metrics') is not None:
        x3 = form.get('metrics')
    if form.get('eps') is not None:
        x4 = float(form.get('eps'))

    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'SOS'
    clf = SOS(contamination=x1, perplexity=x2, metric=x3, eps=x4)
    clf.fit(listOfDFRows)
    # get the prediction labels and outlier scores of the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
    #y_train_scores = clf.decision_scores_  # raw outlier scores, puntuacion de una row para ser anomalia
                                            # cuanto mayor mas probable es
    anomDetected = []
    for i in range(len(y_train_pred)):
        if y_train_pred[i] == 1:
            anomDetected.append(listOfDFRows[i])

    dfResult = pd.DataFrame(anomDetected, columns=df.columns)
    return dfResult




