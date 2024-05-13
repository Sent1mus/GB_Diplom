import datetime

from django.shortcuts import render

from ..models import *
from ..views import *


def main_page(request):
    # Render the main page template
    return render(request, 'main.html')


def about_us(request):
    # Render the about us page template
    return render(request, 'about_us.html')


def get_customers():
    # Retrieve all customer records from the database
    return Customer.objects.all()


def get_administrators():
    # Retrieve all administrator records from the database
    return Administrator.objects.all()


def get_service_providers():
    # Retrieve all service provider records from the database
    return ServiceProvider.objects.all()


def get_services():
    # Retrieve all service records from the database
    return Service.objects.all()


def get_reviews():
    # Retrieve all review records from the database
    return Review.objects.all()


def get_bookings():
    # Retrieve all booking records from the database
    return Booking.objects.all()


class BookingValidator:
    @staticmethod
    def is_slot_available(service_provider_id, appointment_datetime):
        # Calculate the end time of the appointment
        end_time = appointment_datetime + datetime.timedelta(hours=1)
        # Check for any overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            service_provider_id=service_provider_id,
            appointment_datetime__lt=end_time,
            appointment_datetime__gte=appointment_datetime
        ).exists()
        # Return True if no overlapping bookings are found
        return not overlapping_bookings


def temp_list_all_db(request):
    # Prepare context with all database entities for rendering
    context = {
        'customers': get_customers(),
        'administrators': get_administrators(),
        'service_providers': get_service_providers(),
        'services': get_services(),
        'reviews': get_reviews(),
        'bookings': get_bookings()
    }
    # Render the template with all database entities listed
    return render(request, 'temp_list_all_db.html', context)
