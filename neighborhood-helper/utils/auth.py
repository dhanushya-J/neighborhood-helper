from functools import wraps
from flask import session, redirect, url_for, flash, request, g
from database.db import query_db, execute_db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role')
            if user_role not in roles:
                flash('Access Denied: You do not have permission to view this section.', 'danger')
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'helper':
                    return redirect(url_for('helper.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Retrieves current logged in user dict or None."""
    if 'user_id' not in session:
        return None
    user = query_db("SELECT * FROM users WHERE id = %s AND is_active = 1", (session['user_id'],), one=True)
    return user

def add_notification(user_id, title, message, link=None):
    """Adds an in-app notification for a given user."""
    try:
        execute_db(
            "INSERT INTO notifications (user_id, title, message, link, is_read) VALUES (%s, %s, %s, %s, 0)",
            (user_id, title, message, link)
        )
    except Exception as e:
        print(f"Error adding notification: {e}")
