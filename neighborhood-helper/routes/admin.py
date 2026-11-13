from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import query_db, execute_db
from utils.auth import login_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Key administrative metrics (Requirement 15: No revenue/payments, only operational counts)
    total_users = query_db("SELECT COUNT(*) as c FROM users WHERE role = 'user'", one=True)['c']
    total_helpers = query_db("SELECT COUNT(*) as c FROM helpers", one=True)['c']
    approved_helpers = query_db("SELECT COUNT(*) as c FROM helpers WHERE status = 'approved'", one=True)['c']
    total_services = query_db("SELECT COUNT(*) as c FROM services WHERE is_active = 1", one=True)['c']
    total_bookings = query_db("SELECT COUNT(*) as c FROM bookings", one=True)['c']
    pending_bookings = query_db("SELECT COUNT(*) as c FROM bookings WHERE status = 'PENDING'", one=True)['c']
    active_bookings = query_db("SELECT COUNT(*) as c FROM bookings WHERE status IN ('ACCEPTED', 'IN_PROGRESS')", one=True)['c']
    completed_bookings = query_db("SELECT COUNT(*) as c FROM bookings WHERE status = 'COMPLETED'", one=True)['c']
    cancelled_bookings = query_db("SELECT COUNT(*) as c FROM bookings WHERE status IN ('CANCELLED', 'REJECTED')", one=True)['c']
    avg_rating_res = query_db("SELECT COALESCE(ROUND(AVG(rating), 1), 0.0) as r FROM reviews", one=True)
    avg_rating = float(avg_rating_res['r']) if avg_rating_res else 0.0

    metrics = {
        'total_users': total_users,
        'total_helpers': total_helpers,
        'approved_helpers': approved_helpers,
        'total_services': total_services,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'avg_rating': avg_rating
    }

    # Recent bookings
    recent_bookings = query_db("""
        SELECT b.*, u_c.name as customer_name, u_h.name as helper_name, s.name as service_name
        FROM bookings b
        JOIN users u_c ON b.user_id = u_c.id
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u_h ON h.user_id = u_h.id
        JOIN services s ON b.service_id = s.id
        ORDER BY b.created_at DESC
        LIMIT 8
    """)

    return render_template('admin/dashboard.html', metrics=metrics, recent_bookings=recent_bookings)

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    search = request.args.get('q', '').strip()
    sql = "SELECT * FROM users WHERE role = 'user'"
    params = []
    if search:
        sql += " AND (name LIKE %s OR email LIKE %s OR phone LIKE %s OR area LIKE %s OR city LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
    sql += " ORDER BY created_at DESC"
    users_list = query_db(sql, params)
    return render_template('admin/users.html', users=users_list, search=search)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    user = query_db("SELECT id, name, is_active FROM users WHERE id = %s", (user_id,), one=True)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))

    new_status = 0 if user['is_active'] else 1
    execute_db("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id))
    action_text = 'activated' if new_status == 1 else 'deactivated'
    flash(f"User {user['name']} has been {action_text}.", 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/helpers')
@login_required
@role_required('admin')
def helpers():
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'all')
    sql = """
        SELECT h.*, u.name, u.email, u.phone, u.area, u.city, u.is_active, s.name as service_name
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE 1=1
    """
    params = []

    if status_filter != 'all':
        sql += " AND h.status = %s"
        params.append(status_filter)

    if search:
        sql += " AND (u.name LIKE %s OR u.email LIKE %s OR u.area LIKE %s OR u.city LIKE %s OR s.name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    sql += " ORDER BY h.created_at DESC"
    helpers_list = query_db(sql, params)

    return render_template('admin/helpers.html', helpers=helpers_list, search=search, current_status=status_filter)

@admin_bp.route('/helpers/<int:helper_id>/status', methods=['POST'])
@login_required
@role_required('admin')
def update_helper_status(helper_id):
    new_status = request.form.get('status')
    if new_status not in ['approved', 'rejected', 'pending']:
        flash('Invalid status choice.', 'danger')
        return redirect(url_for('admin.helpers'))

    execute_db("UPDATE helpers SET status = %s WHERE id = %s", (new_status, helper_id))
    flash(f"Helper profile status updated to '{new_status}'.", 'success')
    return redirect(url_for('admin.helpers'))

@admin_bp.route('/services', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def services():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        icon = request.form.get('icon', 'wrench').strip()
        description = request.form.get('description', '').strip()
        base_price = request.form.get('base_price', 250.00)

        if not name:
            flash('Service name is required.', 'danger')
        else:
            try:
                execute_db("""
                    INSERT INTO services (name, icon, description, base_price, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (name, icon, description, base_price))
                flash(f"Service category '{name}' created successfully.", 'success')
            except Exception as e:
                flash(f"Error creating service: {str(e)}", 'danger')

        return redirect(url_for('admin.services'))

    services_list = query_db("""
        SELECT s.*, COUNT(h.id) as helper_count
        FROM services s
        LEFT JOIN helpers h ON s.id = h.service_id
        GROUP BY s.id
        ORDER BY s.name ASC
    """)
    return render_template('admin/services.html', services=services_list)

@admin_bp.route('/services/<int:service_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_service(service_id):
    service = query_db("SELECT id, name, is_active FROM services WHERE id = %s", (service_id,), one=True)
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('admin.services'))

    new_status = 0 if service['is_active'] else 1
    execute_db("UPDATE services SET is_active = %s WHERE id = %s", (new_status, service_id))
    action_text = 'activated' if new_status == 1 else 'deactivated'
    flash(f"Service category '{service['name']}' has been {action_text}.", 'info')
    return redirect(url_for('admin.services'))

@admin_bp.route('/bookings')
@login_required
@role_required('admin')
def bookings():
    status = request.args.get('status', 'all')
    service_id = request.args.get('service_id', type=int)
    search = request.args.get('q', '').strip()

    sql = """
        SELECT b.*, u_c.name as customer_name, u_c.phone as customer_phone,
               u_h.name as helper_name, u_h.phone as helper_phone,
               s.name as service_name
        FROM bookings b
        JOIN users u_c ON b.user_id = u_c.id
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u_h ON h.user_id = u_h.id
        JOIN services s ON b.service_id = s.id
        WHERE 1=1
    """
    params = []

    if status != 'all':
        sql += " AND b.status = %s"
        params.append(status)
    if service_id:
        sql += " AND b.service_id = %s"
        params.append(service_id)
    if search:
        sql += " AND (b.booking_code LIKE %s OR u_c.name LIKE %s OR u_h.name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    sql += " ORDER BY b.created_at DESC"
    bookings_list = query_db(sql, params)
    services_list = query_db("SELECT id, name FROM services ORDER BY name ASC")

    return render_template('admin/bookings.html', bookings=bookings_list, services=services_list, current_status=status, current_service=service_id, search=search)

@admin_bp.route('/reviews')
@login_required
@role_required('admin')
def reviews():
    reviews_list = query_db("""
        SELECT r.*, u_c.name as reviewer_name, u_h.name as helper_name, s.name as service_name, b.booking_code
        FROM reviews r
        JOIN users u_c ON r.user_id = u_c.id
        JOIN helpers h ON r.helper_id = h.id
        JOIN users u_h ON h.user_id = u_h.id
        JOIN services s ON h.service_id = s.id
        JOIN bookings b ON r.booking_id = b.id
        ORDER BY r.created_at DESC
    """)
    return render_template('admin/reviews.html', reviews=reviews_list)

@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_review(review_id):
    rev = query_db("SELECT helper_id FROM reviews WHERE id = %s", (review_id,), one=True)
    if rev:
        helper_id = rev['helper_id']
        execute_db("DELETE FROM reviews WHERE id = %s", (review_id,))
        # Recalculate helper rating
        execute_db("""
            UPDATE helpers
            SET 
                avg_rating = COALESCE((SELECT ROUND(AVG(rating), 1) FROM reviews WHERE helper_id = %s), 0.0),
                total_reviews = (SELECT COUNT(*) FROM reviews WHERE helper_id = %s)
            WHERE id = %s
        """, (helper_id, helper_id, helper_id))
        flash('Review deleted and helper rating recalculated.', 'info')
    return redirect(url_for('admin.reviews'))
