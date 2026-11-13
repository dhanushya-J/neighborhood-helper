# Neighborhood Helper
> **Subtitle:** Local Services. Trusted Helpers. Simple Booking.  
> **Type:** College Mini Project (Realistic, Full-Stack Web Application)

---

## 1. Project Overview & Objectives
**Neighborhood Helper** is a human-designed, production-ready local service booking web application designed to connect neighborhood residents with trusted, nearby service technicians (e.g., plumbers, electricians, carpenters, house cleaners, painters, appliance mechanics, and tutors).

### Core Objectives:
1. **Accurate Local Discovery:** Match residents with local service providers using exact distance calculations (Haversine spherical formula) alongside customer satisfaction ratings.
2. **Strict Workflow & Payment Protection:** Enforce a reliable 8-stage lifecycle (`PENDING` &rarr; `ACCEPTED` &rarr; `IN_PROGRESS` &rarr; `COMPLETED` &rarr; `PAYMENT_PENDING` &rarr; `PAID`), guaranteeing that payments remain strictly **locked** until the technician visits, completes the work, and issues the final bill.
3. **Verified Community Ratings:** Restrict reviews to paid and completed bookings, dynamically recalculating the technician's average rating without manual manipulation.
4. **Role-Based Isolation:** Clean role segregation across **Residents (Users)**, **Service Providers (Helpers)**, and **Administrators**.

---

## 2. Technology Stack

- **Frontend:**
  - HTML5 & CSS3 (Custom, human-designed responsive design system; no bloated UI kits or heavy JS frameworks)
  - Vanilla JavaScript (Geolocation detection API, real-time bill calculations, interactive 5-star rating widget, notification toggling)
  - FontAwesome 6 icons (CDN)
- **Backend:**
  - Python 3.10+
  - Flask (REST-style routes, modular blueprints, session management, template context processors)
  - Werkzeug (Secure `scrypt` password hashing)
- **Database:**
  - MySQL 8.0 / MariaDB
  - PyMySQL (Fast, secure connection pool with parameterized queries preventing SQL injection)

---

## 3. End-to-End Demonstration Workflow

```text
USER / RESIDENT                           HELPER / TECHNICIAN
=============================             =============================
1. Log in / Register
2. Search Service (e.g., Plumber)
3. Enter Locality / Use Browser GPS
4. Sort by Rating + Distance (Haversine)
5. View Profile & Reviews
6. Book Helper (BK1001)
         │
         ▼ (Status: PENDING)
         └──────────────────────────────► 7. Receives Booking Request
                                          8. Helper Clicks [Accept]
                                                   │
                                                   ▼ (Status: ACCEPTED)
                                          9. Helper Arrives & Clicks [Start Work]
                                                   │
                                                   ▼ (Status: IN_PROGRESS)
                                                   [PAYMENT REMAINS LOCKED]
                                          10. Work Finished & Enters Bill:
                                              • Service Amount: ₹400
                                              • Spare Parts:    ₹100
                                              • Final Total:    ₹500
                                                   │
         ┌─────────────────────────────────────────┘
         ▼ (Status: PAYMENT_PENDING)
11. Payment Unlocked!
    Resident Pays ₹500
    (UPI / Card / Cash)
         │
         ▼ (Status: PAID)
12. Review Screen Unlocks
    Resident Leaves 1-5 Star
    Rating & Written Feedback
         │
         ▼
Helper Profile Rating Dynamically Updates!
```

---

## 4. Default Demo Accounts

For college presentation, live evaluation, or quick testing, use these verified pre-seeded accounts:

| Role | Email Address | Password | Profile Summary |
| :--- | :--- | :--- | :--- |
| **Resident (User)** | `user@example.com` | `User@123` | **Rahul Sharma** (Anna Nagar East) &mdash; Has active and completed bookings ready to view/pay |
| **Helper (Provider)** | `helper@example.com` | `Helper@123` | **Rajasekaran M** (Master Plumber, 8 yrs exp, 4.8★) &mdash; Has incoming requests & active jobs |
| **Administrator** | `admin@example.com` | `Admin@123` | **Suresh Kumar** &mdash; Access to full analytics, service management, and user moderation |

*Note: The login page includes quick-fill convenience buttons to load these credentials with one click during viva demonstrations.*

---

## 5. Database Schema & Architecture

The database is normalized into 7 tables with strict foreign keys:

1. **`users`**: Resident, Helper, and Admin credentials, addresses, and geographic coordinates (`latitude`, `longitude`).
2. **`services`**: Service categories (Plumbing, Electrical, Cleaning, Carpentry, Painting, Appliance Repair, Tutoring, Delivery).
3. **`helpers`**: Professional profile data (`experience_years`, `hourly_rate`, `availability`, `status`, `avg_rating`, `total_reviews`).
4. **`bookings`**: Booking requests, timestamps, problem descriptions, workflow states, and final amounts.
5. **`payments`**: Payment records, transaction reference IDs, settlement amounts, and payment methods (`UPI`, `Card`, `Cash`).
6. **`reviews`**: 1-5 star customer ratings and written feedback (strictly 1 review per booking).
7. **`notifications`**: In-app alerts for job status changes, payment updates, and review notices.

