from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import query_db, execute_db
from utils.auth import login_required, role_required
from utils.distance import haversine, resolve_coordinates

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
@role_required('user')
def dashboard():
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if not user:
        session.clear()
        flash('Your session has expired. Please log in again.', 'info')
        return redirect(url_for('auth.login'))
    
    # Statistics (No payment metrics)
    stats = {
        'active_bookings': query_db("""
            SELECT COUNT(*) as c FROM bookings 
            WHERE user_id = %s AND status IN ('PENDING', 'ACCEPTED', 'IN_PROGRESS')
        """, (user_id,), one=True)['c'],
        'completed_bookings': query_db("""
            SELECT COUNT(*) as c FROM bookings 
            WHERE user_id = %s AND status = 'COMPLETED'
        """, (user_id,), one=True)['c'],
        'reviews_given': query_db("""
            SELECT COUNT(*) as c FROM reviews 
            WHERE user_id = %s
        """, (user_id,), one=True)['c']
    }

    # Upcoming / Active booking
    upcoming_booking = query_db("""
        SELECT b.*, s.name as service_name, s.icon as service_icon, 
               u.name as helper_name, u.phone as helper_phone, u.area as helper_area, u.city as helper_city
        FROM bookings b
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u ON h.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.user_id = %s AND b.status IN ('PENDING', 'ACCEPTED', 'IN_PROGRESS')
        ORDER BY b.booking_date ASC, b.id DESC
        LIMIT 1
    """, (user_id,), one=True)

    # Recent bookings
    recent_bookings = query_db("""
        SELECT b.*, s.name as service_name, s.icon as service_icon, 
               u.name as helper_name
        FROM bookings b
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u ON h.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
        LIMIT 5
    """, (user_id,))

    # Recently used helpers
    recent_helpers = query_db("""
        SELECT DISTINCT h.id, u.name, u.area, u.city, s.name as service_name, h.avg_rating, h.total_reviews, h.hourly_rate
        FROM bookings b
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u ON h.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE b.user_id = %s AND b.status = 'COMPLETED'
        LIMIT 4
    """, (user_id,))

    # Popular services list for quick booking
    services = query_db("SELECT * FROM services WHERE is_active = 1 LIMIT 8")

    return render_template('user/dashboard.html', 
                           user=user, 
                           stats=stats, 
                           upcoming_booking=upcoming_booking,
                           recent_bookings=recent_bookings,
                           recent_helpers=recent_helpers,
                           services=services)

@user_bp.route('/search')
def search():
    service_id = request.args.get('service_id', type=int)
    search_query = request.args.get('q', '').strip()
    city_input = request.args.get('city', '').strip()
    area_input = request.args.get('area', '').strip() or request.args.get('location', '').strip()
    radius_km = request.args.get('radius', type=float) or request.args.get('max_distance', type=float) or request.args.get('distance', type=float)
    min_rating = request.args.get('min_rating', type=float)
    availability = request.args.get('availability', '').strip()
    sort_by = request.args.get('sort', 'smart').strip() # smart, rating, distance, price

    gps_lat = request.args.get('lat', type=float)
    gps_lng = request.args.get('lng', type=float)

    # Default to user's saved city/area if logged in and no search location entered
    current_user = None
    if 'user_id' in session and session.get('role') == 'user':
        current_user = query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)
        if not city_input and not area_input and not (gps_lat and gps_lng) and current_user:
            city_input = current_user.get('city') or 'Coimbatore'
            area_input = current_user.get('area') or 'Gandhipuram'

    # Dynamic distinct cities from approved helpers in DB + core cities
    db_cities_rows = query_db("""
        SELECT DISTINCT u.city 
        FROM helpers h 
        JOIN users u ON h.user_id = u.id 
        WHERE h.status = 'approved' AND u.is_active = 1 AND u.city IS NOT NULL AND u.city != ''
        ORDER BY u.city ASC
    """)
    cities_set = {r['city'].strip().title() for r in db_cities_rows if r['city']}
    for core_city in ['Coimbatore', 'Chennai', 'Madurai']:
        cities_set.add(core_city)
    if city_input:
        cities_set.add(city_input.strip().title())
    available_cities = sorted(list(cities_set))

    # Determine reference coordinates strictly separating cities
    ref_lat, ref_lng, display_area, resolved_city = resolve_coordinates(
        city=city_input,
        area=area_input,
        user_lat=gps_lat,
        user_lng=gps_lng
    )

    # Base query for approved and active helpers in the selected city ONLY
    sql = """
        SELECT h.id as helper_id, h.experience_years, h.hourly_rate, h.availability, 
               h.avg_rating, h.total_reviews, h.description,
               u.id as user_id, u.name as helper_name, u.email, u.phone, u.area, u.city, 
               u.latitude, u.longitude, u.profile_pic,
               s.id as service_id, s.name as service_name, s.icon as service_icon, s.base_price
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE h.status = 'approved' AND u.is_active = 1
          AND LOWER(u.city) = LOWER(%s)
    """
    params = [resolved_city]

    if service_id:
        sql += " AND h.service_id = %s"
        params.append(service_id)

    if search_query:
        sql += " AND (s.name LIKE %s OR u.name LIKE %s OR h.description LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    if availability and availability.lower() != 'all':
        sql += " AND h.availability = %s"
        params.append(availability)

    if min_rating:
        sql += " AND h.avg_rating >= %s"
        params.append(min_rating)

    helpers_raw = query_db(sql, params)
    services = query_db("SELECT * FROM services WHERE is_active = 1 ORDER BY name ASC")

    # Calculate actual Haversine distance from the reference location
    results = []
    for h in helpers_raw:
        dist = haversine(ref_lat, ref_lng, h['latitude'], h['longitude'])
        h_data = dict(h)
        h_data['distance'] = dist if dist is not None else 999.0
        
        # Apply strict radius filter if requested
        if radius_km and radius_km > 0 and h_data['distance'] > radius_km:
            continue

        # Smart balance score: prioritize rating, gently penalize distance
        h_data['smart_score'] = (float(h_data['avg_rating']) * 2.0) - (h_data['distance'] / 4.0)
        results.append(h_data)

    # Sort results
    if sort_by == 'rating':
        results.sort(key=lambda x: (float(x['avg_rating']), -x['distance']), reverse=True)
    elif sort_by == 'distance':
        results.sort(key=lambda x: (x['distance'], -float(x['avg_rating'])))
    elif sort_by == 'price':
        results.sort(key=lambda x: (float(x['hourly_rate']), -float(x['avg_rating'])))
    else: # 'smart'
        results.sort(key=lambda x: x['smart_score'], reverse=True)

    SERVICE_ROLE_NAMES = {
        'Plumbing': 'Plumbers',
        'Electrical': 'Electricians',
        'Cleaning': 'Cleaners',
        'Carpentry': 'Carpenters',
        'Painting': 'Painters',
        'Appliance Repair': 'Appliance Repair Technicians',
        'Tutoring': 'Tutors',
        'Delivery Assistance': 'Delivery Assistants'
    }

    selected_service = None
    role_title = f"Helpers near {display_area}, {resolved_city}"
    
    if service_id:
        selected_service = query_db("SELECT * FROM services WHERE id = %s", (service_id,), one=True)
        if selected_service:
            role_plural = SERVICE_ROLE_NAMES.get(selected_service['name'], f"{selected_service['name']} Specialists")
            role_title = f"{role_plural} near {display_area}, {resolved_city}"
    elif search_query:
        for s in services:
            if s['name'].lower() == search_query.lower() or search_query.lower() in s['name'].lower():
                selected_service = s
                role_plural = SERVICE_ROLE_NAMES.get(s['name'], f"{s['name']} Specialists")
                role_title = f"{role_plural} near {display_area}, {resolved_city}"
                break

    return render_template('user/search.html',
                           helpers=results,
                           services=services,
                           selected_service=selected_service,
                           role_title=role_title,
                           current_service_id=service_id,
                           selected_city=resolved_city,
                           selected_area=display_area,
                           available_cities=available_cities,
                           ref_lat=ref_lat,
                           ref_lng=ref_lng,
                           radius=radius_km,
                           min_rating=min_rating,
                           availability=availability,
                           sort_by=sort_by,
                           search_query=search_query)

