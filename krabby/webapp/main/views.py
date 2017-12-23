from flask import render_template
from flask_login import login_required
from . import main
# ______________________________


@main.route('/', methods=['GET'])
@login_required
def index():
    return render_template("main/index.html")
# ______________________________
