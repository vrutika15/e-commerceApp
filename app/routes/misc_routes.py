from flask import Blueprint, flash, redirect, url_for, request
from flask_login import login_required, logout_user

misc_bp = Blueprint('misc', __name__)


# Logout route
@misc_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.admin_login'))


@misc_bp.route('/search')
def search():
    query = request.args.get('q')
    # Dummy response or redirect
    return f"<h1>Search Results for: {query}</h1>"