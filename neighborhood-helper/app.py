import os
from flask import Flask, render_template, session, g, jsonify, request
from config import Config
from database.db import close_db, query_db, execute_db, init_database
from routes.auth import auth_bp
from routes.user import user_bp
from routes.helper import helper_bp
from routes.admin import admin_bp
from routes.booking import booking_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register database teardown
app.teardown_appcontext(close_db)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(helper_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(booking_bp)

@app.context_processor
def inject_global_data():
    """Injects user session data, unread notifications, and active services into all templates."""
    current_user = None
    unread_notifications = []
    unread_count = 0

    if 'user_id' in session:
        current_user = query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)
        if not current_user:
            session.clear()
        else:
            unread_notifications = query_db("""
                SELECT * FROM notifications 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (session['user_id'],))
            unread_res = query_db("""
                SELECT COUNT(*) as c FROM notifications 
                WHERE user_id = %s AND is_read = 0
            """, (session['user_id'],), one=True)
            unread_count = unread_res['c'] if unread_res else 0

    nav_services = query_db("SELECT id, name, icon FROM services WHERE is_active = 1 ORDER BY name ASC LIMIT 8")

    db_cities_rows = query_db("""
        SELECT DISTINCT u.city 
        FROM helpers h 
        JOIN users u ON h.user_id = u.id 
        WHERE h.status = 'approved' AND u.is_active = 1 AND u.city IS NOT NULL AND u.city != ''
        ORDER BY u.city ASC
    """)
    cities_set = {r['city'].strip().title() for r in (db_cities_rows or []) if r.get('city')}
    for core_city in ['Coimbatore', 'Chennai', 'Madurai']:
        cities_set.add(core_city)
    available_cities = sorted(list(cities_set))

    return {
        'current_user': current_user,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
        'nav_services': nav_services,
        'available_cities': available_cities
    }

@app.route('/')
def index():
    services = query_db("SELECT * FROM services WHERE is_active = 1 ORDER BY name ASC")
    
    # Top rated approved helpers for showcase
    featured_helpers = query_db("""
        SELECT h.*, u.name as helper_name, u.area, u.city, s.name as service_name, s.icon as service_icon
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE h.status = 'approved' AND u.is_active = 1
        ORDER BY h.avg_rating DESC, h.total_reviews DESC
        LIMIT 4
    """)

    # Overall system stats for hero banner
    stats = {
        'total_helpers': query_db("SELECT COUNT(*) as c FROM helpers WHERE status = 'approved'", one=True)['c'],
        'total_bookings': query_db("SELECT COUNT(*) as c FROM bookings", one=True)['c'],
        'avg_rating': 4.8
    }

    return render_template('index.html', services=services, featured_helpers=featured_helpers, stats=stats)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/search')
def search_redirect():
    return redirect(url_for('user.search', **request.args))

@app.route('/login')
def login_redirect():
    return redirect(url_for('auth.login', **request.args))

@app.route('/logout')
def logout_redirect():
    return redirect(url_for('auth.logout'))

@app.route('/api/notifications/mark-all-read', methods=['POST'])
def mark_notifications_read():
    if 'user_id' in session:
        execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (session['user_id'],))
        return jsonify({'status': 'success'})
    return jsonify({'status': 'unauthorized'}), 401

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize DB tables if needed on startup
    try:
        init_database(force=False)
    except Exception as e:
        print(f"Database check warning: {e}")

    # Run Flask development server
    app.run(host='127.0.0.1', port=5000, debug=True)
