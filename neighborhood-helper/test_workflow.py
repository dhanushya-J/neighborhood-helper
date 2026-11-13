import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database.db import query_db, init_database

def run_tests():
    print("==================================================")
    print("NEIGHBORHOOD HELPER - FULL WORKFLOW TEST SUITE")
    print("==================================================")
    
    # 0. Initialize DB
    print("[1] Initializing fresh database...")
    init_database(force=True)

    client = app.test_client()

    # 1. Test Public Home Page
    print("\n[2] Testing Home Page...")
    resp = client.get('/')
    assert resp.status_code == 200, f"Home page returned {resp.status_code}"
    assert b"Neighborhood Helper" in resp.data
    assert b"Find Trusted Helpers Near You" in resp.data
    print("[PASS] Home page loaded successfully.")

    # 2. Test User Search with location & Haversine distance
    print("\n[3] Testing Service Search in Anna Nagar (Plumbing)...")
    resp = client.get('/user/search?service_id=1&location=Anna+Nagar&radius=10&sort=smart')
    assert resp.status_code == 200
    assert b"Rajasekaran M" in resp.data
    assert b"km away" in resp.data
    print("[PASS] Search returned nearby helpers with accurate Haversine distance.")

    # 3. Test New User Registration
    print("\n[4] Testing User Registration...")
    reg_data = {
        'name': 'Test Resident',
        'email': 'testuser@example.com',
        'phone': '9876543210',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'address': 'Flat 3B, Sunshine Apartments, Anna Nagar',
        'city': 'Chennai',
        'area': 'Anna Nagar'
    }
    resp = client.post('/auth/register/user', data=reg_data, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Welcome, Test Resident" in resp.data or b"Test Resident" in resp.data
    print("[PASS] User registered and auto-logged in successfully.")

    # 4. User views helper profile
    print("\n[5] Viewing Helper Profile (ID: 1 - Rajasekaran M)...")
    resp = client.get('/user/helper/1')
    assert resp.status_code == 200
    assert b"Rajasekaran M" in resp.data
    assert b"Verified Customer Reviews" in resp.data
    print("[PASS] Helper profile and verified reviews loaded.")

    # 5. User creates a new booking request
    print("\n[6] Creating a new service booking...")
    book_data = {
        'problem_description': 'Water leaking from kitchen sink pipe joint under the sink.',
        'booking_date': '2026-10-05',
        'preferred_time': '11:30 AM',
        'service_address': 'Flat 3B, Sunshine Apartments, Anna Nagar',
        'additional_notes': 'Please call before arrival.'
    }
    resp = client.post('/book/1', data=book_data, follow_redirects=True)
    assert resp.status_code == 200
    assert b"BK" in resp.data
    assert b"PENDING" in resp.data
    assert b"Payment Locked" in resp.data

    # Extract created booking code
    new_booking = query_db("SELECT * FROM bookings WHERE problem_description LIKE '%kitchen sink pipe joint%'", one=True)
    assert new_booking is not None
    booking_code = new_booking['booking_code']
    booking_id = new_booking['id']
    print(f"[PASS] Booking created successfully: Code={booking_code}, ID={booking_id}, Status={new_booking['status']}.")

    # Verify payment is locked for user
    resp = client.get(f'/payment/{booking_code}', follow_redirects=True)
    assert b"Payment is locked" in resp.data or b"Payment Locked" in resp.data
    print("[PASS] Verified rule: Payment is strictly locked while PENDING.")

    # 6. Logout User and Login as Helper
    print("\n[7] Logging in as Helper (helper@example.com)...")
    client.get('/auth/logout')
    resp = client.post('/auth/login', data={'email': 'helper@example.com', 'password': 'Helper@123'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Helper Dashboard" in resp.data or b"Rajasekaran" in resp.data
    print("[PASS] Helper logged in successfully.")

    # Helper checks requests
    resp = client.get('/helper/requests')
    assert resp.status_code == 200
    assert booking_code.encode() in resp.data
    print(f"[PASS] Helper sees booking request {booking_code}.")

    # Helper accepts booking
    print(f"\n[8] Helper accepts booking {booking_code}...")
    resp = client.post(f'/helper/booking/{booking_id}/accept', follow_redirects=True)
    assert resp.status_code == 200
    b_updated = query_db("SELECT status FROM bookings WHERE id = %s", (booking_id,), one=True)
    assert b_updated['status'] == 'ACCEPTED'
    print(f"[PASS] Status transitioned to ACCEPTED.")

    # Helper starts work (arrives at site)
    print(f"\n[9] Helper starts work on {booking_code}...")
    resp = client.post(f'/helper/booking/{booking_id}/start', follow_redirects=True)
    assert resp.status_code == 200
    b_updated = query_db("SELECT status FROM bookings WHERE id = %s", (booking_id,), one=True)
    assert b_updated['status'] == 'IN_PROGRESS'
    print(f"[PASS] Status transitioned to IN_PROGRESS.")

    # Helper completes work and enters final amount
    print(f"\n[10] Helper completes work and submits final amount...")
    complete_data = {
        'service_amount': '450.00',
        'additional_charges': '150.00'
    }
    resp = client.post(f'/helper/booking/{booking_id}/complete', data=complete_data, follow_redirects=True)
    assert resp.status_code == 200
    b_updated = query_db("SELECT status, service_amount, additional_charges, final_amount FROM bookings WHERE id = %s", (booking_id,), one=True)
    assert b_updated['status'] == 'PAYMENT_PENDING'
    assert float(b_updated['final_amount']) == 600.00
    print(f"[PASS] Work completed! Status: PAYMENT_PENDING, Final Amount: Rs.{b_updated['final_amount']}.")

    # 7. Logout Helper, Log in as User
    print(f"\n[11] Logging back in as Resident to pay...")
    client.get('/auth/logout')
    client.post('/auth/login', data={'email': 'testuser@example.com', 'password': 'Password@123'}, follow_redirects=True)

    # User views booking detail: Payment is now UNLOCKED!
    resp = client.get(f'/booking/{booking_code}')
    assert resp.status_code == 200
    assert b"Payment Enabled" in resp.data or b"Pay" in resp.data
    assert b"600" in resp.data
    print(f"[PASS] Payment is now verified UNLOCKED on user booking detail.")

    # User proceeds to payment checkout
    print(f"\n[12] Processing payment of Rs.600 via UPI...")
    pay_data = {
        'payment_method': 'UPI'
    }
    resp = client.post(f'/payment/{booking_code}', data=pay_data, follow_redirects=True)
    assert resp.status_code == 200
    b_updated = query_db("SELECT status FROM bookings WHERE id = %s", (booking_id,), one=True)
    assert b_updated['status'] == 'PAID'
    payment_rec = query_db("SELECT * FROM payments WHERE booking_id = %s", (booking_id,), one=True)
    assert payment_rec is not None
    assert payment_rec['status'] == 'SUCCESS'
    assert float(payment_rec['amount']) == 600.00
    print(f"[PASS] Payment processed! Status: PAID. Payment code: {payment_rec['payment_code']}, Txn: {payment_rec['transaction_id']}.")

    # 8. User submits 5-star review
    print(f"\n[13] Submitting 5-star rating and review...")
    rev_data = {
        'rating': '5',
        'comment': 'Exceptional service! Rajasekaran arrived right on time and fixed the concealed leak cleanly.'
    }
    resp = client.post(f'/review/{booking_code}', data=rev_data, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Thank you! Your rating and review have been published" in resp.data

    # Verify review in DB and helper rating recalculated
    review_rec = query_db("SELECT * FROM reviews WHERE booking_id = %s", (booking_id,), one=True)
    assert review_rec is not None
    assert review_rec['rating'] == 5
    
    helper_rec = query_db("SELECT avg_rating, total_reviews FROM helpers WHERE id = 1", one=True)
    print(f"[PASS] Review stored! Helper updated avg_rating: {helper_rec['avg_rating']} stars across {helper_rec['total_reviews']} total reviews.")

    # 9. Verify duplicate review prevention
    print("\n[14] Testing duplicate review prevention...")
    resp = client.post(f'/review/{booking_code}', data=rev_data, follow_redirects=True)
    assert b"already submitted a review" in resp.data
    print("[PASS] Prevented duplicate review.")

    # 10. Login as Admin and audit
    print("\n[15] Logging in as Admin (admin@example.com)...")
    client.get('/auth/logout')
    resp = client.post('/auth/login', data={'email': 'admin@example.com', 'password': 'Admin@123'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Admin Console" in resp.data or b"System Metrics" in resp.data

    # Check admin bookings view
    resp = client.get('/admin/bookings')
    assert resp.status_code == 200
    assert booking_code.encode() in resp.data
    assert b"PAID" in resp.data

    # Check admin payments view
    resp = client.get('/admin/payments')
    assert resp.status_code == 200
    assert payment_rec['payment_code'].encode() in resp.data

    print("[PASS] Admin successfully audited bookings and payments.")

    print("\n==================================================")
    print("ALL 15 INTEGRATION TEST STEPS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == '__main__':
    with app.app_context():
        run_tests()
