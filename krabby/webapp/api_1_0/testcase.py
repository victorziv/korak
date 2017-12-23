from flask import jsonify, request
from config import logger
from . import api
from models import Testcasemod
from webapp.lib import reporthelper
testcasemod = Testcasemod()
# ______________________________________

"""
It is a common practice to define
URLs that represent collections of resources with a trailing slash, as this gives them a
"folder" representation.
"""


@api.route('/testcases/', methods=['GET'])
def get_testcases():
    logger.debug("Get machines args: {}".format(request.args))

    current_page = int(request.args['page'])
    rows_limit = int(request.args['rows'])
    testcases_total = testcasemod.get_total()
    logger.debug("Testcases total: %s", testcases_total)
    total_pages, offset = reporthelper.evaluate_page_data(testcases_total, current_page, rows_limit)
    logger.debug("Total pages: %s", total_pages)
    logger.debug("Offset: %s", offset)

    args = {
        'offset': offset,
        'limit': rows_limit
    }
    testcases = testcasemod.get_all(args)
    logger.debug("Testcases: {}".format(testcases))

    response_data = {
        "totalpages": total_pages,
        "totalrecords": testcases_total,
        "currpage": current_page,
        "testcases": [dict(tc) for tc in testcases]
    }

    return jsonify(response_data)
# ______________________________________


@api.route('/testcases/<int:caseid>')
def get_testcase_by_id(caseid):
    testcase = testcasemod.get_one_by_id(caseid)
    return jsonify({'testcase': testcase})
# ______________________________________
