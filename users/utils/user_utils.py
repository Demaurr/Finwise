from .ip_utils import get_client_ip, get_ip_location

def update_user_location_if_missing(request, user):
    """If user has no location, update it using their IP."""
    if not user.location:
        ip = get_client_ip(request)
        location_data = get_ip_location(ip)
        if location_data:
            user.location = location_data
            user.save(update_fields=["location"])
