from flask import Blueprint
api = Blueprint('api', __name__)
# from . import machine  # noqa
from . import session  # noqa
from . import task  # noqa
from . import testcase # noqa
from . import ivtdoc  # noqa
