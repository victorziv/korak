import os
from flask import request, render_template, send_from_directory
from flask_login import login_required
from . import main
from models import Sessionmod
from config import logger
sessionmod = Sessionmod()
# ______________________________


@main.route('/', methods=['GET'])
@main.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template("main/dashboard/dashboard.html")
# ______________________________


@main.route('/machines/', methods=['GET'], defaults={'category': 'verification'})
@main.route('/machines/<category>/', methods=['GET'])
@login_required
def machines(category):
    logger.info("Machines category: %s", category)
    return render_template("main/%s/%s.html" % (category, category))
# ______________________________


@main.route('/testcases/', methods=['GET'])
def testcases():
    return render_template("main/testcases/testcases.html")
# ______________________________


@main.route('/task/log/', methods=['GET'])
def task_log():
    logfile = request.args.get('path', '')
    logdir = os.path.dirname(logfile)
    logfile = os.path.basename(logfile)
    return send_from_directory(logdir, logfile, mimetype="text/html")
# ______________________________________


@main.route('/machines/verified/session/<sessionid>/edit', methods=['GET'])
@login_required
def session_edit_form(sessionid):
    logger.info("Session ID to edit: %s", sessionid)
    session = sessionmod.fetch_session(sessionid)
    return render_template("main/verified/session_edit_form.html", session=session)
# ______________________________
