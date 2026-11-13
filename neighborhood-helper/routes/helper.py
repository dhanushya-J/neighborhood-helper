from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import query_db, execute_db
from utils.auth import login_required, role_required, add_notification
from utils.distance import resolve_coordinates

helper_bp = Blueprint('helper', __name__, url_prefix='/helper')

def get_current_helper_id():
    user_id = session.get('user_id')
    h = query_db("SELECT id FROM helpers WHERE user_id = %s", (user_id,), one=True)
    return h['id'] if h else None

@helper_bp.route('/dashboard')
@login_required
@role_required('helper')
def dashboard():
    user_id = session['user_id']
    helper = query_db("""
        SELECT h.*, u.name, u.name as helper_name, u.email, u.phone, u.area, u.city, s.name as service_name
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE h.user_id = %s
    """, (user_id,), one=True)

    if not helper:
        flash('Helper profile not found.', 'danger')
        return redirect(url_for('auth.logout'))

    helper_id = helper['id']

    # Statistics
    new_requests_count = query_db("SELECT COUNT(*) as c FROM bookings WHERE helper_id = %s AND status = 'PENDING'", (helper_id,), one=True)['c']
    accepted_jobs_count = query_db("SELECT COUNT(*) as c FROM bookings WHERE helper_id = %s AND status = 'ACCEPTED'", (helper_id,), one=True)['c']
    active_jobs_count = query_db("SELECT COUNT(*) as c FROM bookings WHERE helper_id = %s AND status IN ('ACCEPTED', 'IN_PROGRESS')", (helper_id,), one=True)['c']
    completed_jobs_count = query_db("SELECT COUNT(*) as c FROM bookings WHERE helper_id = %s AND status = 'COMPLETED'", (helper_id,), one=True)['c']

    stats = {
        'new_requests': new_requests_count,
        'accepted_jobs': accepted_jobs_count,
        'active_jobs': active_jobs_count,
        'completed_jobs': completed_jobs_count,
        'avg_rating': helper['avg_rating'],
        'total_reviews': helper['total_reviews']
    }

    # Recent pending requests
    pending_requests = query_db("""
        SELECT b.*, u.name as customer_name, u.phone as customer_phone, u.area as customer_area, u.city as customer_city, s.name as service_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.helper_id = %s AND b.status = 'PENDING'
        ORDER BY b.created_at DESC
        LIMIT 5
    """, (helper_id,))

    # Active ongoing jobs
    active_jobs = query_db("""
        SELECT b.*, u.name as customer_name, u.phone as customer_phone, u.area as customer_area, u.city as customer_city, s.name as service_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.helper_id = %s AND b.status IN ('ACCEPTED', 'IN_PROGRESS')
        ORDER BY b.booking_date ASC
        LIMIT 5
    """, (helper_id,))

    return render_template('helper/dashboard.html', 
                           helper=helper, 
                           stats=stats, 
                           pending_requests=pending_requests,
                           active_jobs=active_jobs)

@helper_bp.route('/requests')
@login_required
@role_required('helper')
def requests_list():
    helper_id = get_current_helper_id()
    requests = query_db("""
        SELECT b.*, u.name as customer_name, u.phone as customer_phone, u.area as customer_area, u.city as customer_city, s.name as service_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.helper_id = %s AND b.status = 'PENDING'
        ORDER BY b.created_at DESC
    """, (helper_id,))
    return render_template('helper/requests.html', requests=requests)

@helper_bp.route('/booking/<int:booking_id>/accept', methods=['POST'])
@login_required
@role_required('helper')
def accept_booking(booking_id):
    helper_id = get_current_helper_id()
    booking = query_db("SELECT b.*, u.id as customer_user_id FROM bookings b JOIN users u ON b.user_id = u.id WHERE b.id = %s AND b.helper_id = %s", (booking_id, helper_id), one=True)
    
    if not booking:
        flash('Booking not found or not assigned to you.', 'danger')
        return redirect(url_for('helper.requests_list'))

    if booking['status'] != 'PENDING':
        flash('This request is no longer pending.', 'warning')
        return redirect(url_for('helper.requests_list'))

    execute_db("UPDATE bookings SET status = 'ACCEPTED' WHERE id = %s", (booking_id,))

    add_notification(booking['customer_user_id'],
                     "Booking Accepted",
                     f"Your booking {booking['booking_code']} has been accepted by the helper.",
                     f"/booking/{booking['booking_code']}")

    flash(f"Booking {booking['booking_code']} accepted! You can now start work when you arrive at the location.", 'success')
    return redirect(url_for('helper.jobs'))

@helper_bp.route('/booking/<int:booking_id>/reject', methods=['POST'])
@login_required
@role_required('helper')
def reject_booking(booking_id):
    helper_id = get_current_helper_id()
    reason = request.form.get('rejection_reason', 'Helper unavailable at requested time').strip()
    booking = query_db("SELECT b.*, u.id as customer_user_id FROM bookings b JOIN users u ON b.user_id = u.id WHERE b.id = %s AND b.helper_id = %s", (booking_id, helper_id), one=True)
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('helper.requests_list'))

    if booking['status'] != 'PENDING':
        flash('This request is no longer pending.', 'warning')
        return redirect(url_for('helper.requests_list'))

    execute_db("UPDATE bookings SET status = 'REJECTED', cancellation_reason = %s WHERE id = %s", (reason, booking_id))

    add_notification(booking['customer_user_id'],
                     "Booking Declined",
                     f"Your booking request {booking['booking_code']} could not be accepted: {reason}",
                     f"/booking/{booking['booking_code']}")

    flash(f"Booking {booking['booking_code']} was rejected.", 'info')
    return redirect(url_for('helper.requests_list'))

