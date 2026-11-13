from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db
from utils.distance import resolve_coordinates

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'helper':
            return redirect(url_for('helper.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html', email=email)

        user = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)

        if not user['is_active']:
            flash('Your account has been deactivated. Please contact support/admin.', 'danger')
            return render_template('auth/login.html', email=email)

        # Helper approval check
        if user['role'] == 'helper':
            helper_record = query_db("SELECT * FROM helpers WHERE user_id = %s", (user['id'],), one=True)
            if helper_record and helper_record['status'] == 'rejected':
                flash('Your helper profile was not approved by administration.', 'danger')
                return render_template('auth/login.html', email=email)

        # Set session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['email'] = user['email']
        session['role'] = user['role']

        flash(f"Welcome back, {user['name']}!", 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user['role'] == 'helper':
            return redirect(url_for('helper.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', 'Chennai').strip()
        area = request.form.get('area', '').strip()

        # Validation
        if not (name and email and phone and password and confirm_password and address and area):
            flash('All fields are required. Please fill in every detail.', 'danger')
            return render_template('auth/register_user.html', form=request.form)

        if len(phone) < 10:
            flash('Please enter a valid 10-digit phone number.', 'danger')
            return render_template('auth/register_user.html', form=request.form)

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter carefully.', 'danger')
            return render_template('auth/register_user.html', form=request.form)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register_user.html', form=request.form)

        # Check existing email
        existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Resolve coordinates from city and area
        lat, lng, display_area, resolved_city = resolve_coordinates(city=city, area=area)
        city = resolved_city
        if display_area and not area:
            area = display_area

        # Password hash
        pwd_hash = generate_password_hash(password)

        res = execute_db("""
            INSERT INTO users (name, email, password_hash, phone, role, address, city, area, latitude, longitude, is_active)
            VALUES (%s, %s, %s, %s, 'user', %s, %s, %s, %s, %s, 1)
        """, (name, email, pwd_hash, phone, address, city, area, lat, lng))

        user_id = res['last_id']

        # Auto login
        session['user_id'] = user_id
        session['user_name'] = name
        session['email'] = email
        session['role'] = 'user'

        flash('Registration successful! Welcome to Neighborhood Helper.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/register_user.html')

@auth_bp.route('/register/helper', methods=['GET', 'POST'])
def register_helper():
    services = query_db("SELECT * FROM services WHERE is_active = 1 ORDER BY name ASC")
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', 'Chennai').strip()
        area = request.form.get('area', '').strip()
        service_id = request.form.get('service_id')
        experience_years = request.form.get('experience_years', 1)
        hourly_rate = request.form.get('hourly_rate', 300)
        description = request.form.get('description', '').strip()

        # Validation
        if not (name and email and phone and password and confirm_password and address and area and service_id):
            flash('Please complete all mandatory fields.', 'danger')
            return render_template('auth/register_helper.html', services=services, form=request.form)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register_helper.html', services=services, form=request.form)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register_helper.html', services=services, form=request.form)

        existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Resolve coordinates from city and area
        lat, lng, display_area, resolved_city = resolve_coordinates(city=city, area=area)
        city = resolved_city
        if display_area and not area:
            area = display_area

        pwd_hash = generate_password_hash(password)

        # Insert user with role 'helper'
        user_res = execute_db("""
            INSERT INTO users (name, email, password_hash, phone, role, address, city, area, latitude, longitude, is_active)
            VALUES (%s, %s, %s, %s, 'helper', %s, %s, %s, %s, %s, 1)
        """, (name, email, pwd_hash, phone, address, city, area, lat, lng))

        user_id = user_res['last_id']

        # Insert helper record
        execute_db("""
            INSERT INTO helpers (user_id, service_id, experience_years, description, hourly_rate, availability, status, avg_rating, total_reviews)
            VALUES (%s, %s, %s, %s, %s, 'Available', 'approved', 0.00, 0)
        """, (user_id, service_id, experience_years, description, hourly_rate))

        session['user_id'] = user_id
        session['user_name'] = name
        session['email'] = email
        session['role'] = 'helper'

        flash('Helper registration complete! Your account is active and ready to accept bookings.', 'success')
        return redirect(url_for('helper.dashboard'))

    return render_template('auth/register_helper.html', services=services)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))