---

## 6. Installation & Setup Guide

### Prerequisites
- Python 3.10 or higher
- MySQL Server 8.0 (running on `localhost:3306`)

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd C:\Users\jeyye\.gemini\antigravity\scratch\neighborhood-helper
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Database Credentials
Edit `config.py` or set environment variables:
```python
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Your_MySQL_Password' # default in environment: Srija@17
MYSQL_DB = 'neighborhood_helper'
```

### Step 4: Initialize the Database & Seed Data
Run the automated schema and demo data generator:
```powershell
python init_db.py --force
```
This automatically creates the `neighborhood_helper` database, all 7 tables, and populates 23 realistic accounts, 8 services, 16 sample bookings, 10 payments, and 10 reviews.

### Step 5: Start the Web Application
```powershell
python app.py
```
Open your web browser and visit: **`http://127.0.0.1:5000`**

---

## 7. Project Structure

```text
neighborhood-helper/
│
├── app.py                     # Application entry point, error handlers & context processors
├── config.py                  # Database settings & Chennai locality coordinates mapping
├── init_db.py                 # Command-line database initializer runner
├── requirements.txt           # Python library requirements
├── README.md                  # Project documentation & presentation guide
│
├── database/
│   ├── db.py                  # PyMySQL connection pooling & parameterized query helpers
│   ├── schema.sql             # Table definitions with foreign keys & indexes
│   └── seed.sql               # Seed data for Chennai localities & demo accounts
│
├── routes/
│   ├── auth.py                # Login, resident registration, helper registration, logout
│   ├── user.py                # User dashboard, location-based search, helper profiles
│   ├── helper.py              # Helper dashboard, request approvals, job progress & invoicing
│   ├── booking.py             # Booking creation, timeline visualization, cancellation
│   ├── payment.py             # Payment simulation (UPI/Card/Cash) & verified review submission
│   └── admin.py               # Administrator metrics, user moderation & category management
│
├── static/
│   ├── css/
│   │   └── style.css          # Clean, human-designed responsive styling (320px - 1440px)
│   ├── js/
│   │   └── main.js            # Geolocation GPS, billing math, star ratings & notifications
│   └── images/                # Static assets & avatar placeholders
│
├── templates/
│   ├── base.html              # Core navigation, notification dropdown, and footer layout
│   ├── index.html             # Public landing page with hero, search, and service cards
│   ├── about.html             # Project background and technical description
│   ├── how_it_works.html      # 6-step lifecycle illustrated walkthrough
│   ├── 404.html & 500.html    # Friendly error handling templates
│   ├── auth/                  # Authentication templates (login, user/helper register)
│   ├── user/                  # Resident portals (dashboard, search, book, timeline, pay)
│   ├── helper/                # Provider portals (dashboard, requests, jobs, earnings)
│   └── admin/                 # Administrator console (metrics, users, helpers, services)
│
└── utils/
    ├── auth.py                # Role-based authorization & notification decorators
    └── distance.py            # Haversine distance algorithm & coordinate resolver
```

---

## 8. College Mini Project Viva Q&A Guide

1. **How is distance calculated without an external Google Maps API key?**  
   *Answer:* The application implements the **Haversine formula** (`utils/distance.py`) calculating great-circle distance between decimal degrees (latitude and longitude). If the user allows browser GPS, the HTML5 Geolocation API supplies the user's exact coordinates. If GPS is unavailable or blocked, it resolves the neighborhood locality name against a calibrated coordinates map of Chennai hubs.
2. **How does the system ensure payment security?**  
   *Answer:* A strict state machine check prevents payment during `PENDING`, `ACCEPTED`, or `IN_PROGRESS` states. The `payment_bp.checkout` route verifies that `status == 'PAYMENT_PENDING'`, which is only set when the technician explicitly marks work as completed and enters the bill amount.
3. **How does dynamic helper rating work?**  
   *Answer:* Reviews cannot be submitted until a booking status reaches `PAID`. After submission, a database trigger/query calculates `ROUND(AVG(rating), 2)` from all verified reviews belonging to that helper and stores it directly on the `helpers` table for efficient sorting.
4. **How are SQL injection vulnerabilities prevented?**  
   *Answer:* All SQL queries across `database/db.py` and routes utilize **parameterized queries** (`%s` placeholders with arguments passed as tuples to PyMySQL), ensuring user input is never concatenated directly into query strings.

---

## 9. Future Enhancements
- Integration of live SMS alerts (via Twilio or Fast2SMS)
- Integration of Razorpay live testnet webhook listeners
- Helper document upload and KYC identification verification

---
## running process 
## .\.venv\Scripts\Activate.ps1
## cd .\neighborhood-helper
## python app.py
