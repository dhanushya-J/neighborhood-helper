-- Neighborhood Helper Seed / Demo Data
-- Realistic Chennai localities and verified demo accounts

USE neighborhood_helper;

-- 1. Insert Services
INSERT INTO services (id, name, icon, description, base_price, is_active) VALUES
(1, 'Plumbing', 'wrench', 'Pipe repairs, faucet fittings, leak detection, bathroom fixtures and drainage clearing.', 300.00, 1),
(2, 'Electrical', 'zap', 'Switch repairs, wiring, fan installations, MCB issues, lighting and fuse repairs.', 350.00, 1),
(3, 'Cleaning', 'sparkles', 'Deep house cleaning, kitchen scrubbing, bathroom sanitation and post-event cleanup.', 400.00, 1),
(4, 'Carpentry', 'hammer', 'Furniture assembly, door latch fixes, custom shelving, hinges and cabinet repairs.', 450.00, 1),
(5, 'Painting', 'paint-brush', 'Interior wall touch-ups, door varnishing, waterproof painting and full room coatings.', 500.00, 1),
(6, 'Appliance Repair', 'tv', 'Washing machine, refrigerator, microwave oven, AC service and mixer grinder fixes.', 400.00, 1),
(7, 'Tutoring', 'book-open', 'School mathematics, science coaching, programming basics and English communication.', 350.00, 1),
(8, 'Delivery Assistance', 'truck', 'Grocery pickup, package courier transport, local errand runs and shifting help.', 200.00, 1);

-- 2. Insert Users (Customers, Helpers, Admin)
-- Passwords:
-- user@example.com -> User@123
-- helper@example.com -> Helper@123
-- admin@example.com -> Admin@123
-- All other test users and helpers use User@123 or Helper@123

INSERT INTO users (id, name, email, password_hash, phone, role, address, city, area, latitude, longitude, profile_pic, is_active) VALUES
-- Admin (ID: 1)
(1, 'Suresh Kumar', 'admin@example.com', 'scrypt:32768:8:1$l8D4zXiY5WPwQFlZ$3be72727c8f4424e3c209942a2d2a8256f42596c634364177cdd780fc6dfc3ab0bb4f47898f3ff5d2b223f9a7a07b74e361495739ff42ef793ff833138c62729', '9840123456', 'admin', 'Plot 45, Nungambakkam High Rd', 'Chennai', 'Nungambakkam', 13.0569, 80.2425, 'admin_avatar.png', 1),

-- Customers (IDs: 2 - 11)
(2, 'Rahul Sharma', 'user@example.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9841029384', 'user', '12, 3rd Avenue, Anna Nagar East', 'Chennai', 'Anna Nagar', 13.0850, 80.2101, 'avatar_rahul.png', 1),
(3, 'Priya Sundaram', 'priya.s@gmail.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9789123401', 'user', '45, 100 Feet Bypass Rd, Velachery', 'Chennai', 'Velachery', 12.9815, 80.2180, 'avatar_priya.png', 1),
(4, 'Karthik Raman', 'karthik.r@outlook.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9444109823', 'user', '88, Gandhi Nagar 1st Main, Adyar', 'Chennai', 'Adyar', 13.0012, 80.2565, 'avatar_karthik.png', 1),
(5, 'Ananya Iyer', 'ananya.iyer@yahoo.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9884561234', 'user', '15, GST Road, West Tambaram', 'Chennai', 'Tambaram', 12.9249, 80.1000, 'avatar_ananya.png', 1),
(6, 'Saravanan K', 'saravanan.k@gmail.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9790812345', 'user', '24, Mount Poonamallee High Rd, Porur', 'Chennai', 'Porur', 13.0382, 80.1565, 'avatar_saravanan.png', 1),
(7, 'Divya Balaji', 'divya.b@hotmail.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9840998877', 'user', '71, Race Course Colony, Guindy', 'Chennai', 'Guindy', 13.0067, 80.2025, 'avatar_divya.png', 1),
(8, 'Vignesh Natarajan', 'vignesh.n@gmail.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9600123987', 'user', '33, Nolambur Main Rd, Mogappair West', 'Chennai', 'Mogappair', 13.0837, 80.1755, 'avatar_vignesh.png', 1),
(9, 'Meera Krishnan', 'meera.k@gmail.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9841887766', 'user', '5, Usman Road, T. Nagar', 'Chennai', 'T. Nagar', 13.0418, 80.2341, 'avatar_meera.png', 1),
(10, 'Arvind Swaminathan', 'arvind.s@outlook.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9789012344', 'user', '19, North Mada Street, Mylapore', 'Chennai', 'Mylapore', 13.0368, 80.2676, 'avatar_arvind.png', 1),
(11, 'Deepa Venkatesh', 'deepa.v@gmail.com', 'scrypt:32768:8:1$CWG1fs5JJDB9d93p$3f14106fee02b0d01f3c77317939989dcee9815921505df74c107bb2caf6ef88955138dcabfe12c3f086f8fbff93ed5ae102afaf58ff5c0915bddf31b6544b23', '9444332211', 'user', '52, Ormes Road, Kilpauk', 'Chennai', 'Kilpauk', 13.0784, 80.2407, 'avatar_deepa.png', 1),