@helper_bp.route('/booking/<int:booking_id>/start', methods=['POST'])
@login_required
@role_required('helper')
def start_work(booking_id):
    helper_id = get_current_helper_id()
    booking = query_db("SELECT b.*, u.id as customer_user_id FROM bookings b JOIN users u ON b.user_id = u.id WHERE b.id = %s AND b.helper_id = %s", (booking_id, helper_id), one=True)
    
    if not booking or booking['status'] != 'ACCEPTED':
        flash('Job must be in ACCEPTED status before starting work.', 'warning')
        return redirect(url_for('helper.jobs'))

    execute_db("UPDATE bookings SET status = 'IN_PROGRESS' WHERE id = %s", (booking_id,))

    add_notification(booking['customer_user_id'],
                     "Work Started",
                     f"The helper has started work on booking {booking['booking_code']}.",
                     f"/booking/{booking['booking_code']}")

    flash(f"Work started on booking {booking['booking_code']}.", 'info')
    return redirect(url_for('helper.jobs'))

@helper_bp.route('/booking/<int:booking_id>/complete', methods=['POST'])
@login_required
@role_required('helper')
def complete_work(booking_id):
    helper_id = get_current_helper_id()
    booking = query_db("SELECT b.*, u.id as customer_user_id FROM bookings b JOIN users u ON b.user_id = u.id WHERE b.id = %s AND b.helper_id = %s", (booking_id, helper_id), one=True)
    
    if not booking or booking['status'] != 'IN_PROGRESS':
        flash('Job must be IN_PROGRESS to mark as completed.', 'warning')
        return redirect(url_for('helper.jobs'))

    # Transition booking directly to COMPLETED (no payment step)
    execute_db("UPDATE bookings SET status = 'COMPLETED' WHERE id = %s", (booking_id,))

    add_notification(booking['customer_user_id'],
                     "Work Completed",
                     f"Your service for booking {booking['booking_code']} has been completed! Please rate and review your helper.",
                     f"/booking/{booking['booking_code']}")

    flash(f"Work on booking {booking['booking_code']} marked as completed!", 'success')
    return redirect(url_for('helper.jobs'))

@helper_bp.route('/jobs')
@login_required
@role_required('helper')
def jobs():
    helper_id = get_current_helper_id()
    tab = request.args.get('tab', 'active')

    sql = """
        SELECT b.*, u.name as customer_name, u.phone as customer_phone, u.area as customer_area, u.city as customer_city,
               s.name as service_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.helper_id = %s
    """
    params = [helper_id]

    if tab == 'active':
        sql += " AND b.status IN ('ACCEPTED', 'IN_PROGRESS')"
    elif tab == 'completed':
        sql += " AND b.status = 'COMPLETED'"

    sql += " ORDER BY b.created_at DESC"
    jobs = query_db(sql, params)

    return render_template('helper/jobs.html', jobs=jobs, current_tab=tab)

@helper_bp.route('/reviews')
@login_required
@role_required('helper')
def reviews():
    helper_id = get_current_helper_id()
    reviews_list = query_db("""
        SELECT r.*, u.name as reviewer_name, u.area as reviewer_area, b.booking_code
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        JOIN bookings b ON r.booking_id = b.id
        WHERE r.helper_id = %s
        ORDER BY r.created_at DESC
    """, (helper_id,))
    
    helper = query_db("SELECT avg_rating, total_reviews FROM helpers WHERE id = %s", (helper_id,), one=True)
    return render_template('helper/reviews.html', reviews=reviews_list, helper=helper)

@helper_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('helper')
def profile():
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', 'Coimbatore').strip()
        area = request.form.get('area', '').strip()
        experience_years = request.form.get('experience_years', 1)
        hourly_rate = request.form.get('hourly_rate', 300)
        availability = request.form.get('availability', 'Available')
        description = request.form.get('description', '').strip()

        if not (name and phone and address and area):
            flash('Name, phone, address, and area are required.', 'danger')
        else:
            lat, lng, _, _ = resolve_coordinates(city, area)
            execute_db("""
                UPDATE users 
                SET name = %s, phone = %s, address = %s, city = %s, area = %s, latitude = %s, longitude = %s
                WHERE id = %s
            """, (name, phone, address, city, area, lat, lng, user_id))
            
            execute_db("""
                UPDATE helpers 
                SET experience_years = %s, hourly_rate = %s, availability = %s, description = %s
                WHERE user_id = %s
            """, (experience_years, hourly_rate, availability, description, user_id))
            
            session['user_name'] = name
            flash('Helper profile updated successfully!', 'success')
            return redirect(url_for('helper.profile'))

    helper = query_db("""
        SELECT h.*, u.name, u.email, u.phone, u.address, u.city, u.area, s.name as service_name
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE h.user_id = %s
    """, (user_id,), one=True)
    return render_template('helper/profile.html', helper=helper)
