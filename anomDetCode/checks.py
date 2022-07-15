import types

from flask import request, jsonify
import pandas as pd

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def checkNumericColumns(df, columns):
    resp = ''
    if 'columnsNum' not in columns:
        resp = jsonify({'message': 'No columns part in the request'})
        resp.status_code = 405
        return resp
    elif columns.get('columnsNum') == '':
        resp = jsonify({'message': 'The columns field can not be empty'})
        resp.status_code = 406
        return resp
    else:
        columns = columns.get('columnsNum').split(',')
        print(columns)
        for i in columns:
            if i not in df.columns:
                print('HOLA')
                resp = jsonify({'message': 'The column is not defined in the data'})
                print(resp)
                resp.status_code = 409
                return resp
            elif not df[i].dtype == 'int64' and not df[i].dtype == 'float64':
                resp = jsonify({'message': 'The column ' + i + ' is not numerical.'})
                resp.status_code = 408
                return resp
    return resp


def checkCatColumns(df, columns):
    resp = ''
    if 'columnsCat' not in columns:
        resp = jsonify({'message': 'No columns part in the request'})
        resp.status_code = 405
        return resp
    elif columns.get('columnsCat') == '':
        resp = jsonify({'message': 'The columns field can not be empty'})
        resp.status_code = 406
        return resp
    else:
        columns = columns.get('columnsCat').split(',')
        for i in columns:
            if i not in df.columns:
                resp = jsonify({'message': 'The column ' + i + ' is not defined in the data.'})
                resp.status_code = 407
                return resp
            elif not df[i].dtype == 'bool' and not df[i].dtype == 'object':
                resp = jsonify({'message': 'The column ' + i + ' is not categorical.'})
                resp.status_code = 408
                return resp
    return resp


# Checks if there if a file in the request
def checkFile(file):
    file = request.files
    # file checks
    if 'file' not in file:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 401
        return resp
    if file['file'].filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 402
        return resp
    if not allowed_file(file['file'].filename):
        resp = jsonify({'message': 'The file is not a csv'})
        resp.status_code = 403
        return resp
    try:
        df = pd.read_csv(file['file'])
    except:
        resp = jsonify({'message': 'The file is empty or impossible to read'})
        resp.status_code = 404
        return resp
    else:
        df.drop(columns=df.columns[0], axis=1, inplace=True)
        return df


def checkNumMethods(form):
    listM = ['median', 'mean', 'mode', 'backfill', 'ffill']
    if 'methodNum' not in form:
        resp = jsonify({'message': 'No method in the request'})
        resp.status_code = 409
        return resp
    elif form.get('methodNum') == '':
        resp = jsonify({'message': 'The method field can not be empty'})
        resp.status_code = 410
        return resp
    elif isinstance(form.get('methodNum'), str):
        if form.get('methodNum') in listM:
            return ''
        else:
            resp = jsonify({'message':''+form.get('methodNum')+' is not an available method'})
            resp.status_code = 411
            return resp
    else:
        resp = jsonify({'message': 'The method has to be a string'})
        resp.status_code = 412
        return resp


def checkNum(df, form):
    x = checkNumericColumns(df, form)
    if x == '':
        if checkNumMethods(form) == '':
            return ''
        else:
            return checkNumMethods(form)
    else:
        return x


def checkCatMethods(form):
    listM = ['mode', 'backfill', 'ffill']
    if 'methodCat' not in form:
        resp = jsonify({'message': 'No method in the request'})
        resp.status_code = 409
        return resp
    elif form.get('methodCat') == '':
        resp = jsonify({'message': 'The method field can not be empty'})
        resp.status_code = 410
        return resp
    elif isinstance(form.get('methodCat'), str):
            return ''
    else:
        resp = jsonify({'message': 'The word to replace NA values has to be a string'})
        resp.status_code = 411
        return resp


def checkCat(df, form):
    x = checkCatColumns(df, form)
    if x == '':
        if checkCatMethods(form) == '':
            return ''
        else:
            return checkCatMethods(form)
    else:
        return x