-- Helpers User Accounts (IDs: 12 - 23)
-- Helper 1 (Default demo helper)
(12, 'Rajasekaran M', 'helper@example.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9840192837', 'helper', '54, 2nd Main Rd, Anna Nagar West', 'Chennai', 'Anna Nagar', 13.0870, 80.2120, 'helper_raja.png', 1),
-- Helper 2
(13, 'Kumaravel P', 'kumaravel.p@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9841234567', 'helper', '18, Garden Street, Kilpauk', 'Chennai', 'Kilpauk', 13.0790, 80.2390, 'helper_kumar.png', 1),
-- Helper 3
(14, 'Arun Prakash', 'arun.p@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9789345678', 'helper', '8, Golden George Nagar, Mogappair', 'Chennai', 'Mogappair', 13.0850, 80.1720, 'helper_arun.png', 1),
-- Helper 4
(15, 'Manikandan S', 'mani.electric@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9444567890', 'helper', '22, C-Block, Anna Nagar East', 'Chennai', 'Anna Nagar', 13.0830, 80.2080, 'helper_mani.png', 1),
-- Helper 5
(16, 'Selvam R', 'selvam.r@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9884123890', 'helper', '39, South Boag Rd, T. Nagar', 'Chennai', 'T. Nagar', 13.0400, 80.2320, 'helper_selvam.png', 1),
-- Helper 6
(17, 'Lakshmi Narayanan', 'lakshmi.clean@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9790234567', 'helper', '14, Canal Bank Rd, Adyar', 'Chennai', 'Adyar', 13.0020, 80.2550, 'helper_lakshmi.png', 1),
-- Helper 7
(18, 'Murugan T', 'murugan.wood@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9600987654', 'helper', '9, Kundrathur Main Rd, Porur', 'Chennai', 'Porur', 13.0350, 80.1540, 'helper_murugan.png', 1),
-- Helper 8
(19, 'Dinesh Babu', 'dinesh.paints@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9840876543', 'helper', '28, Taramani Link Rd, Velachery', 'Chennai', 'Velachery', 12.9800, 80.2150, 'helper_dinesh.png', 1),
-- Helper 9
(20, 'Ramesh G', 'ramesh.repairs@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9789654321', 'helper', '62, Kathipara Junction, Guindy', 'Chennai', 'Guindy', 13.0050, 80.2010, 'helper_ramesh.png', 1),
-- Helper 10
(21, 'Sangeetha R', 'sangeetha.maths@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9444765432', 'helper', '11, Roundtana, Anna Nagar', 'Chennai', 'Anna Nagar', 13.0860, 80.2130, 'helper_sangeetha.png', 1),
-- Helper 11
(22, 'Vijay Anand', 'vijay.express@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9884543210', 'helper', '3, Sanatorium Station Rd, Tambaram', 'Chennai', 'Tambaram', 12.9230, 80.0980, 'helper_vijay.png', 1),
-- Helper 12
(23, 'Prakash K', 'prakash.cleaning@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9790654321', 'helper', '19, Shanthi Colony, Anna Nagar', 'Chennai', 'Anna Nagar', 13.0845, 80.2090, 'helper_prakash.png', 1),
-- Helper 13 (Painter in Anna Nagar)
(24, 'Senthil Nathan', 'senthil.paints@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9840912345', 'helper', '14, 5th Avenue, Anna Nagar East', 'Chennai', 'Anna Nagar', 13.0860, 80.2110, 'helper_senthil.png', 1),
-- Helper 14 (Carpenter in Anna Nagar)
(25, 'Ganesan V', 'ganesan.wood@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9884129876', 'helper', '7, 4th Main Road, Anna Nagar West', 'Chennai', 'Anna Nagar', 13.0840, 80.2095, 'helper_ganesan.png', 1),
-- Helper 15 (Appliance Repair in Anna Nagar)
(26, 'Kumaresh M', 'kumaresh.repairs@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9790123987', 'helper', '29, 2nd Avenue, Anna Nagar', 'Chennai', 'Anna Nagar', 13.0855, 80.2105, 'helper_kumaresh.png', 1),
-- Helper 16 (Delivery in Anna Nagar)
(27, 'Deepan S', 'deepan.delivery@gmail.com', 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233', '9600123456', 'helper', '41, 1st Cross Street, Anna Nagar East', 'Chennai', 'Anna Nagar', 13.0835, 80.2085, 'helper_deepan.png', 1);

-- 3. Insert Helper Profiles
INSERT INTO helpers (id, user_id, service_id, experience_years, description, hourly_rate, availability, status, avg_rating, total_reviews) VALUES
-- Helper 1: Rajasekaran M (Plumber, Anna Nagar)
(1, 12, 1, 8, 'Certified master plumber with 8+ years experience in CPVC/PVC piping, sanitary fittings, tank cleaning, and leak troubleshooting. Rapid response across Anna Nagar and surrounding neighborhoods.', 350.00, 'Available', 'approved', 4.80, 5),
-- Helper 2: Kumaravel P (Plumber, Kilpauk)
(2, 13, 1, 5, 'Specialist in bathroom repairs, mixer tap replacements, concealed pipe blockages and water heater line connections. Honest rates and guaranteed quality work.', 300.00, 'Available', 'approved', 4.50, 3),
-- Helper 3: Arun Prakash (Plumber, Mogappair)
(3, 14, 1, 3, 'General plumbing technician for residential apartments. Faucet replacements, pipe leak fixing, flush tank repairs and kitchen sink servicing.', 250.00, 'Available', 'approved', 4.20, 2),
-- Helper 4: Manikandan S (Electrician, Anna Nagar)
(4, 15, 2, 7, 'Government licensed electrical contractor. Safe and precise troubleshooting for power trippings, switchboard replacements, ceiling fan installations, and inverter hookups.', 400.00, 'Available', 'approved', 4.90, 4),
-- Helper 5: Selvam R (Electrician, T. Nagar)
(5, 16, 2, 6, 'Reliable residential electrician. Expert in rewiring, LED panel lighting setup, geyser wiring, and smart switch installations.', 380.00, 'Available', 'approved', 4.60, 3),
-- Helper 6: Lakshmi Narayanan (Cleaning, Adyar)
(6, 17, 3, 4, 'Professional deep-cleaning specialist using industrial non-toxic cleaning agents. Sanitizes kitchens, washrooms, balconies and high-touch areas.', 320.00, 'Available', 'approved', 4.70, 3),
-- Helper 7: Murugan T (Carpenter, Porur)
(7, 18, 4, 10, 'Expert woodworker with 10 years experience in modular furniture, custom wooden partitions, lock repairs, door alignment, and veneer restoration.', 450.00, 'Available', 'approved', 4.85, 4),
-- Helper 8: Dinesh Babu (Painter, Velachery)
(8, 19, 5, 5, 'Professional house painter with expertise in Asian Paints Royale finishes, damp-proof treatments, stencil walls, and door polish work.', 350.00, 'Available', 'approved', 4.40, 2),
-- Helper 9: Ramesh G (Appliance Repair, Guindy)
(9, 20, 6, 8, 'Factory trained technician for Samsung, LG, IFB and Whirlpool appliances. Refrigerators, front-load washers, and microwave servicing.', 400.00, 'Available', 'approved', 4.75, 4),
-- Helper 10: Sangeetha R (Tutoring, Anna Nagar)
(10, 21, 7, 6, 'M.Sc Mathematics graduate providing personalized coaching for CBSE/State Board 6th to 12th standards. Clear concepts and patient mentorship.', 300.00, 'Available', 'approved', 4.90, 3),
-- Helper 11: Vijay Anand (Delivery, Tambaram)
(11, 22, 8, 2, 'Punctual local runner with two-wheeler for medicine pickup, urgent documents delivery, grocery shopping and neighborhood parcels.', 200.00, 'Available', 'approved', 4.60, 2),
-- Helper 12: Prakash K (Cleaning, Anna Nagar)
(12, 23, 3, 3, 'Eco-friendly residential and office space cleaning. Floor buffing, window pane scrubbing and kitchen tile cleaning.', 280.00, 'Available', 'approved', 4.30, 2),
-- Helper 13: Senthil Nathan (Painter, Anna Nagar)
(13, 24, 5, 6, 'Skilled interior and exterior wall painter with 6 years experience across Anna Nagar and Kilpauk. Specialist in emulsion roller finishes, waterproof coatings, and wood door polishing.', 350.00, 'Available', 'approved', 4.80, 4),
-- Helper 14: Ganesan V (Carpenter, Anna Nagar)
(14, 25, 4, 8, 'Master carpenter for customized wooden shelves, cupboard repairs, door lock installations, and modular kitchen hardware adjustments.', 420.00, 'Available', 'approved', 4.70, 3),
-- Helper 15: Kumaresh M (Appliance Repair, Anna Nagar)
(15, 26, 6, 7, 'Prompt technician for refrigerators, washing machines, microwaves, and air conditioner gas charging and tune-up services in Anna Nagar.', 380.00, 'Available', 'approved', 4.90, 5),
-- Helper 16: Deepan S (Delivery, Anna Nagar)
(16, 27, 8, 3, 'Reliable local courier and errand assistant for pharmacy pickups, urgent parcel transport, and neighborhood supplies delivery.', 200.00, 'Available', 'approved', 4.60, 3);

-- 4. Insert Realistic Bookings
-- Demonstrates the exact 8-step lifecycle:
-- BK1001: PENDING (New request for demo user to see or helper to accept)
-- BK1002: ACCEPTED (Helper accepted, ready to start)
-- BK1003: IN_PROGRESS (Helper started work, payment locked)
-- BK1004: PAYMENT_PENDING (Work completed, final amount ₹550 entered, payment unlocked for User!)
-- BK1005: PAID (Completed, paid, reviewed)
-- BK1006 - BK1016: Realistic historical and active bookings across different users and helpers

INSERT INTO bookings (id, booking_code, user_id, helper_id, service_id, problem_description, booking_date, preferred_time, service_address, additional_notes, status, service_amount, additional_charges, final_amount, cancellation_reason, created_at) VALUES
-- 1. Pending request for Rajasekaran (Plumber) by Rahul Sharma (User)
(1, 'BK1001', 2, 1, 1, 'Bathroom concealed pipe is leaking slowly under the basin. Water seepage on the wall.', '2026-10-02', '10:30 AM', '12, 3rd Avenue, Anna Nagar East', 'Please bring spare teflon tape and connector pipe.', 'PENDING', 0.00, 0.00, 0.00, NULL, DATE_SUB(NOW(), INTERVAL 2 HOUR)),

-- 2. Accepted job for Rajasekaran by Saravanan K
(2, 'BK1002', 6, 1, 1, 'Kitchen tap handle broken and dripping continuously.', '2026-10-01', '03:00 PM', '24, Mount Poonamallee High Rd, Porur', 'Building security allows visitors after 2 PM.', 'ACCEPTED', 0.00, 0.00, 0.00, NULL, DATE_SUB(NOW(), INTERVAL 5 HOUR)),

-- 3. In Progress job for Manikandan (Electrician) by Rahul Sharma
(3, 'BK1003', 2, 4, 2, 'Master bedroom ceiling fan regulator stopped working, fan running only on high speed.', '2026-09-30', '02:00 PM', '12, 3rd Avenue, Anna Nagar East', 'Helper is currently working on replacing the regulator.', 'IN_PROGRESS', 0.00, 0.00, 0.00, NULL, DATE_SUB(NOW(), INTERVAL 1 DAY)),

-- 4. Payment Pending job for Rajasekaran by Rahul Sharma (PERFECT FOR USER PAYMENT DEMO!)
(4, 'BK1004', 2, 1, 1, 'Overhead water tank float ball valve replacement and mainline check.', '2026-09-29', '11:00 AM', '12, 3rd Avenue, Anna Nagar East', 'Helper completed work and installed a heavy-duty brass valve.', 'PAYMENT_PENDING', 450.00, 150.00, 600.00, NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),

-- 5. Paid & Reviewed job for Rajasekaran by Divya Balaji
(5, 'BK1005', 7, 1, 1, 'Water purifier inlet pipe joint was leaking heavily in modular kitchen.', '2026-09-27', '04:00 PM', '71, Race Course Colony, Guindy', 'Fixed cleanly in 45 minutes.', 'PAID', 350.00, 50.00, 400.00, NULL, DATE_SUB(NOW(), INTERVAL 4 DAY)),

-- 6. Paid & Reviewed job for Manikandan by Rahul Sharma
(6, 'BK1006', 2, 4, 2, 'Living room main distribution box tripped frequently whenever AC turned on.', '2026-09-25', '10:00 AM', '12, 3rd Avenue, Anna Nagar East', 'Diagnosed MCB capacity mismatch and replaced 32A fuse.', 'PAID', 450.00, 150.00, 600.00, NULL, DATE_SUB(NOW(), INTERVAL 6 DAY)),

-- 7. Paid & Reviewed job for Murugan T (Carpenter) by Karthik Raman
(7, 'BK1007', 4, 7, 4, 'Balcony wooden door was scraping against floor tiles due to swelling.', '2026-09-24', '02:30 PM', '88, Gandhi Nagar 1st Main, Adyar', 'Planed the door bottom edge and lubricated brass hinges.', 'PAID', 450.00, 50.00, 500.00, NULL, DATE_SUB(NOW(), INTERVAL 7 DAY)),

-- 8. Paid & Reviewed job for Ramesh G (Appliance) by Priya Sundaram
(8, 'BK1008', 3, 9, 6, 'LG front-load washing machine was vibrating excessively during spin cycle.', '2026-09-22', '11:00 AM', '45, 100 Feet Bypass Rd, Velachery', 'Replaced damper shock absorbers with genuine LG spare.', 'PAID', 500.00, 350.00, 850.00, NULL, DATE_SUB(NOW(), INTERVAL 9 DAY)),

-- 9. Paid & Reviewed job for Lakshmi Narayanan (Cleaning) by Ananya Iyer
(9, 'BK1009', 5, 6, 3, 'Deep cleaning of two bathrooms and kitchen tiles before house warming.', '2026-09-20', '09:00 AM', '15, GST Road, West Tambaram', 'Excellent cleaning service completed in 3 hours.', 'PAID', 600.00, 100.00, 700.00, NULL, DATE_SUB(NOW(), INTERVAL 11 DAY)),

-- 10. Paid & Reviewed job for Sangeetha R (Tutoring) by Divya Balaji
(10, 'BK1010', 7, 10, 7, '10th Class CBSE Quadratic equations and trigonometry home coaching.', '2026-09-18', '05:00 PM', '71, Race Course Colony, Guindy', 'Very patient teacher.', 'PAID', 350.00, 0.00, 350.00, NULL, DATE_SUB(NOW(), INTERVAL 13 DAY)),

-- 11. Paid & Reviewed job for Dinesh Babu (Painter) by Meera Krishnan
(11, 'BK1011', 9, 8, 5, 'Accent wall painting in drawing hall with geometric pattern.', '2026-09-15', '09:30 AM', '5, Usman Road, T. Nagar', 'Provided own rollers and drop cloths.', 'PAID', 700.00, 150.00, 850.00, NULL, DATE_SUB(NOW(), INTERVAL 16 DAY)),

-- 12. Paid & Reviewed job for Kumaravel P (Plumbing) by Arvind Swaminathan
(12, 'BK1012', 10, 2, 1, 'Replacement of ancient hot water gate valve in terrace.', '2026-09-14', '01:00 PM', '19, North Mada Street, Mylapore', 'Prompt response.', 'PAID', 350.00, 100.00, 450.00, NULL, DATE_SUB(NOW(), INTERVAL 17 DAY)),

-- 13. Paid & Reviewed job for Vijay Anand (Delivery) by Vignesh Natarajan
(13, 'BK1013', 8, 11, 8, 'Pick up orthopedic medical documents from clinic and deliver to residence.', '2026-09-12', '06:00 PM', '33, Nolambur Main Rd, Mogappair West', 'Safe and on-time courier service.', 'PAID', 200.00, 50.00, 250.00, NULL, DATE_SUB(NOW(), INTERVAL 19 DAY)),

-- 14. Paid & Reviewed job for Prakash K (Cleaning) by Rahul Sharma
(14, 'BK1014', 2, 12, 3, 'Balcony mesh cleaning and pigeon netting wash.', '2026-09-10', '10:00 AM', '12, 3rd Avenue, Anna Nagar East', 'Spotless work.', 'PAID', 300.00, 50.00, 350.00, NULL, DATE_SUB(NOW(), INTERVAL 21 DAY)),

-- 15. Cancelled booking for demo user
(15, 'BK1015', 2, 2, 1, 'Leaking garden bibcock tap.', '2026-09-08', '04:00 PM', '12, 3rd Avenue, Anna Nagar East', 'Customer managed to tighten the bolt themselves.', 'CANCELLED', 0.00, 0.00, 0.00, 'Customer tightened the washer manually before visit.', DATE_SUB(NOW(), INTERVAL 23 DAY)),

-- 16. Rejected booking by helper (due to scheduling conflict)
(16, 'BK1016', 3, 4, 2, 'Full flat wiring inspection on festival evening.', '2026-09-05', '07:30 PM', '45, 100 Feet Bypass Rd, Velachery', 'Already scheduled for another emergency job at that hour.', 'REJECTED', 0.00, 0.00, 0.00, 'Helper had another ongoing emergency job.', DATE_SUB(NOW(), INTERVAL 26 DAY)),

-- 17. Paid & Reviewed job for Senthil Nathan (Painter in Anna Nagar) by Rahul Sharma
(17, 'BK1017', 2, 13, 5, 'Living room ceiling touch up and primer coat painting.', '2026-09-03', '10:00 AM', '12, 3rd Avenue, Anna Nagar East', 'Smooth finish and no paint drops on floor.', 'PAID', 450.00, 50.00, 500.00, NULL, DATE_SUB(NOW(), INTERVAL 28 DAY)),

-- 18. Paid & Reviewed job for Ganesan V (Carpenter in Anna Nagar) by Saravanan K
(18, 'BK1018', 6, 14, 4, 'Sliding wardrobe drawer alignment and brass knob fitting.', '2026-09-01', '02:30 PM', '24, Mount Poonamallee High Rd, Porur', 'Solid workmanship and timely completion.', 'PAID', 400.00, 50.00, 450.00, NULL, DATE_SUB(NOW(), INTERVAL 30 DAY));

-- 5. Insert Realistic Payment Records
INSERT INTO payments (id, payment_code, booking_id, user_id, helper_id, amount, payment_method, transaction_id, status, paid_at) VALUES
(1, 'PAY1001', 5, 7, 1, 400.00, 'UPI', 'UPI_TXN_98721389712', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(2, 'PAY1002', 6, 2, 4, 600.00, 'Card', 'CRD_TXN_88471209341', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(3, 'PAY1003', 7, 4, 7, 500.00, 'Cash', 'CSH_TXN_44019284723', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(4, 'PAY1004', 8, 3, 9, 850.00, 'UPI', 'UPI_TXN_12093849102', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 9 DAY)),
(5, 'PAY1005', 9, 5, 6, 700.00, 'Net Banking', 'NBK_TXN_66192837401', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 11 DAY)),
(6, 'PAY1006', 10, 7, 10, 350.00, 'UPI', 'UPI_TXN_55192837490', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 13 DAY)),
(7, 'PAY1007', 11, 9, 8, 850.00, 'Card', 'CRD_TXN_77491029381', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 16 DAY)),
(8, 'PAY1008', 12, 10, 2, 450.00, 'Cash', 'CSH_TXN_33109284719', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 17 DAY)),
(9, 'PAY1009', 13, 8, 11, 250.00, 'UPI', 'UPI_TXN_44901928371', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 19 DAY)),
(10, 'PAY1010', 14, 2, 12, 350.00, 'UPI', 'UPI_TXN_88291049281', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(11, 'PAY1011', 17, 2, 13, 500.00, 'UPI', 'UPI_TXN_77192839101', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 28 DAY)),
(12, 'PAY1012', 18, 6, 14, 450.00, 'Cash', 'CSH_TXN_88192039481', 'SUCCESS', DATE_SUB(NOW(), INTERVAL 30 DAY));