@user_bp.route('/helper/<int:helper_id>')
def helper_profile(helper_id):
    helper = query_db("""
        SELECT h.*, u.name as helper_name, u.email, u.phone, u.area, u.city, 
               u.latitude, u.longitude, u.profile_pic,
               s.name as service_name, s.icon as service_icon, s.base_price
        FROM helpers h
        JOIN users u ON h.user_id = u.id
        JOIN services s ON h.service_id = s.id
        WHERE h.id = %s AND h.status = 'approved' AND u.is_active = 1
    """, (helper_id,), one=True)

    if not helper:
        flash('Helper not found or profile is currently inactive.', 'warning')
        return redirect(url_for('user.search'))

    # Calculate distance if user location is available
    distance = None
    if 'user_id' in session:
        cur_user = query_db("SELECT latitude, longitude FROM users WHERE id = %s", (session['user_id'],), one=True)
        if cur_user:
            distance = haversine(cur_user['latitude'], cur_user['longitude'], helper['latitude'], helper['longitude'])

    # Fetch helper reviews
    reviews = query_db("""
        SELECT r.*, u.name as reviewer_name, u.area as reviewer_area, u.city as reviewer_city
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.helper_id = %s
        ORDER BY r.created_at DESC
    """, (helper_id,))

    return render_template('user/helper_profile.html', helper=helper, distance=distance, reviews=reviews)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('user')
def profile():
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', 'Coimbatore').strip()
        area = request.form.get('area', '').strip()

        if not (name and phone and address and area):
            flash('Name, phone, address, and area are required.', 'danger')
        else:
            lat, lng, _, _ = resolve_coordinates(city, area)
            execute_db("""
                UPDATE users 
                SET name = %s, phone = %s, address = %s, city = %s, area = %s, latitude = %s, longitude = %s
                WHERE id = %s
            """, (name, phone, address, city, area, lat, lng, user_id))
            
            session['user_name'] = name
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.profile'))

    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    return render_template('user/profile.html', user=user)

@user_bp.route('/reviews')
@login_required
@role_required('user')
def my_reviews():
    user_id = session['user_id']
    reviews = query_db("""
        SELECT r.*, u.name as helper_name, s.name as service_name, b.booking_code
        FROM reviews r
        JOIN bookings b ON r.booking_id = b.id
        JOIN helpers h ON b.helper_id = h.id
        JOIN users u ON h.user_id = u.id
        JOIN services s ON b.service_id = s.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    """, (user_id,))
    return render_template('user/reviews.html', reviews=reviews)
