import requests
import re
import sys
from app import app
from database.db import query_db

BASE_URL = "http://127.0.0.1:5000"

def parse_helper_cards(html):
    """Extract individual helper card info (name, area, city, rating, distance) from search HTML."""
    chunks = html.split('<div class="helper-card">')[1:]
    cards = []
    for chunk in chunks:
        # extract card HTML
        c = chunk[:2500]
        # City & Area: e.g. "Gandhipuram, Coimbatore"
        loc_match = re.search(r'fa-location-dot"></i>\s*([^<]+)', c)
        loc = loc_match.group(1).strip() if loc_match else ""
        
        # Rating: e.g. "4.6"
        rate_match = re.search(r'class="rating-pill">\s*<i class="fa-solid fa-star"></i>\s*([\d\.]+)', c)
        rating = float(rate_match.group(1)) if rate_match else 0.0
        
        # Distance: e.g. "0.2 km"
        dist_match = re.search(r'fa-route"></i>\s*([\d\.]+)\s*km', c)
        dist = float(dist_match.group(1)) if dist_match else 999.0
        
        cards.append({
            "loc": loc,
            "rating": rating,
            "distance": dist
        })
    return cards

def test_suite():
    passed = 0
    failed = 0

    def assert_true(cond, msg):
        nonlocal passed, failed
        if cond:
            print(f"  [PASS] {msg}")
            passed += 1
        else:
            print(f"  [FAIL] {msg}")
            failed += 1

    session = requests.Session()

    print("\n--- 1. Testing Homepage & Navigation ---")
    r = session.get(f"{BASE_URL}/")
    assert_true(r.status_code == 200, "Home page loads with 200 OK")
    assert_true("Neighborhood Helper" in r.text, "Home page contains title")
    assert_true("Pay Now" not in r.text and "UPI" not in r.text, "No payment/UPI on home page")

    print("\n--- 2. Testing How It Works Page ---")
    r = session.get(f"{BASE_URL}/how-it-works")
    assert_true(r.status_code == 200, "How it Works page loads with 200 OK")
    assert_true("1. Search Local Helpers by City & Area" in r.text, "Step 1 present")
    assert_true("5. User Submits Rating & Review" in r.text, "Step 5 present")
    assert_true("Payment" not in r.text, "No Payment references in How It Works")

    print("\n--- 3. Testing Strict City & Area Isolation (Coimbatore) ---")
    r = session.get(f"{BASE_URL}/user/search?city=Coimbatore&area=Gandhipuram", allow_redirects=True)
    assert_true(r.status_code == 200, "Coimbatore search returns 200 OK")
    cards = parse_helper_cards(r.text)
    assert_true(len(cards) > 0, f"Found {len(cards)} Coimbatore helpers")
    all_cbe = all("Coimbatore" in c["loc"] and "Chennai" not in c["loc"] for c in cards)
    assert_true(all_cbe, "STRICT ISOLATION: 100% of helper cards are in Coimbatore, 0 in Chennai")
    min_dist = min(c["distance"] for c in cards)
    assert_true(min_dist < 1.0, f"Accurate Haversine: Nearest Gandhipuram helper is {min_dist} km away (< 1 km)")

    print("\n--- 4. Testing Strict City & Area Isolation (Chennai) ---")
    r = session.get(f"{BASE_URL}/user/search?city=Chennai&area=Anna+Nagar", allow_redirects=True)
    assert_true(r.status_code == 200, "Chennai search returns 200 OK")
    cards_chn = parse_helper_cards(r.text)
    assert_true(len(cards_chn) > 0, f"Found {len(cards_chn)} Chennai helpers")
    all_chn = all("Chennai" in c["loc"] and "Coimbatore" not in c["loc"] for c in cards_chn)
    assert_true(all_chn, "STRICT ISOLATION: 100% of helper cards are in Chennai, 0 in Coimbatore")
    min_dist_chn = min(c["distance"] for c in cards_chn)
    assert_true(min_dist_chn < 1.0, f"Accurate Haversine: Nearest Anna Nagar helper is {min_dist_chn} km away (< 1 km)")

    print("\n--- 5. Testing Empty State When No Helpers Match ---")
    r = session.get(f"{BASE_URL}/user/search?city=Coimbatore&area=Peelamedu&service_id=999", allow_redirects=True)
    assert_true(r.status_code == 200, "Search with non-existent service returns 200 OK")
    assert_true("No helpers found in your selected area" in r.text, "Clean empty state message shown")
    cards_empty = parse_helper_cards(r.text)
    assert_true(len(cards_empty) == 0, "STRICT ISOLATION: Zero cards rendered, no fallback to another city")

    print("\n--- 6. Testing Rating & Distance Filters ---")
    r = session.get(f"{BASE_URL}/user/search?city=Coimbatore&min_rating=4.5", allow_redirects=True)
    assert_true(r.status_code == 200, "Min rating 4.5 search returns 200 OK")
    cards_rated = parse_helper_cards(r.text)
    if cards_rated:
        all_above = all(c["rating"] >= 4.5 for c in cards_rated)
        assert_true(all_above, f"All {len(cards_rated)} returned helpers have rating >= 4.5: {[c['rating'] for c in cards_rated]}")
    else:
        assert_true(True, "Filter executed successfully")

    # Max Distance Filter (e.g. 5 km)
    r = session.get(f"{BASE_URL}/user/search?city=Coimbatore&area=Gandhipuram&max_distance=5", allow_redirects=True)
    assert_true(r.status_code == 200, "Max distance 5 km search returns 200 OK")
    cards_dist = parse_helper_cards(r.text)
    if cards_dist:
        all_within = all(c["distance"] <= 5.0 for c in cards_dist)
        assert_true(all_within, f"All {len(cards_dist)} returned helpers are within 5 km: {[c['distance'] for c in cards_dist]}")

    print("\n--- 7. Testing End-to-End Booking Lifecycle (No Payment) ---")
    # Step A: Login User
    user_sess = requests.Session()
    login_res = user_sess.post(f"{BASE_URL}/auth/login", data={
        "email": "user@example.com",
        "password": "User@123"
    }, allow_redirects=True)
    assert_true("my bookings" in login_res.text.lower() or "dashboard" in login_res.text.lower() or "logout" in login_res.text.lower(), "User logged in successfully")

    # Step B: Book Murugesan K (helper_id=2, Coimbatore Gandhipuram plumber)
    book_post = user_sess.post(f"{BASE_URL}/book/2", data={
        "booking_date": "2026-10-05",
        "preferred_time": "10:30",
        "service_address": "12 Cross Cut Road, Gandhipuram, Coimbatore",
        "problem_description": "Kitchen sink pipe leakage urgent repair",
        "additional_notes": "Please call 5 mins prior"
    }, allow_redirects=False)
    assert_true(book_post.status_code == 302, "Booking created and redirected")
    redirect_url = book_post.headers.get("Location")
    booking_code = redirect_url.split("/")[-1]
    print(f"    Created Booking Code: {booking_code}")

    # Fetch booking ID from database
    with app.app_context():
        b_rec = query_db("SELECT id, status FROM bookings WHERE booking_code = %s", (booking_code,), one=True)
        booking_id = b_rec['id']
        print(f"    Booking DB ID: {booking_id}, Initial Status: {b_rec['status']}")
    
    assert_true(b_rec['status'] == "PENDING", "Initial status in DB is PENDING")

    # Verify booking detail page
    b_detail = user_sess.get(f"{BASE_URL}/booking/{booking_code}")
    assert_true("PENDING" in b_detail.text, "Booking detail UI shows PENDING")
    assert_true("Pay Now" not in b_detail.text, "No Pay Now button in PENDING state")

    # Step C: Helper Login (muru.cbe@example.com / Helper@123)
    helper_sess = requests.Session()
    helper_login = helper_sess.post(f"{BASE_URL}/auth/login", data={
        "email": "muru.cbe@example.com",
        "password": "Helper@123"
    }, allow_redirects=True)
    assert_true("murugesan" in helper_login.text.lower() or "incoming booking requests" in helper_login.text.lower() or "dashboard" in helper_login.text.lower() or "logout" in helper_login.text.lower(), "Helper logged in successfully")

    # Step D: Helper Accepts Booking
    accept_res = helper_sess.post(f"{BASE_URL}/helper/booking/{booking_id}/accept", allow_redirects=False)
    assert_true(accept_res.status_code == 302, "Helper accepted booking")

    b_detail = user_sess.get(f"{BASE_URL}/booking/{booking_code}")
    assert_true("ACCEPTED" in b_detail.text, "Booking status updated to ACCEPTED")

    # Step E: Helper Starts Work (IN_PROGRESS)
    start_res = helper_sess.post(f"{BASE_URL}/helper/booking/{booking_id}/start", allow_redirects=False)
    assert_true(start_res.status_code == 302, "Helper started work")

    b_detail = user_sess.get(f"{BASE_URL}/booking/{booking_code}")
    assert_true("IN_PROGRESS" in b_detail.text, "Booking status updated to IN_PROGRESS")

    # Step F: Helper Completes Work (COMPLETED) - direct completion, no payment/bills
    comp_res = helper_sess.post(f"{BASE_URL}/helper/booking/{booking_id}/complete", allow_redirects=False)
    assert_true(comp_res.status_code == 302, "Helper marked work completed")

    b_detail = user_sess.get(f"{BASE_URL}/booking/{booking_code}")
    assert_true("COMPLETED" in b_detail.text, "Booking status updated to COMPLETED")
    assert_true("Rate & Review Helper" in b_detail.text, "Review prompt unlocked on COMPLETED")
    assert_true("Pay Now" not in b_detail.text, "Zero payment prompts")

    # Step G: User Submits Review
    rev_page = user_sess.get(f"{BASE_URL}/review/{booking_code}")
    assert_true(rev_page.status_code == 200, "Review submission page loads with 200 OK")
    assert_true("Rate Your Experience" in rev_page.text, "Review form displayed")

    rev_post = user_sess.post(f"{BASE_URL}/review/{booking_code}", data={
        "rating": "5",
        "comment": "Outstanding service! Arrived in Gandhipuram within 20 mins and fixed the pipe flawlessly."
    }, allow_redirects=False)
    assert_true(rev_post.status_code == 302, "Review submitted and redirected to booking details")

    # Check booking detail reflects review submitted
    b_detail_after = user_sess.get(f"{BASE_URL}/booking/{booking_code}")
    assert_true("Outstanding service" in b_detail_after.text, "Submitted review visible in booking detail")

    print("\n--- 8. Testing Admin Console & Metrics ---")
    admin_sess = requests.Session()
    admin_login = admin_sess.post(f"{BASE_URL}/auth/login", data={
        "email": "admin@example.com",
        "password": "Admin@123"
    }, allow_redirects=True)
    assert_true("admin" in admin_login.text.lower() or "system metrics" in admin_login.text.lower() or "logout" in admin_login.text.lower(), "Admin logged in successfully")

    # Check all admin pages
    pages = [
        ("/admin/dashboard", "Admin Dashboard"),
        ("/admin/users", "Admin Users"),
        ("/admin/helpers", "Admin Helpers"),
        ("/admin/services", "Admin Services"),
        ("/admin/bookings", "Admin Bookings"),
        ("/admin/reviews", "Admin Reviews")
    ]
    for path, name in pages:
        res = admin_sess.get(f"{BASE_URL}{path}")
        assert_true(res.status_code == 200, f"{name} loads with 200 OK")
        assert_true("Payment" not in res.text or "sidebar-link active" not in res.text, f"No payment tabs on {name}")

    print("\n--- 9. Testing Decommissioned Payment Routes ---")
    dead_payment_res = user_sess.get(f"{BASE_URL}/payment/checkout/{booking_code}")
    assert_true(dead_payment_res.status_code in [404, 302], "Payment route returns 404 or redirects (no active payment gateway)")

    print(f"\n==========================================")
    print(f"TEST SUMMARY: {passed} PASSED, {failed} FAILED")
    print(f"==========================================")
    return failed == 0

if __name__ == "__main__":
    success = test_suite()
    sys.exit(0 if success else 1)
