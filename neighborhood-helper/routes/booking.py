from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date
from database.db import query_db, execute_db
from utils.auth import login_required, role_required, add_notification

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/<int:helper_id>', methods=['GET', 'POST'])
@login_required
@role_required('user')
def create_booking(helper_id):
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    
    helper = query_db("""
        SELECT h.*, u.name as helper_name, u.phone as helper_phone, u.area as helper_area, u.city as helper_city,
               s.id as service_id, s.name as service_name, s.base_price
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE h.id = %s AND h.status = 'approved' AND u.is_active = 1
    """, (helper_id,), one=True)

    if not helper:
        flash('Helper is currently unavailable for booking.', 'warning')
        return redirect(url_for('user.search'))

    if helper['availability'] != 'Available':
        flash(f"Helper is currently marked as '{helper['availability']}'. Please choose another helper or check back later.", 'warning')

    if request.method == 'POST':
        problem_description = request.form.get('problem_description', '').strip()
        booking_date = request.form.get('booking_date', '').strip() or request.form.get('service_date', '').strip()
        preferred_time = request.form.get('preferred_time', '').strip()
        service_address = request.form.get('service_address', '').strip()
        additional_notes = request.form.get('additional_notes', '').strip()

        if not (problem_description and booking_date and preferred_time and service_address):
            flash('Please fill in all required fields (Problem Description, Date, Time, and Address).', 'danger')
            return render_template('user/book.html', helper=helper, user=user, form=request.form)

        # Generate unique booking code: BK1000 + next ID
        count_res = query_db("SELECT MAX(id) as max_id FROM bookings", one=True)
        next_num = (count_res['max_id'] or 0) + 1001
        booking_code = f"BK{next_num}"

        execute_db("""
            INSERT INTO bookings (booking_code, user_id, helper_id, service_id, problem_description, 
                                 booking_date, preferred_time, service_address, additional_notes, 
                                 status, service_amount, additional_charges, final_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', 0.00, 0.00, 0.00)
        """, (booking_code, user_id, helper['id'], helper['service_id'], problem_description,
              booking_date, preferred_time, service_address, additional_notes))

        # Send notifications
        add_notification(helper['user_id'], 
                         "New Booking Request", 
                         f"You have received a new booking request {booking_code} from {user['name']} for {helper['service_name']}.",
                         f"/helper/requests")
        add_notification(user_id,
                         "Booking Placed",
                         f"Your booking {booking_code} with {helper['helper_name']} has been submitted and is pending acceptance.",
                         f"/booking/{booking_code}")

        flash(f"Booking {booking_code} created successfully! Waiting for helper confirmation.", 'success')
        return redirect(url_for('booking.booking_details', booking_code=booking_code))

    today_str = date.today().isoformat()
    return render_template('user/book.html', helper=helper, user=user, today=today_str)

@booking_bp.route('/user/bookings')
@login_required
@role_required('user')
def user_bookings():
    user_id = session['user_id']
    status_filter = request.args.get('status', 'ALL').upper()

    sql = """
        SELECT b.*, s.name as service_name, s.icon as service_icon,
               u.name as helper_name, u.phone as helper_phone, u.area as helper_area, u.city as helper_city,
               r.id as review_id, r.rating as user_rating
        FROM bookings b
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u ON h.user_id = u.id
        JOIN services s ON b.service_id = s.id
        LEFT JOIN reviews r ON b.id = r.booking_id
        WHERE b.user_id = %s
    """
    params = [user_id]

    if status_filter == 'PENDING':
        sql += " AND b.status = 'PENDING'"
    elif status_filter == 'ACCEPTED':
        sql += " AND b.status = 'ACCEPTED'"
    elif status_filter == 'IN_PROGRESS':
        sql += " AND b.status = 'IN_PROGRESS'"
    elif status_filter == 'COMPLETED':
        sql += " AND b.status = 'COMPLETED'"
    elif status_filter == 'CANCELLED':
        sql += " AND b.status IN ('CANCELLED', 'REJECTED')"

    sql += " ORDER BY b.created_at DESC"
    bookings = query_db(sql, params)

    return render_template('user/bookings.html', bookings=bookings, current_status=status_filter)

