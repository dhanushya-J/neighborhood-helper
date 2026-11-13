import math
from config import Config

CITY_ALIASES = {
    'mdu': 'Madurai',
    'madurai': 'Madurai',
    'cbe': 'Coimbatore',
    'coimbatore': 'Coimbatore',
    'kovai': 'Coimbatore',
    'chn': 'Chennai',
    'maa': 'Chennai',
    'chennai': 'Chennai',
    'madras': 'Chennai',
    'tpr': 'Tiruppur',
    'tiruppur': 'Tiruppur',
    'tirupur': 'Tiruppur',
    'salem': 'Salem',
    'slm': 'Salem',
    'trichy': 'Trichy',
    'try': 'Trichy',
    'tiruchirappalli': 'Trichy',
    'erode': 'Erode',
    'ed': 'Erode',
    'vellore': 'Vellore',
    'tirunelveli': 'Tirunelveli',
    'nellai': 'Tirunelveli',
    'thanjavur': 'Thanjavur',
    'dindigul': 'Dindigul'
}

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great circle distance between two points
    on the earth (specified in decimal degrees).
    Returns distance in kilometers rounded to 1 decimal place.
    """
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except (ValueError, TypeError):
        return None

    R = 6371.0  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = R * c
    return round(distance, 1)

def resolve_coordinates(city=None, area=None, user_lat=None, user_lng=None):
    """
    Resolves latitude, longitude, display area name, and resolved city.
    Manual city/area entry takes absolute priority over GPS.
    Returns: (lat, lng, display_area, resolved_city)
    """
    raw_city = (city or '').strip().lower()
    raw_area = (area or '').strip().lower()

    # Detect alias or direct city match
    detected_city = CITY_ALIASES.get(raw_city)

    # Check if city name or alias was entered in area string (e.g. "Simmakkal, Madurai" or "mdu")
    if not detected_city:
        for alias, canon in CITY_ALIASES.items():
            if alias == raw_area or f" {alias} " in f" {raw_area} " or raw_area.endswith(f", {alias}") or raw_area.endswith(f" {alias}"):
                detected_city = canon
                break

    # If still not detected, check if raw_city matches any known city directly (case-insensitive)
    if not detected_city and raw_city:
        for known_city in Config.CITIES.keys():
            if known_city.lower() == raw_city:
                detected_city = known_city
                break

    # If it's a completely new custom district/town not in dictionary
    if not detected_city and raw_city:
        detected_city = raw_city.title()

    # Clean locality search string
    clean_area = raw_area
    if detected_city:
        clean_area = clean_area.replace(detected_city.lower(), '').strip(', ')
    for alias in CITY_ALIASES.keys():
        clean_area = clean_area.replace(alias, '').strip(', ')

    # 1. Match known locality in Config.LOCALITIES
    if clean_area and not clean_area.startswith('current location'):
        for loc_name, (coords, loc_city) in Config.LOCALITIES.items():
            if loc_name == clean_area or loc_name in clean_area or clean_area in loc_name:
                # If city is detected, prefer locality from that city
                if not detected_city or detected_city.lower() == loc_city.lower():
                    return coords[0], coords[1], loc_name.title(), loc_city

    # 2. If city is known in Config.CITIES, return city center
    if detected_city and detected_city in Config.CITIES:
        display_name = clean_area.title() if clean_area else detected_city
        coords = Config.CITIES[detected_city]
        return coords[0], coords[1], display_name, detected_city

    # 3. If city is a new custom district (not in Config.CITIES)
    if detected_city:
        display_name = clean_area.title() if clean_area else detected_city
        # Regional Tamil Nadu fallback centroid (11.1271, 78.6569)
        return 11.1271, 78.6569, display_name, detected_city

    # 4. GPS fallback
    if user_lat is not None and user_lng is not None:
        try:
            ulat = float(user_lat)
            ulng = float(user_lng)
            if -90 <= ulat <= 90 and -180 <= ulng <= 180 and not (ulat == 0 and ulng == 0):
                # Find nearest known city
                closest_city = 'Coimbatore'
                min_d = 999999.0
                for c_name, c_coords in Config.CITIES.items():
                    d = haversine(ulat, ulng, c_coords[0], c_coords[1])
                    if d is not None and d < min_d:
                        min_d = d
                        closest_city = c_name
                return ulat, ulng, f'Current Location ({closest_city})', closest_city
        except (ValueError, TypeError):
            pass

    # 5. Default fallback to Coimbatore
    coords = Config.CITIES['Coimbatore']
    return coords[0], coords[1], 'Gandhipuram', 'Coimbatore'
