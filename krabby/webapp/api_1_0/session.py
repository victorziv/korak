from flask import jsonify, request, make_response
from config import logger
from . import api
from webapp.lib import reporthelper
from models import Sessionmod, Usermod

sessionmod = Sessionmod()
usermod = Usermod()
# ______________________________________


def calculate_session_state(states):
    if all([s == 'finished' for s in states]):
        return "finished"

    if all([s == 'pending' for s in states]):
        return "pending"

    if 'running' in states:
        return 'running'

    elif len(set(['onhold', 'finished', 'aborted']).intersection(set(states))):
        return 'onhold'

    return 'unknown'
# ______________________________________


@api.route('/machine/verified/<machineid>', methods=['DELETE'])
def delete_machine_from_verification(machineid):
    try:
        sessionmod.delete(machineid)
        return jsonify({'machineid': machineid})

    except Exception as e:
        logger.exception("!ERROR")
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________


@api.route('/verification/session/', methods=['GET'])
def get_session():
    try:
        logger.info("Get session args: {}".format(request.args))
        params = request.args

        current_page = int(params['page'])
        rows_limit = int(params['rows'])
        total = sessionmod.fetch_total()
        logger.debug("Total: %s", total)
        total_pages, offset = reporthelper.evaluate_page_data(total, current_page, rows_limit)
        logger.debug("Total pages: %s", total_pages)
        logger.debug("Offset: %s", offset)

        page_params = {
            'offset': offset,
            'limit': rows_limit,
            'sort_field': params['sidx'],
            'sort_order': params['sord']
        }

        verified_machines = sessionmod.fetch_page(page_params)

        logger.debug("Machines: {}".format(verified_machines))

        response_data = {
            "totalpages": total_pages,
            "totalrecords": total,
            "currpage": current_page,
            "session": [dict(m) for m in verified_machines]
        }

        return jsonify(response_data)

    except Exception as e:
        logger.exception('!ERROR')
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________


@api.route('/verification/session/owner/<username>', methods=['GET'])
def get_session_owner(username):
    try:
        owner = usermod.fetch_by_username(username)
        logger.debug("Owner: %r", owner)

        return jsonify(owner)

    except Exception as e:
        logger.exception('!ERROR')
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________


@api.route('/verification/session/<sessionid>/state', methods=['PUT'])
def update_session_state(sessionid):
    try:
        logger.debug("Session ID: %r", sessionid)
        task_states = sessionmod.fetch_session_task_states(sessionid)
        logger.debug("Task states for sessionid %s: %r", sessionid, task_states)
        state = calculate_session_state(task_states)
        sessionmod.update_session_state(sessionid, state)
        return jsonify({'state': state})
    except Exception as e:
        logger.exception("!ERROR")
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________


@api.route('/verification/session/<sessionid>/update/from/jira', methods=['PUT'])
def update_session_from_jira(sessionid):
    try:
        logger.debug("Machine session ID: %r", sessionid)
        sessionmod.update_session_from_jira(sessionid)
        return jsonify({'sessionid': sessionid})
    except Exception as e:
        logger.exception("!ERROR")
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________
