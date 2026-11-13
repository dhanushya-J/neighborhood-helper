import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'neighborhood-helper-college-project-secret-key-2026')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'neighborhood_helper')

    # Supported Cities / Districts with accurate reference coordinates
    CITIES = {
        'Coimbatore': (11.0168, 76.9558),
        'Chennai': (13.0827, 80.2707),
        'Madurai': (9.9252, 78.1198),
        'Tiruppur': (11.1085, 77.3411),
        'Salem': (11.6643, 78.1460),
        'Trichy': (10.7905, 78.7047),
        'Erode': (11.3410, 77.7172),
        'Tirunelveli': (8.7139, 77.7567),
        'Vellore': (12.9165, 79.1325),
        'Thanjavur': (10.7870, 79.1378),
        'Dindigul': (10.3673, 77.9803)
    }

    # Predefined localities with exact coordinates mapped to City / District
    LOCALITIES = {
        # Coimbatore Localities
        'gandhipuram': ((11.0183, 76.9644), 'Coimbatore'),
        'rs puram': ((11.0125, 76.9458), 'Coimbatore'),
        'r.s. puram': ((11.0125, 76.9458), 'Coimbatore'),
        'peelamedu': ((11.0264, 77.0142), 'Coimbatore'),
        'saibaba colony': ((11.0315, 76.9460), 'Coimbatore'),
        'singanallur': ((10.9996, 77.0266), 'Coimbatore'),
        'ramanathapuram': ((10.9930, 76.9850), 'Coimbatore'),
        'ukkadam': ((10.9910, 76.9590), 'Coimbatore'),
        'ganapathy': ((11.0420, 76.9830), 'Coimbatore'),
        'kuniyamuthur': ((10.9630, 76.9540), 'Coimbatore'),
        'vadavalli': ((11.0280, 76.9020), 'Coimbatore'),
        'saravanampatti': ((11.0824, 77.0006), 'Coimbatore'),
        'coimbatore': ((11.0168, 76.9558), 'Coimbatore'),

        # Chennai Localities
        'anna nagar': ((13.0850, 80.2101), 'Chennai'),
        'adyar': ((13.0012, 80.2565), 'Chennai'),
        'velachery': ((12.9815, 80.2180), 'Chennai'),
        'guindy': ((13.0067, 80.2025), 'Chennai'),
        'porur': ((13.0382, 80.1565), 'Chennai'),
        'tambaram': ((12.9249, 80.1000), 'Chennai'),
        'mogappair': ((13.0837, 80.1755), 'Chennai'),
        't. nagar': ((13.0418, 80.2341), 'Chennai'),
        't nagar': ((13.0418, 80.2341), 'Chennai'),
        'mylapore': ((13.0368, 80.2676), 'Chennai'),
        'kilpauk': ((13.0784, 80.2407), 'Chennai'),
        'kodambakkam': ((13.0513, 80.2209), 'Chennai'),
        'nungambakkam': ((13.0569, 80.2425), 'Chennai'),
        'thiruvanmiyur': ((12.9830, 80.2594), 'Chennai'),
        'perambur': ((13.1075, 80.2376), 'Chennai'),
        'sholinganallur': ((12.9010, 80.2279), 'Chennai'),
        'omr': ((12.9348, 80.2312), 'Chennai'),
        'chennai': ((13.0827, 80.2707), 'Chennai'),

        # Madurai Localities
        'goripalayam': ((9.9320, 78.1320), 'Madurai'),
        'simmakkal': ((9.9270, 78.1220), 'Madurai'),
        'mattuthavani': ((9.9540, 78.1580), 'Madurai'),
        'kk nagar': ((9.9290, 78.1520), 'Madurai'),
        'k.k. nagar': ((9.9290, 78.1520), 'Madurai'),
        'ss colony': ((9.9180, 78.1020), 'Madurai'),
        's.s. colony': ((9.9180, 78.1020), 'Madurai'),
        'aarapalayam': ((9.9320, 78.1030), 'Madurai'),
        'thallakulam': ((9.9350, 78.1380), 'Madurai'),
        'villapuram': ((9.8970, 78.1250), 'Madurai'),
        'tirunagar': ((9.8780, 78.0650), 'Madurai'),
        'teppakulam': ((9.9130, 78.1470), 'Madurai'),
        'madurai': ((9.9252, 78.1198), 'Madurai')
    }

    # Backward compatibility
    CHENNAI_LOCALITIES = {k: v[0] for k, v in LOCALITIES.items() if v[1] == 'Chennai'}
    OORUS = CITIES