-- 6. Insert Realistic Reviews
INSERT INTO reviews (id, booking_id, user_id, helper_id, rating, comment, created_at) VALUES
(1, 5, 7, 1, 5, 'Rajasekaran was very prompt and arrived within 25 minutes of confirmation. Replaced the RO purifier adapter quickly and cleanly. Highly recommend him for plumbing work!', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(2, 6, 2, 4, 5, 'Excellent electrical diagnosis! We had this tripping issue for a week. Manikandan diagnosed the MCB rating in 10 minutes and replaced it safely. Very polite behavior.', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(3, 7, 4, 7, 5, 'Murugan is a seasoned carpenter. Shaved our teak balcony door to perfection without chipping the paint. Arrived on time with proper woodworking tools.', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(4, 8, 3, 9, 5, 'Ramesh detected the drum suspension issue in our front-load washing machine right away. Saved us from a costly company service center bill. Very honest technician.', DATE_SUB(NOW(), INTERVAL 9 DAY)),
(5, 9, 5, 6, 4, 'Very thorough cleaning service! The kitchen and bathroom look brand new. Will definitely book again for deep cleaning before festivals.', DATE_SUB(NOW(), INTERVAL 11 DAY)),
(6, 10, 7, 10, 5, 'Sangeetha explains high school mathematics concepts with great patience and clarity. My daughter understood trigonometry proofs comfortably.', DATE_SUB(NOW(), INTERVAL 13 DAY)),
(7, 11, 9, 8, 4, 'Dinesh did a neat job with the royal blue stencil wall. Crisp edges and cleaned up all paint spatters before leaving.', DATE_SUB(NOW(), INTERVAL 16 DAY)),
(8, 12, 10, 2, 4, 'Kumaravel fixed the terrace overhead line valve swiftly. Good workmanship and fair pricing.', DATE_SUB(NOW(), INTERVAL 17 DAY)),
(9, 13, 8, 11, 5, 'Vijay handled our medical lab reports carefully and delivered them swiftly in heavy evening traffic. Great local delivery support!', DATE_SUB(NOW(), INTERVAL 19 DAY)),
(10, 14, 2, 12, 4, 'Prakash cleaned the entire balcony and railing thoroughly. Removed all dust and water spots. Good service.', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(11, 17, 2, 13, 5, 'Senthil is a skilled painter right here in Anna Nagar! Very clean roller work and neatly covered our furniture before starting.', DATE_SUB(NOW(), INTERVAL 28 DAY)),
(12, 18, 6, 14, 5, 'Ganesan aligned the wooden wardrobe drawers perfectly. Honest and prompt local craftsman.', DATE_SUB(NOW(), INTERVAL 30 DAY));

-- 7. Insert In-App Notifications
INSERT INTO notifications (id, user_id, title, message, link, is_read, created_at) VALUES
(1, 2, 'Service Completed - Payment Available', 'Your water tank ball valve repair (BK1004) has been completed by Rajasekaran. Total amount ₹600 is now ready for payment.', '/user/bookings', 0, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(2, 2, 'Work Started', 'Manikandan S has started work on your booking BK1003 (Fan regulator replacement).', '/user/bookings', 1, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(3, 2, 'Booking Placed', 'Your booking BK1001 has been submitted to Rajasekaran M and is pending acceptance.', '/user/bookings', 0, DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(4, 12, 'New Booking Request', 'You have received a new plumbing request BK1001 from Rahul Sharma in Anna Nagar East.', '/helper/requests', 0, DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(5, 12, 'Job Accepted', 'You accepted booking BK1002 from Saravanan K scheduled for 01 Oct 2026.', '/helper/jobs', 1, DATE_SUB(NOW(), INTERVAL 5 HOUR)),
(6, 15, 'Work In Progress', 'You started work on BK1003 for Rahul Sharma.', '/helper/jobs', 1, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(7, 1, 'System Alert', 'New helper registration received and verified for Prakash K (Cleaning).', '/admin/helpers', 1, DATE_SUB(NOW(), INTERVAL 20 DAY));
