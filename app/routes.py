from app import app
from flask import Flask, request, render_template, redirect, url_for, Response
from CreateClassSchedule import *
import os


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
