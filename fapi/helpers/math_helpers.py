from math import exp, sqrt


def gauss_score(a, b, sigma=0.4):
    d = a - b
    return exp(-(d * d) / (2 * sigma * sigma))


def wilson_score(rating, n_reviews, z=1.4):
    """
    Calculează Wilson Lower Bound pentru un rating pe 5 stele.
    """
    if n_reviews == 0:
        return 0.0

    phat = (rating - 1) / 4.0

    numerator = (
        phat
        + z * z / (2 * n_reviews)
        - z * sqrt((phat * (1 - phat) + z * z / (4 * n_reviews)) / n_reviews)
    )
    denominator = 1 + z * z / n_reviews
    lb = numerator / denominator

    return lb


import math


def haversine_distance(lat1, lon1, lat2, lon2):
    # Raza medie a Pamantului în metri
    R = 6_371_000

    # Convertim grade în radiani
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)

    # Formula Haversine
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distanta
    distance = R * c
    return distance
