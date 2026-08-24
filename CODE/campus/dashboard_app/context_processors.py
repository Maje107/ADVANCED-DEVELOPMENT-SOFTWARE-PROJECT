from resources.models import Booking


def booking_notifications(request):
    if request.user.is_authenticated and request.user.role == 'admin':
        return {'pending_booking_count': Booking.objects.filter(status='pending').count()}
    return {'pending_booking_count': 0}
