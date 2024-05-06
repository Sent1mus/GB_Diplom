from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, BookingForm, EditProfileForm, ReviewForm
from .models import *


def list_all_db(request):
    customers = Customer.objects.all()
    administrators = Administrator.objects.all()
    service_providers = ServiceProvider.objects.all()
    services = Service.objects.all()
    reviews = Review.objects.all()
    bookings = Booking.objects.all()

    context = {
        'customers': customers,
        'administrators': administrators,
        'service_providers': service_providers,
        'services': services,
        'reviews': reviews,
        'bookings': bookings
    }

    return render(request, 'list_all_db.html', context)


# Main Page View
def main_page(request):
    return render(request, 'main.html')


# About Us Page View
def about_us(request):
    return render(request, 'about_us.html')


def check_provider_availability(service_provider, appointment_time):
    return Booking.objects.filter(service_provider=service_provider, appointment_time=appointment_time).exists()


def handle_booking_request(request):
    form = BookingForm(request.POST)
    if form.is_valid():
        service_provider = form.cleaned_data['service_provider']
        appointment_time = form.cleaned_data['appointment_time']
        if check_provider_availability(service_provider, appointment_time):
            return None, "This service provider is not available at the selected time."
        booking = form.save(commit=False)
        booking.customer = request.user.customer
        booking.save()
        return booking, None
    return None, form.errors


def render_services_page(request, form=None):
    services = Service.objects.all()
    form = form or BookingForm()
    return render(request, 'services.html', {
        'services': services,
        'form': form
    })


def services(request):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={request.path}')

    if request.method == 'POST':
        booking, error = handle_booking_request(request)
        if booking:
            return redirect('services')
        else:
            form = BookingForm(request.POST)  # Reinitialize the form with POST data
            return render_services_page(request, form=form)
    else:
        return render_services_page(request)


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to a home page
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')


def user_logout(request):
    logout(request)  # Log out the user
    return redirect('main')  # Redirect to the main page after logout


@login_required
def profile(request):
    return render(request, 'profile.html', {'profile': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user.baseprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user.baseprofile)
    return render(request, 'edit_profile.html', {'form': form})


class ReviewForm:
    pass


@login_required
def add_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.service = service
            review.save()
            return redirect('service_reviews', service_id=service.id)
        else:
            return render(request, 'add_review.html', {'form': form, 'service': service, 'error': 'Form is not valid'})
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'service': service})
