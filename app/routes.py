from app import app
from flask import Flask, request, render_template, redirect, url_for, Response
import os
import random
import datetime
import pandas as pd
import numpy as np
import pdfkit as pdf


def createMatrix(n):
    firstRow = random.sample(range(n), n)
    permutes = random.sample(range(n), n)
    return list(firstRow[i:] + firstRow[:i] for i in permutes)


def generateSchedule(n_students, n_stations):
    uneven = False
    if (n_students % n_stations) == 0:
        uneven = False
    else:
        uneven = True
    if not uneven:
        m = createMatrix(n_students)
        n_roles = int(round(n_students / n_stations))
        d = postProcess(m, n_roles, n_stations, uneven)

        if d == 0:
            bannerO = "=" * 30 + "=" * len(
                " SCHEDULE HAS BEEN OPTIMZED AND GENERATED ") + "=" * 30
            print(bannerO)
        else:
            generateSchedule(n_students, n_stations)
    else:
        m = createMatrix(n_students)
        n_roles = int(round(n_students / n_stations))
        matrix = getDF(m, uneven, n_students, n_stations)
        d = checkDuplicates(matrix)
        if d == 0:
            bannerO = "=" * 30 + "=" * len(
                " SCHEDULE HAS BEEN OPTIMZED AND GENERATED "
            ) + "=" * 30 + "\n\n"
            print(bannerO)
        else:
            generateSchedule(n_students, n_stations)

    return getDF(m, uneven, n_students, n_stations)


def getDF(m, uneven, n_students, n_stations):
    n_roles = int(round(n_students / n_stations))
    if not uneven:
        df = pd.DataFrame(m)
        df.index = [
            "Role {}".format((i % n_roles) + 1) for i in range(n_students)
        ]
        df.columns = ["Time {}".format(i) for i in range(n_students)]
    else:
        df = pd.DataFrame(m)
        break_rows = getBreakRows(n_students,
                                  determineNumBreaks(n_students, n_roles))
        rows = ["Role {}".format((i % n_roles) + 1) for i in range(n_students)]
        df.index = FixRows(rows, break_rows)
        df.columns = ["Time {}".format(i) for i in range(n_students)]
    return df


def postProcess(m, n_roles, n_stations, uneven):
    if not uneven:
        m = np.array(m)
        groups = m.reshape(n_stations, n_roles, m.shape[0])
        tuples = []
        ij = []
        for i, group in enumerate(groups):
            for j, section in enumerate(group.T):
                tuples.append(list(section[1:]))  #patient-PTA    print()
        d = len(getCounts(tuples))
        return d


def getCounts(tuples):
    d = {}
    for l in tuples:
        t = tuple(l)
        if t in d:
            d[t] += 1
        else:
            d[t] = 1
    d = dict((k, v) for k, v in d.items() if v > 1)
    return d


def createMatrixWithBreaks(n):
    firstRow = random.sample(range(n), n)
    permutes = random.sample(range(n), n)
    m = np.array(list(firstRow[i:] + firstRow[:i] for i in permutes))
    m = np.where(m == 0, -100, m)
    print(m.shape)
    return m


def determineNumBreaks(num_students, num_roles):
    return num_students % num_roles


def getBreakRows(num_students, num_breaks):
    every = num_students // (2 + num_breaks)
    break_rows = []
    for i in range(num_breaks):
        break_rows.append(every + i * every)
    return break_rows


def FixRows(rows, break_rows):
    for i, row in enumerate(break_rows):
        rows.insert(row, "Break")
        rows.pop()
    return rows


def checkDuplicates(matrix):
    patient_pta_roles = matrix.T.columns[-2], matrix.T.columns[-1]
    r2 = matrix.T[patient_pta_roles[0]].values
    r3 = matrix.T[patient_pta_roles[1]].values
    r2 = r2.T
    r3 = r3.T

    tuples = []
    for i in range(len(r2)):
        for j in range(len(r2[i])):
            tuples.append([r2[i][j], r3[i][j]])  #patient-PTA    print()
    d = len(getCounts(tuples))
    return d


def createHTML(df, pdfName="foo.pdf"):
    table = df.to_html(classes='mystyle')


def getPDF(df, pdfName="schedule.pdf"):
    df.to_html('results/df.html')
    pdf.from_file('results/df.html', pdfName)


def getCSV(df, pdfName="schedule.csv"):
    df.to_csv(pdfName)


def webappV1(n_students, n_stations):
    matrix = generateSchedule(n_students, n_stations)
    oname = "results/nstudents_{}_nstations_{}".format(n_students, n_stations)
    date = datetime.datetime.today().strftime('%Y-%m-%d-%H_%M_%S')

    csvFile = oname + "_" + date + ".csv"
    getCSV(matrix, pdfName=csvFile)
    bannerO = "=" * 30 + " SCHEDULE HAS BEEN OPTIMZED AND GENERATED " + "=" * 30
    print("\n\n{}\n\n".format(bannerO))
    return matrix, csvFile

# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods=["GET", "POST"])
def gfg():
    base_dir = os.getcwd()
    if request.method == "POST":
        n_students = int(request.form.get("nstudents"))
        n_stations = int(request.form.get("nstations"))

        df, cfile = webappV1(n_students, n_stations)
        # cfile = base_dir + "/" + cfile
        return render_template('simple.html',
                               tables=[df.to_html(classes='data')],
                               titles=df.columns.values,
                               file=cfile)

    return render_template("form.html")


@app.route("/<csvdir>", methods=['get'])
def get_csv(csvdir):
    print("here")
    with open(csvdir) as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"content-disposition": "attachment; filename=data.csv"})
