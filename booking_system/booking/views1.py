from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView

from .forms import RegisterForm, BookingForm, EditProfileForm, ReviewForm
from .models import *


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


# Main Page View
def main_page(request):
    return render(request, 'main.html')


# About Us Page View
def about_us(request):
    return render(request, 'about_us.html')


def check_provider_availability(service_provider, appointment_time):
    return Booking.objects.filter(service_provider=service_provider, appointment_time=appointment_time).exists()


def handle_booking_request(request):
    form = create_booking_form(request)
    if is_form_valid(form):
        return process_valid_booking_form(request, form)
    return None, form.errors


def create_booking_form(request):
    return BookingForm(request.POST)


def is_form_valid(form):
    return form.is_valid()


def process_valid_booking_form(request, form):
    service_provider = form.cleaned_data['service_provider']
    appointment_time = form.cleaned_data['appointment_time']
    if check_provider_availability(service_provider, appointment_time):
        return None, "This service provider is not available at the selected time."
    return create_booking(request, form)


def create_booking(request, form):
    customer = get_or_create_customer(request)
    return save_booking(form, customer)


def get_or_create_customer(request):
    return Customer.objects.get_or_create(user=request.user)


def save_booking(form, customer):
    booking = form.save(commit=False)
    booking.customer = customer
    booking.save()
    return booking, None


def render_services_page(request, form=None):
    services = Service.objects.all()
    form = form or BookingForm()
    return render(request, 'services.html', {
        'services': services,
        'form': form
    })


def services(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request)
    return process_request_based_on_method(request)


def process_request_based_on_method(request):
    if request.method == 'POST':
        return handle_services_post(request)
    return handle_services_get(request)


def redirect_to_login(request):
    return redirect(f'/login/?next={request.path}')


def handle_services_post(request):
    form = BookingForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('services')
    return render_services_page(request, form)


def handle_services_get(request):
    form = BookingForm()
    services = Service.objects.all()
    form.fields['service_provider'].queryset = get_service_provider_queryset(request)
    return render_services_page(request, form)


def get_service_provider_queryset(request):
    service_id = request.GET.get('service', None)
    if service_id:
        return ServiceProvider.objects.filter(service__id=service_id)
    return ServiceProvider.objects.none()


def get_service_providers(request):
    service_id = request.GET.get('serviceId')
    providers = ServiceProvider.objects.filter(service__id=service_id).values('id', 'user__username', 'specialization')
    return JsonResponse({'providers': list(providers)})


class BookServiceView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'services.html'  # Adjust if you have a specific template for booking
    success_url = reverse_lazy('services')  # Redirect to the services page after booking

    def form_valid(self, form):
        # Add additional logic if needed, e.g., setting the customer
        form.instance.customer = self.request.user.customer
        return super().form_valid(form)


def signup(request):
    if request.method == 'POST':
        return process_signup_post(request)
    return process_signup_get(request)

def process_signup_post(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('main')
    return render(request, 'signup.html', {'form': form})

def process_signup_get(request):
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
    profile, created = BaseProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


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


# Booking List View
@login_required
def booking_list(request):
    user = request.user
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'user_booking.html', {'bookings': bookings})


# Booking Update View
@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form})


# Booking Delete View
@login_required
def booking_delete(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return redirect('booking_list')
    else:
        # Render a template with an error message
        return render(request, 'error.html', {
            'message': 'This action is only allowed via a POST request.'
        })
