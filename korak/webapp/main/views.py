from flask import render_template
from . import main
# ______________________________


@main.route('/', methods=['GET'])
def home():
    return render_template("main/home.html")
# ______________________________
