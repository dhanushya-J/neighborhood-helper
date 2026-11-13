import os
import random
from app import app
from database.db import execute_db, query_db

PASS_HELPER = 'scrypt:32768:8:1$X7fvK9TINISWMoOE$2076608846d367dd28d3ae23f79e24a9cc96fd1ae92db94c6eeedca36ea144cb7bde52e0e21479feef7a79aba792f9d9f8c15882cb4966763203d7dac7d16233' # Helper@123

def seed_madurai():
    with app.app_context():
        # Check if Madurai helpers already exist
        mdu_count = query_db("SELECT COUNT(*) as c FROM helpers h JOIN users u ON h.user_id = u.id WHERE u.city = 'Madurai'", one=True)['c']
        if mdu_count > 0:
            print(f"Madurai already has {mdu_count} helpers.")
            return

        mdu_helpers = [
            ('Muruganathan K', 'muru.plumb.mdu@example.com', '9842109876', '12, North Veli St', 'Goripalayam', 9.9320, 78.1320, 1, 6, 'Expert domestic plumber in Goripalayam & Simmakkal, Madurai. Pipe repairs, motor fitting, sanitary fixtures.', 300.00, 4.7, 15),
            ('Pandian S', 'pandian.electric.mdu@example.com', '9843210987', '45, West Perumal Maistry St', 'Simmakkal', 9.9270, 78.1220, 2, 8, 'Licensed electrician in Simmakkal, Madurai. House wiring, short-circuits, LED lights, inverter setup.', 350.00, 4.6, 12),
            ('Meenakshi Sundaram', 'meenakshi.paint.mdu@example.com', '9844321098', '88, 80 Feet Road', 'KK Nagar', 9.9290, 78.1520, 5, 7, 'Specialist wall painter in KK Nagar & Anna Nagar Madurai. Distemper, emulsion, exterior weather coats.', 380.00, 4.8, 18),
            ('Alagarsamy R', 'alagar.wood.mdu@example.com', '9845432109', '21, Bypass Road', 'SS Colony', 9.9180, 78.1020, 4, 5, 'Master carpenter in SS Colony, Madurai. Wood shelving, modern kitchen cabinets, lock and door fitting.', 350.00, 4.5, 10),
            ('Soundararajan M', 'soundar.repairs.mdu@example.com', '9846543210', '104, Lake View Road', 'Mattuthavani', 9.9540, 78.1580, 6, 9, 'Senior appliance technician in Mattuthavani, Madurai. Washing machines, refrigerators, and microwave oven fixes.', 400.00, 4.7, 14)
        ]

        comments_pool = {
            5: ["Excellent service in Madurai! Very punctual and clean workmanship.",
                "Top notch helper. Solved the problem with great skill.",
                "Highly professional and courteous. Recommended!"],
            4: ["Good quality service, finished on time.",
                "Satisfied with the job done, very polite.",
                "Nice work, fair charges."],
            3: ["Decent job done.", "Service was average but resolved the issue."]
        }

        # Available customer user IDs for realistic reviews
        customer_users = query_db("SELECT id FROM users WHERE role = 'user' LIMIT 8")
        cust_ids = [u['id'] for u in customer_users] or [2, 3, 4, 5]

        for h in mdu_helpers:
            user_res = execute_db("""
                INSERT INTO users (name, email, password_hash, phone, role, address, city, area, latitude, longitude, profile_pic, is_active)
                VALUES (%s, %s, %s, %s, 'helper', %s, 'Madurai', %s, %s, %s, 'default_helper.png', 1)
            """, (h[0], h[1], PASS_HELPER, h[2], h[3], h[4], h[5], h[6]))
            user_id = user_res['last_id']

            helper_res = execute_db("""
                INSERT INTO helpers (user_id, service_id, experience_years, description, hourly_rate, availability, status, avg_rating, total_reviews)
                VALUES (%s, %s, %s, %s, %s, 'Available', 'approved', %s, %s)
            """, (user_id, h[7], h[8], h[9], h[10], h[11], h[12]))
            helper_id = helper_res['last_id']

            # Seed realistic review records
            target_rating = h[11]
            num_reviews = h[12]
            five_count = int(round(num_reviews * (target_rating - 3.8) / 1.2))
            five_count = max(0, min(num_reviews, five_count))
            four_count = num_reviews - five_count

            ratings_list = [5] * five_count + [4] * four_count
            for i, score in enumerate(ratings_list):
                c_id = cust_ids[i % len(cust_ids)]
                comment = random.choice(comments_pool[score])
                # Create completed booking record for review foreign key
                b_code = f"BK{helper_id * 1000 + i + 1}"
                b_res = execute_db("""
                    INSERT INTO bookings (booking_code, user_id, helper_id, service_id, problem_description,
                                         booking_date, preferred_time, service_address, status,
                                         service_amount, additional_charges, final_amount, created_at)
                    VALUES (%s, %s, %s, %s, 'Household service request', '2026-09-15', '11:00',
                            %s, 'COMPLETED', %s, 0.00, %s, DATE_SUB(NOW(), INTERVAL %s DAY))
                """, (b_code, c_id, helper_id, h[7], f"{h[4]}, Madurai", h[10], h[10], i + 1))
                b_id = b_res['last_id']

                execute_db("""
                    INSERT INTO reviews (booking_id, user_id, helper_id, rating, comment, created_at)
                    VALUES (%s, %s, %s, %s, %s, DATE_SUB(NOW(), INTERVAL %s DAY))
                """, (b_id, c_id, helper_id, score, comment, i + 1))

            # Recalculate true rating
            execute_db("""
                UPDATE helpers h
                SET avg_rating = COALESCE((SELECT ROUND(AVG(rating), 1) FROM reviews WHERE helper_id = %s), 0.0),
                    total_reviews = (SELECT COUNT(*) FROM reviews WHERE helper_id = %s)
                WHERE id = %s
            """, (helper_id, helper_id, helper_id))

        print("Seeded 5 Madurai helpers and authentic reviews successfully.")

if __name__ == "__main__":
    seed_madurai()
