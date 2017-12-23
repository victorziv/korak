from functools import wraps
from flask import g
from .errors import forbidden
# _______________________________


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("====> Current user: %r" % g.current_user)
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# _______________________________