def checkMix(df, form):
    x = checkCatColumns(df, form)
    y = checkNumericColumns(df, form)
    if x == '' and y == '':
        if checkCatMethods(form) == '' and checkNumMethods(form) == '':
            return ''
        elif checkCatMethods(form) == '' and not checkNumMethods(form) == '':
            return checkNumMethods(form)
        elif not checkCatMethods(form) == '' and checkNumMethods(form) == '':
            return checkCatMethods(form)
        else:
            return checkNumMethods(form)
    elif not x == '' and y == '':
        return x
    elif x == '' and not y == '':
        return y
    else:
        return x


# Checks for anomaly detection methods

# Generic checks


def checkContamination(form):
    if form.get('contamination') is not None:
        try:
            if float(form.get('contamination')):

                if (float(form.get('contamination')) > 0.0) and (float(form.get('contamination')) <= 0.5):
                    return ''
                else:
                    resp = jsonify({'message': 'Contamination has to be between 0.0 and 0.5'})
                    resp.status_code = 405
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Contamination has to be float type'})
            resp.status_code = 405
            return resp
    else:
        return ''


def checkNeighbors(form):
    if form.get('neighbors') is not None:
        try:
            if int(form.get('neighbors')):
                if int(form.get('neighbors')) > 0:
                    return ''
                else:
                    resp = jsonify({'message': 'Neighbor number has to be bigger than 0'})
                    resp.status_code = 406
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Neighbors has to be an integer'})
            resp.status_code = 406
            return resp
    else:
        return ''


def checkAlgorithm(form):
    if form.get('algorithm') is not None:
        if isinstance(form.get('algorithm'),str):
            if form.get('algorithm') == 'auto' or form.get('algorithm') == 'ball_tree' \
                    or form.get('algorithm') == 'kd_tree' or form.get('algorithm') == 'brute':
                return ''
            else:
                resp = jsonify({'message': 'The algorithm has to be ball_tree, kd_tree, auto or brute'})
                resp.status_code = 408
                return resp
        else:
            resp = jsonify({'message': 'The method has to be a string'})
            resp.status_code = 408
            return resp
    else:
        return ''


def checkWeightBool(form):
    if form.get('weight') is not None:
        if isinstance(form.get('weight'), str):
            if form.get('weight') == 'True' or form.get('weight') == 'False':
                return ''
            else:
                resp = jsonify({'message': 'Weight has to be a True or False string'})
                resp.status_code = 409
                return resp
        else:
            resp = jsonify({'message': 'Weight has to be a True or False string'})
            resp.status_code = 409
            return resp
    else:
        return ''


def checkTol(form):
    if form.get('tol') is not None:
        try:
            if float(form.get('tol')):
                if (float(form.get('tol')) >= 0.0):
                    return ''
                else:
                    resp = jsonify({'message': 'Tol has to be bigger than 0.0'})
                    resp.status_code = 410
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Tol has to be float type'})
            resp.status_code = 410
            return resp
    else:
        return ''


def checkEstimators(form):
    if form.get('estimators') is not None:
        try:
            if int(form.get('estimators')):
                if int(form.get('estimators')) > 0:
                    return ''
                else:
                    resp = jsonify({'message': 'Estimators have to be bigger than 0'})
                    resp.status_code = 411
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Estimators have to be an integer'})
            resp.status_code = 411
            return resp
    else:
        return ''


# Check Knn


def checkKnnNeighbors(df, form):
    if form.get('neighbors') is not None:
        try:
            if int(form.get('neighbors')):
                if int(form.get('neighbors')) > 0:
                    if int(form.get('neighbors')) <= df.shape[0]:
                        return ''
                    else:
                        resp = jsonify({'message': 'Neighbor number has to be smaller than the number of rows'})
                        resp.status_code = 406
                        return resp
                else:
                    resp = jsonify({'message': 'Neighbor number has to be bigger than 0'})
                    resp.status_code = 406
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Neighbor has to be an integer'})
            resp.status_code = 406
            return resp
    else:
        return ''