@booking_bp.route('/booking/<string:booking_code>')
@login_required
def booking_details(booking_code):
    user_id = session['user_id']
    role = session.get('role')

    booking = query_db("""
        SELECT b.*, 
               s.name as service_name, s.icon as service_icon, s.base_price,
               u_cust.id as customer_id, u_cust.name as customer_name, u_cust.phone as customer_phone, 
               u_cust.email as customer_email, u_cust.area as customer_area, u_cust.city as customer_city,
               u_help.id as helper_user_id, u_help.name as helper_name, u_help.phone as helper_phone,
               u_help.email as helper_email, u_help.area as helper_area, u_help.city as helper_city,
               h.hourly_rate, h.avg_rating, h.total_reviews, h.experience_years,
               r.id as review_id, r.rating as review_rating, r.comment as review_comment, r.created_at as reviewed_at
        FROM bookings b
        JOIN users u_cust ON b.user_id = u_cust.id
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u_help ON h.user_id = u_help.id
        JOIN services s ON b.service_id = s.id
        LEFT JOIN reviews r ON b.id = r.booking_id
        WHERE b.booking_code = %s
    """, (booking_code,), one=True)

    if not booking:
        flash('Booking not found.', 'danger')
        if role == 'helper':
            return redirect(url_for('helper.jobs'))
        elif role == 'admin':
            return redirect(url_for('admin.bookings'))
        return redirect(url_for('booking.user_bookings'))

    # Security check: Only customer, helper, or admin can view this booking
    if role == 'user' and booking['customer_id'] != user_id:
        flash('Access denied. You do not own this booking.', 'danger')
        return redirect(url_for('booking.user_bookings'))
    if role == 'helper' and booking['helper_user_id'] != user_id:
        flash('Access denied. You are not assigned to this job.', 'danger')
        return redirect(url_for('helper.jobs'))

    return render_template('user/booking_detail.html', booking=booking)

@booking_bp.route('/booking/<string:booking_code>/cancel', methods=['POST'])
@login_required
@role_required('user')
def cancel_booking(booking_code):
    user_id = session['user_id']
    booking = query_db("SELECT b.*, h.user_id as helper_user_id FROM bookings b JOIN helpers h ON b.helper_id = h.id WHERE b.booking_code = %s AND b.user_id = %s", (booking_code, user_id), one=True)

    if not booking:
        flash('Booking not found or not owned by you.', 'danger')
        return redirect(url_for('booking.user_bookings'))

    if booking['status'] != 'PENDING':
        flash('Bookings can only be cancelled while in PENDING status.', 'warning')
        return redirect(url_for('booking.booking_details', booking_code=booking_code))

    reason = request.form.get('cancellation_reason', 'Cancelled by customer').strip()
    execute_db("UPDATE bookings SET status = 'CANCELLED', cancellation_reason = %s WHERE id = %s", (reason, booking['id']))

    add_notification(booking['helper_user_id'],
                     "Booking Cancelled",
                     f"Booking request {booking_code} was cancelled by the customer.",
                     f"/helper/requests")

    flash(f"Booking {booking_code} has been cancelled.", 'info')
    return redirect(url_for('booking.booking_details', booking_code=booking_code))

@booking_bp.route('/review/<string:booking_code>', methods=['GET', 'POST'])
@login_required
@role_required('user')
def add_review(booking_code):
    user_id = session['user_id']
    booking = query_db("""
        SELECT b.*, s.name as service_name, u.name as helper_name, u.phone as helper_phone,
               h.id as helper_profile_id, h.user_id as helper_user_id
        FROM bookings b
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u ON h.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.booking_code = %s AND b.user_id = %s
    """, (booking_code, user_id), one=True)

    if not booking:
        flash('Booking not found or unauthorized.', 'danger')
        return redirect(url_for('booking.user_bookings'))

    # Review requirement: Booking must be in COMPLETED status
    if booking['status'] != 'COMPLETED':
        flash('Reviews can only be submitted after the service is marked as completed by the helper.', 'warning')
        return redirect(url_for('booking.booking_details', booking_code=booking_code))

    # Check if already reviewed
    existing_review = query_db("SELECT id FROM reviews WHERE booking_id = %s", (booking['id'],), one=True)
    if existing_review:
        flash('You have already submitted a review for this booking.', 'info')
        return redirect(url_for('booking.booking_details', booking_code=booking_code))

    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating', 5))
        except ValueError:
            rating = 5

        if rating < 1 or rating > 5:
            flash('Please choose a rating between 1 and 5 stars.', 'danger')
            return render_template('user/review.html', booking=booking)

        comment = request.form.get('comment', '').strip()
        if not comment:
            flash('Please write a brief feedback comment about the service.', 'danger')
            return render_template('user/review.html', booking=booking)

        # Insert review
        execute_db("""
            INSERT INTO reviews (booking_id, user_id, helper_id, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (booking['id'], user_id, booking['helper_id'], rating, comment))

        # Dynamically recalculate helper's average rating and total reviews from reviews table
        helper_id = booking['helper_id']
        execute_db("""
            UPDATE helpers
            SET 
                avg_rating = COALESCE((SELECT ROUND(AVG(rating), 1) FROM reviews WHERE helper_id = %s), 0.0),
                total_reviews = (SELECT COUNT(*) FROM reviews WHERE helper_id = %s)
            WHERE id = %s
        """, (helper_id, helper_id, helper_id))

        # Send notification to helper
        add_notification(booking['helper_user_id'],
                         "New Review Received",
                         f"You received a {rating}-star review from {session['user_name']} for {booking_code}!",
                         f"/helper/reviews")

        flash('Thank you! Your rating and review have been published.', 'success')
        return redirect(url_for('booking.booking_details', booking_code=booking_code))

    return render_template('user/review.html', booking=booking)
