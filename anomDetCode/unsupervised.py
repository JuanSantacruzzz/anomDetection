import pandas as pd
from pyod.models.cblof import CBLOF
from pyod.models.cof import COF
from pyod.models.hbos import HBOS
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.pca import PCA


def knnAd(df,form):
    # Default parameters
    x1 = 0.1
    x2 = 5
    x3 = 'largest'
    x4 = 'auto'

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('neighbors') is not None:
        x2 = int(form.get('neighbors'))
    if form.get('method') is not None:
        x3 = form.get('method')
    if form.get('algorithm') is not None:
        x4 = form.get('algorithm')

    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'KNN'
    clf = KNN(contamination=x1, n_neighbors=x2, method=x3, algorithm=x4)
    clf.fit(listOfDFRows)

    # get the prediction labels and outlier scores of the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)

    anomDetected = []
    for i in range(len(y_train_pred)):
        if y_train_pred[i] == 1:
            anomDetected.append(listOfDFRows[i])

    dfResult = pd.DataFrame(anomDetected, columns=df.columns)
    return dfResult


def hbosAd(df, form):
    # Default parameters
    x1 = 0.1
    x2 = 10
    x3 = 0.1
    x4 = 0.5

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('bins') is not None:
        x2 = int(form.get('bins'))
    if form.get('alpha') is not None:
        x3 = float(form.get('alpha'))
    if form.get('tol') is not None:
        x4 = float(form.get('tol'))


    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'HBOS'
    clf = HBOS(contamination=x1, n_bins=x2, alpha=x3, tol=x4)
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


def cofAd(df,form):
    # Default parameters
    x1 = 0.1
    x2 = 20
    x3 = 'fast'

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('neighbors') is not None:
        x2 = int(form.get('neighbors'))
    if form.get('method') is not None:
        x3 = form.get('method')


    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'COF'
    clf = COF(contamination=x1, n_neighbors=x2, method=x3)
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


def lofAd(df, form):
    # Default parameters
    x1 = 0.1
    x2 = 20
    x3 = 'auto'
    x4 = 30

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('neighbors') is not None:
        x2 = int(form.get('neighbors'))
    if form.get('algorithm') is not None:
        x3 = form.get('algorithm')
    if form.get('leafSize') is not None:
        x4 = int(form.get('leafSize'))

    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'LOF'
    clf = LOF(contamination=x1, n_neighbors=x2, algorithm=x3, leaf_size=x4)
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


def cblofAd(df,form):
    # Default parameters
    x1 = 0.1
    x2 = 8
    x3 = 0.9
    x4 = 5
    x5 = 'False'

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('clusters') is not None:
        x2 = int(form.get('clusters'))
    if form.get('alpha') is not None:
        x3 = float(form.get('alpha'))
    if form.get('beta') is not None:
        x4 = float(form.get('beta'))
    if form.get('weight') is not None:
        x5 = form.get('weight')

    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'CBLOF'
    clf = CBLOF(contamination=x1, n_clusters=x2, alpha=x3, beta=x4,
                use_weights=x5)
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


def pcaAd(df,form):
    # Default parameters
    x1 = 0.1
    x2 = 'False'
    x3 = 'auto'
    x4 = 'True'

    # Change the parameters if the user wants to do it
    if form.get('contamination') is not None:
        x1 = float(form.get('contamination'))
    if form.get('whiten') is not None:
        x2 = form.get('whiten')
    if form.get('solver') is not None:
        x3 = form.get('solver')
    if form.get('weight') is not None:
        x4 = form.get('weight')


    listOfDFRows = df.to_numpy().tolist()
    clf_name = 'CBLOF'
    clf = PCA(contamination=x1, whiten=x2, svd_solver=x3 ,weighted=x4)
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