# users/utils/ip_utils.py
import requests
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Safely extract IP address from Django request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_ip_location(ip):
    """Return structured location data for given IP using ipapi.co."""
    try:
        res = requests.get(f"https://ipwho.is/{ip}/json/", timeout=5)
        if res.status_code == 200:
            data = res.json()
            return {
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "ip": ip,
            }
    except Exception as e:
        logger.warning(f"IP lookup failed for {ip}: {e}")
    return None
