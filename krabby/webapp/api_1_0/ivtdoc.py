import os
import subprocess
from flask import jsonify
from flask import current_app as cup
from . import api
# ______________________________________


def build_ivtdoc():
    ivt_test_path = cup.config['IVT_TEST_DIR']
    os.chdir(ivt_test_path)
    print("IVT tests directory: {}".format(os.getcwd()))
    subprocess.call('./docbuild.sh')
    return True
# ______________________________________


@api.route('/ivtdoc/update', methods=['GET', 'POST'])
def ivtdoc_update():
    print("Updating IVT documentation")
    status = build_ivtdoc()
    return jsonify({'status': status})
# ______________________________________
