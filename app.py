from flask_swagger_ui import get_swaggerui_blueprint
import pandas as pd
from flask import Flask, request, redirect, jsonify, make_response
from anomDetCode.naValues import naDataGeneralInfo, changeNA, changeNAvaluesNum, changeNAvaluesCat
from anomDetCode.checks import checkFile, checkCatColumns, checkNumericColumns, checkNum, checkCat, checkMix, \
    checkKnnParams, checkHbosParams, checkCofParams, checkLofParams, checkCblofParams, checkPcaParams, checkSosParams, \
    checkOcsvmParams, checkXgbodParams, checkIforestParams
from anomDetCode.preprocessing import standarize, dencoding
from anomDetCode.unsupervised import knnAd, hbosAd, cofAd, lofAd, cblofAd, pcaAd
from anomDetCode.semisupervised import iforestAd, xgbodAd, ocsvmAd, sosAd

UPLOAD_FOLDER = 'upload'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv'}

### swagger specific ###
SWAGGER_URL = '/doc'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Anomaly detection"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# %%%%%%%%%%%%%%% INFORMATION ABOUT THE DATA SET %%%%%%%%%%%%%%%

# Gives information about the NA values of the csv. It tells how many rows has NA values and
# the number and percentage of NA value each column has
@app.route('/naValues/info', methods=['POST'])
def infoNaValues():
    file = request.files
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        result = naDataGeneralInfo(x)
        if result[0] == 0:
            resp = jsonify({'message': 'Your file has ' + str(result[0]) + ' NA values.'})
            resp.status_code = 200
        else:
            resp = jsonify(
                {'message': 'Your file has ' + str(result[0]) + ' NA values, distributed in ' + str(result[2]) +
                            ' rows and ' + str(result[4]) + ' columns, that are ' + result[3]})
            resp.status_code = 201
    else:
        resp = x
    return resp


# %%%%%%%%%%%%%%% PREPROCESSING %%%%%%%%%%%%%%%

# Standarize numeric values of the desired columns
# need a csv and a string with the columns' names separated by ,
# returns a modified csv
@app.route('/preprocessing/standarize', methods=['POST'])
def stanData():
    file = request.files
    columns = request.form
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        if checkNumericColumns(x, columns) == '':
            columns = columns.get('columnsNum').split(',')
            resp = make_response(standarize(x, columns).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkNumericColumns(x, columns)
    else:
        resp = x
    return resp


# Apply dummy decoding
# need a csv and a the name of the columns
# returns a modified csv
@app.route('/preprocessing/dummyEn', methods=['POST'])
def dumEncond():
    file = request.files
    columns = request.form
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        if checkCatColumns(x, columns) == '':
            columns = request.form.get('columnsCat').split(',')
            resp = make_response(dencoding(x, columns).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkCatColumns(x, columns)
    else:
        resp = x
    return resp


# %%%%%%%%%%%%%%% TREATING NA VALUES %%%%%%%%%%%%%%%

# Replace na values in a numeric csv with the method that the user wants
# need a csv, a method and a string with the column name separated by ,
# it returns the csv modified
@app.route('/naValues/rNaNum', methods=['POST'])
def replaceNaNumeric():
    file = request.files
    form1 = request.form
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        y = checkNum(x, form1)
        if y == '':
            method = form1.get('methodNum')
            columns = form1.get('columnsNum').split(',')
            resp = make_response(changeNAvaluesNum(x, method, columns).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            resp = y
    else:
        resp = x
    return resp


# Replace na values in a categorical csv with the method that the user wants
# need a csv, a method and a string with the columns' name separated by ,
# it returns the csv modified
@app.route('/naValues/rNaCat', methods=['POST'])
def replaceNaCategorical():
    file = request.files
    form1 = request.form
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        y = checkCat(x, form1)
        if y == '':
            method = form1.get('methodCat')
            columns = form1.get('columnsCat').split(',')
            resp = make_response(changeNAvaluesCat(x, method, columns).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            print(y)
            resp = y
    else:
        resp = x
    return resp


# Replace na values in a mixed dataset
# need a csv, categorical method, categorical columns, numeric method, numeric columns
@app.route('/naValues/rNaMix', methods=['POST'])
def replaceNaMix():
    file = request.files
    form1= request.form
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        y = checkMix(x, form1)
        if y == '':
            methodCat = request.form.get('methodCat')
            columnsCat = request.form.get('columnsCat').split(',')
            methodNum = request.form.get('methodNum')
            columnsNum = request.form.get('columnsNum').split(',')
            x = changeNAvaluesCat(x, methodCat, columnsCat)
            resp = make_response(changeNAvaluesNum(x, methodNum, columnsNum).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            resp = y
    else:
        resp = x
    return resp


# Change the values ?,-,'' for na values
# it return a csv with the values changed
@app.route('/naValues/change', methods=['POST'])
def changeToNa():
    file = request.files
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        resp = make_response(changeNA(x).to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        resp.status_code = 201
    else:
        resp = x
    return resp


# %%%%%%%%%%%%%%% ANOMALY DETECTION %%%%%%%%%%%%%%%
# Anomalies are detected in a csv using knn
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/kNN', methods=['POST'])
def anDetKnn():
    file = request.files
    form = request.form
    x = checkFile(file)
    if isinstance(x, pd.DataFrame):
        if checkKnnParams(x, form) == '':
            resp = make_response(knnAd(x,form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkKnnParams(x, form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using hbos
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/hbos', methods=['POST'])
def anDetHbos():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkHbosParams(form) == '':
            resp = make_response(hbosAd(x, form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkHbosParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using cof
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/cof', methods=['POST'])
def anDetcof():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkCofParams(form) == '':
            resp = make_response(cofAd(x,form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkCofParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using lof
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/lof', methods=['POST'])
def anDetlof():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkLofParams(form) == '':
            resp = make_response(lofAd(x,form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkLofParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using cblof
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/cblof', methods=['POST'])
def anDetcblof():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkCblofParams(form) == '':
            resp = make_response(cblofAd(x,form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkCblofParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using pca
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/pca', methods=['POST'])
def anDetpca():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkPcaParams(form) == '':
            resp = make_response(pcaAd(x,form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkPcaParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using sos
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/sos', methods=['POST'])
def anDetsos():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkSosParams(form,x) == '':
            resp = make_response(sosAd(x, form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkSosParams(form,x)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using ocsvm
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/ocsvm', methods=['POST'])
def anDetocsvm():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkOcsvmParams(form) == '':
            resp = make_response(ocsvmAd(x, form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkOcsvmParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using xgbod
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies

# NECESITA EL GROUND TRUE EN EL FIT, REPASAR Y HACER SI QUEREMOS O ELIMINAR
@app.route('/anomalyDetection/xgbod', methods=['POST'])
def anDetxgbod():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkXgbodParams(form) == '':
            resp = make_response(xgbodAd(x, form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkXgbodParams(form)
    else:
        resp = x
    return resp


# Anomalies are detected in a csv using iforest
# need a numeric csv without na values
# return a csv with the rows that are supposed to be anomalies
@app.route('/anomalyDetection/iforest', methods=['POST'])
def anDetiforest():
    file = request.files
    x = checkFile(file)
    form = request.form
    if isinstance(x, pd.DataFrame):
        if checkIforestParams(form) == '':
            resp = make_response(iforestAd(x, form).to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"
            resp.status_code = 201
        else:
            return checkIforestParams(form)
    else:
        resp = x
    return resp


if __name__ == "__main__":
    app.run()