def checkMethodStr(form):
    if form.get('method') is not None:
        if isinstance(form.get('method'), str):
            if form.get('method') == 'largest' or form.get('method') == 'mean' or form.get('method') == 'median':
                return ''
            else:
                resp = jsonify({'message': 'The method has to be largest, mean or median string'})
                resp.status_code = 407
                return resp
        else:
            resp = jsonify({'message': 'The method has to be a string'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkKnnParams(df, form):
    if checkContamination(form) == '':
        if checkKnnNeighbors(df, form) == '':
            if checkMethodStr(form) == '':
                if checkAlgorithm(form) == '':
                    return ''
                else:
                    return checkAlgorithm(form)
            else:
                return checkMethodStr(form)
        else:
            return checkKnnNeighbors(df, form)
    else:
        return checkContamination(form)

# Check HBOs


def checkBins(form):
    if form.get('bins') is not None:
        if form.get('bins') == 'auto':
            return ''
        else:
            try:
                if int(form.get('bins')):
                    if int(form.get('bins')) > 0:
                        return ''
                    else:
                        resp = jsonify({'message': 'Bins has to be integer bigger than 0 or auto'})
                        resp.status_code = 406
                        return resp
            except ValueError:
                resp = jsonify({'message': 'Bins has to be integer or auto'})
                resp.status_code = 406
                return resp
    else:
        return ''


def checkAlphaFloat(form):
    if form.get('alpha') is not None:
        try:
            if float(form.get('alpha')):
                if (float(form.get('alpha')) >= 0.0) and (float(form.get('alpha')) <= 1.0):
                    return ''
                else:
                    resp = jsonify({'message': 'Alpha has to be between 0.0 and 1.0'})
                    resp.status_code = 407
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Alpha has to be float type'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkTolFloat(form):
    if form.get('tol') is not None:
        try:
            if float(form.get('tol')):
                if (float(form.get('tol')) >= 0.0) and (float(form.get('tol')) <= 1.0):
                    return ''
                else:
                    resp = jsonify({'message': 'Tol has to be between 0.0 and 1.0'})
                    resp.status_code = 408
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Tol has to be float type'})
            resp.status_code = 408
            return resp
    else:
        return ''


def checkHbosParams(form):
    if checkContamination(form) == '':
        if checkBins(form) == '':
            if checkAlphaFloat(form) == '':
                if checkTolFloat(form) == '':
                    return ''
                else:
                    return checkTolFloat(form)
            else:
                return checkAlphaFloat(form)
        else:
            return checkBins(form)
    else:
        return checkContamination(form)



# Check Cof


def checkMethodCof(form):
    if form.get('method') is not None:
        if isinstance(form.get('method'), str):
            if form.get('method') == 'fast' or form.get('method') == 'memory':
                return ''
            else:
                resp = jsonify({'message': 'The method has to be fast or memory'})
                resp.status_code = 407
                return resp
        else:
            resp = jsonify({'message': 'The method has to be a string'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkCofParams(form):
    if checkContamination(form) == '':
        if checkNeighbors(form) == '':
            if checkMethodCof(form) == '':
                return ''
            else:
                return checkMethodCof(form)
        else:
            return checkNeighbors(form)
    else:
        return checkContamination(form)


# Check Lof


def checkLeafSize(form):
    if form.get('leafSize') is not None:
        try:
            if int(form.get('leafSize')):
                if int(form.get('leafSize')) > 0:
                    return ''
                else:
                    resp = jsonify({'message': 'Leaf size has to be bigger than 0'})
                    resp.status_code = 407
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Leaf size has to be an integer'})
            resp.status_code = 407
            return resp

    else:
        return ''


def checkLofParams(form):
    if checkContamination(form) == '':
        if checkNeighbors(form) == '':
            if checkAlgorithm(form) == '':
                if checkLeafSize(form) == '':
                    return ''
                else:
                    return checkLeafSize(form)
            else:
                return checkAlgorithm(form)
        else:
            return checkNeighbors(form)
    else:
        return checkContamination(form)


# Check CBLOF


def checkClusters(form):
    if form.get('clusters') is not None:
        try:
            if int(form.get('clusters')):
                if int(form.get('clusters')) > 0:
                    return ''
                else:
                    resp = jsonify({'message': 'Clusters have to be bigger than 0'})
                    resp.status_code = 406
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Clusters have to be an integer'})
            resp.status_code = 406
            return resp

    else:
        return ''


def checkAlpha(form):
    if form.get('alpha') is not None:
        try:
            if float(form.get('alpha')):
                if (float(form.get('alpha')) >= 0.5) and (float(form.get('alpha')) <= 1.0):
                    return ''
                else:
                    resp = jsonify({'message': 'Alpha has to be between 0.5 and 1.0'})
                    resp.status_code = 407
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Alpha has to be float type'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkBeta(form):
    if form.get('beta') is not None:
        try:
            if float(form.get('beta')):
                if float(form.get('beta')) >=1.0:
                    return ''
                else:
                    resp = jsonify({'message': 'Beta have to be bigger or equal than 1'})
                    resp.status_code = 408
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Beta has to be an integer or a float'})
            resp.status_code = 408
            return resp

    else:
        return ''


def checkCblofParams(form):
    if checkContamination(form) == '':
        if checkClusters(form) == '':
            if checkAlpha(form) == '':
                if checkBeta(form) == '':
                    if checkWeightBool(form) == '':
                        return ''
                    else:
                        return checkWeightBool(form)
                else:
                    return checkBeta(form)
            else:
                return checkAlpha(form)
        else:
            return checkClusters(form)
    else:
        return checkContamination(form)


# Check pca


def checkWhitenBool(form):
    if form.get('whiten') is not None:
        if isinstance(form.get('whiten'), str):
            if form.get('whiten') == 'True' or form.get('whiten') == 'False':
                return ''
            else:
                resp = jsonify({'message': 'whiten has to be a True or False string'})
                resp.status_code = 406
                return resp
        else:
            resp = jsonify({'message': 'whiten has to be a True or False string'})
            resp.status_code = 406
            return resp
    else:
        return ''


def checkSvdSolver(form):
    if form.get('solver') is not None:
        if isinstance(form.get('solver'),str):
            if form.get('solver') == 'auto' or form.get('solver') == 'full' \
                    or form.get('solver') == 'arpack' or form.get('solver') == 'randomized':
                return ''
            else:
                resp = jsonify({'message': 'The solver has to be full, arpack, auto or randomized'})
                resp.status_code = 407
                return resp
        else:
            resp = jsonify({'message': 'The solver has to be a string'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkPcaParams(form):
    if checkContamination(form) == '':
        if checkWhitenBool(form) == '':
            if checkSvdSolver(form) == '':
                if checkTol(form) == '':
                    if checkWeightBool(form) == '':
                        return ''
                    else:
                        return checkWeightBool(form)
                else:
                    return checkTol(form)
            else:
                return checkSvdSolver(form)
        else:
            return checkWhitenBool(form)
    else:
        return checkContamination(form)


# Check sos

def checkPerplexity(form,df):
    if form.get('perplexity') is not None:
        try:
            if float(form.get('perplexity')):
                if float(form.get('perplexity')) >= 1:
                    if float(form.get('perplexity')) <= df.shape[0]-1:
                        return ''
                    else:
                        resp = jsonify({'message': 'perplexity number has to be smaller than the number of rows'})
                        resp.status_code = 406
                        return resp
                else:
                    resp = jsonify({'message': 'perplexity number has to be 1 or more'})
                    resp.status_code = 406
                    return resp
        except ValueError:
            resp = jsonify({'message': 'perplexity has to be an float'})
            resp.status_code = 406
            return resp
    else:
        return ''


def checkMetricsSos(form):

    my_list = ['euclidean', 'braycurtis','canberra','chebyshev','correlation','dice','hamming','jaccard','kulsinski',
            'mahalanobis','matching','minkowski','rogerstanimoto','russellrao','seuclidean','sokalmichener',
            'sokalsneath','sqeuclidean','yule']

    if form.get('metrics') is not None:
        if isinstance(form.get('metrics'), str):
            if form.get('metrics') in my_list:
                return ''
            else:
                resp = jsonify({'message': 'The metric has to be in the list '})
                resp.status_code = 407
                return resp
        else:
            resp = jsonify({'message': 'The metric has to be a string'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkEps(form):
    if form.get('eps') is not None:
        try:
            if float(form.get('eps')):
                if float(form.get('eps')) <= 0.0:
                    resp = jsonify({'message': 'Eps number has to be equal or bigger than 0'})
                    resp.status_code = 408
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Eps has to be an float'})
            resp.status_code = 408
            return resp
    else:
        return ''


def checkSosParams(form, df):
    if checkContamination(form) == '':
        if checkPerplexity(form, df) == '':
            if checkMetricsSos(form) == '':
                if checkEps(form) == '':
                    return ''
                else:
                    return checkEps(form)
            else:
                return checkMetricsSos(form)
        else:
            return checkPerplexity(form, df)
    else:
        return checkContamination(form)


# Check ocsvm


def checkKernel(form):
    list = ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed']

    if form.get('kernel') is not None:
        if isinstance(form.get('kernel'),str):
            if form.get('kernel') in list:
                return ''
            else:
                resp = jsonify({'message': 'The kernel has to be in the list '})
                resp.status_code = 406
                return resp
        else:
            resp = jsonify({'message': 'The kernel has to be a string'})
            resp.status_code = 406
            return resp
    else:
        return ''


def checkNu(form):
    if form.get('nu') is not None:
        try:
            if float(form.get('nu')):
                if float(form.get('nu')) > 0.0 and float(form.get('nu')) <= 1.0:
                    return ''
                else:
                    resp = jsonify({'message': 'nu number has to be bigger than 0.0 and smaller or equal to 1.0'})
                    resp.status_code = 407
                    return resp
        except ValueError:
            resp = jsonify({'message': 'nu has to be an float'})
            resp.status_code = 407
            return resp
    else:
        return ''


def checkDegree(form):
    if form.get('degree') is not None:
        try:
            if int(form.get('degree')):
                if int(form.get('degree')) > 0:
                    return ''
                else:
                    resp = jsonify({'message': 'Degree has to be bigger than 0'})
                    resp.status_code = 408
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Degree has to be an integer'})
            resp.status_code = 408
            return resp

    else:
        return ''


def checkOcsvmParams(form):
    if checkContamination(form) == '':
        if checkKernel(form) == '':
            if checkNu(form) == '':
                if checkDegree(form) == '':
                    if checkTol(form) == '':
                        return ''
                    else:
                        return checkTol(form)
                else:
                    return checkDegree(form)
            else:
                return checkNu(form)
        else:
            return checkKernel(form)
    else:
        return checkContamination(form)


# Check xgbod

def checkMaxDepth(form):
    if form.get('depth') is not None:
        try:
            if int(form.get('depth')):
                if int(form.get('depth')) > 0:
                    return ''
                else:
                    resp = jsonify({'message': 'Depth have to be bigger than 0'})
                    resp.status_code = 400
                    return resp
        except ValueError:
            resp = jsonify({'message': 'Depth have to be an integer'})
            resp.status_code = 400
            return resp
    else:
        return ''


def checkBooster(form):
    list = ['gbtree', 'gblinear', 'dart']

    if form.get('booster') is not None:
        if isinstance(form.get('booster'),str):
            if form.get('booster') in list:
                return ''
            else:
                resp = jsonify({'message': 'The booster has to be in the list '})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({'message': 'The booster has to be a string'})
            resp.status_code = 400
            return resp
    else:
        return ''


def checkXgbodParams(form):
    if checkMaxDepth(form) == '':
        if checkEstimators(form) == '':
            if checkBooster(form) == '':
               return ''
            else:
                return checkBooster(form)
        else:
            return checkEstimators(form)
    else:
        return checkMaxDepth(form)


# Check iforest

def checkBootstrap(form):
    if form.get('bootstrap') is not None:
        if isinstance(form.get('bootstrap'), str):
            if form.get('bootstrap') == 'True' or form.get('bootstrap') == 'False':
                return ''
            else:
                resp = jsonify({'message': 'Bootstrap has to be a True or False string'})
                resp.status_code = 406
                return resp
        else:
            resp = jsonify({'message': 'Bootstrap has to be a True or False string'})
            resp.status_code = 406
            return resp
    else:
        return ''


def checkIforestParams(form):
    if checkContamination(form) == '':
        if checkBootstrap(form) == '':
            if checkEstimators(form) == '':
                return ''
            else:
                return checkEstimators(form)
        else:
            return checkBootstrap(form)
    else:
        return checkContamination(form)








