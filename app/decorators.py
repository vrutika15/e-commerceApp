from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to Admin and Super Admin only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role.name not in ['Admin', 'Super Admin']:
            abort(403)  # Forbidden if the user is neither Admin nor Super Admin
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """
    Decorator to restrict access to Super Admin only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role.name != 'Super Admin':
            abort(403)  # Forbidden if the user is not Super Admin
        return f(*args, **kwargs)
    return decorated_function
