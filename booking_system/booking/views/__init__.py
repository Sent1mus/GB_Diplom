from django.shortcuts import render

from ..models import *
from ..views import *


# Main Page View
def main_page(request):
    return render(request, 'main.html')


# About Us Page View
def about_us(request):
    return render(request, 'about_us.html')


def get_customers():
    return Customer.objects.all()


def get_administrators():
    return Administrator.objects.all()


def get_service_providers():
    return ServiceProvider.objects.all()


def get_services():
    return Service.objects.all()


def get_reviews():
    return Review.objects.all()


def get_bookings():
    return Booking.objects.all()


def list_all_db(request):
    context = {
        'customers': get_customers(),
        'administrators': get_administrators(),
        'service_providers': get_service_providers(),
        'services': get_services(),
        'reviews': get_reviews(),
        'bookings': get_bookings()
    }
    return render(request, 'list_all_db.html', context)