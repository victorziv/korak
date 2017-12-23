import psycopg2
from flask import jsonify, request, make_response, url_for
from config import logger
from . import api
from models import Sessionmod, Sessiontaskmod, Taskhandler
from webapp.lib import reporthelper
sessionmod = Sessionmod()
session_taskmod = Sessiontaskmod()
task_handler = Taskhandler()
# ===============================


def add_uri(task):
    task['uri'] = url_for('api.get_task', sessionid=task['sessionid'], taskid=task['id'], _external=True)
    return task
# ______________________________________


@api.route('/verification/<sessionid>/tasks/<taskid>', methods=['GET'])
def get_task(sessionid, taskid):
    logger.info("ARGS: {}".format(request.args))

    task = session_taskmod.fetch_session_task(sessionid, taskid)
    logger.debug("Session task: %r", task)

    return jsonify({'task': task})
# ______________________________________


@api.route('/verification/<sessionid>/tasks/', methods=['GET'])
def get_tasks(sessionid):
    logger.info("Get verified machines args: {}".format(request.args))

    current_page = int(request.args['page'])
    rows_limit = int(request.args['rows'])
    sort_field = request.args['sidx']
    sort_order = request.args['sord']
    session_total = session_taskmod.fetch_total(sessionid)
    logger.debug("Session %s total: %s", sessionid, session_total)
    total_pages, offset = reporthelper.evaluate_page_data(session_total, current_page, rows_limit)

    page_params = {
        'sessionid': sessionid,
        'offset': offset,
        'limit': rows_limit,
        'sort_field': sort_field,
        'sort_order': sort_order
    }

    tasks = session_taskmod.fetch_page(page_params)
    logger.debug("Session tasks: %s", tasks)
#     for t in tasks:
#         reporthelper.compose_task_report(t)

    response_data = {
        "totalpages": total_pages,
        "totalrecords": session_total,
        "currpage": current_page,
        "tasks": [add_uri(dict(t)) for t in tasks]
    }

    return jsonify(response_data)
# ______________________________________


@api.route('/verification/session/tasks/<taskid>/current_state/<current_state>', methods=['GET'])
def check_task_state_change(taskid, current_state):
    logger.info("ARGS: {}".format(request.args))

    task = session_taskmod.fetch_session_task(taskid)
    logger.debug("TASK: %r", task)
    task['taskid'] = task['id']
    if task['state'] == current_state:
        task['state_changed'] = False
    else:
        task['state_changed'] = True

    return jsonify(task)
# ______________________________________


@api.route('/verification/session/task/queue', methods=['POST'])
def queue_task():
    try:
        task = request.get_json()['task']
        session_taskmod.put_session_task_in_queue(task)
        logger.debug("TASK: %r", task)
        session_taskmod.update(
            'session_task',
            rowid=task['session_taskid'],
            row=dict(state='queued', message=None, result=None, start=None, finish=None, log=None)
        )

        return jsonify({'taskid': task['session_taskid'], 'state': 'queued', 'taskname': task['session_task_name']})

    except psycopg2.IntegrityError as e:
        msg = "Another task of session {} already running".format(task['sessionuid'])
        return make_response(jsonify({'message': msg}), 409)

    except Exception as e:
        logger.exception("!ERROR")
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________


@api.route('/verification/session/task/action/<action>', methods=['POST'])
def stop_task(action):
    try:
        task = request.get_json()['task']
        logger.debug("TASK: %r", task)
        task['action'] = action
        taskid = session_taskmod.put_taskmng_in_queue(task)
        session_task = session_taskmod.fetch_session_task(taskid)

        return jsonify(
            {
                'taskid': taskid,
                'action': action,
                'taskname': session_task['taskname'],
                'state': session_task['state']
            }
        )

    except Exception as e:
        logger.exception("!ERROR")
        return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________


# @api.route('/verification/tasks/<int:taskid>/action/<action>', methods=['PUT'])
# def task_action(taskid, action):
#     try:
#         task = session_taskmod.fetch_session_task(taskid)
#         logger.debug("ACTION %s ON TASK: %r", action, task)
# #         task = taskmanager.trigger_action(task, action)
#         return jsonify({'task': task['name'], 'action': action, 'state': task['state']})
#     except Exception as e:
#         logger.exception("!ERROR")
#         return make_response(jsonify({'message': str(e)}), 500)
# ______________________________________
