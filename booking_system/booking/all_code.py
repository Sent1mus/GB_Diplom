# fill_administrators.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Administrator

class Command(BaseCommand):
    help = 'Fills the Administrator database with dummy data'

    def handle(self, *args, **options):
        # Number of administrators to create
        num_administrators = 3

        for i in range(num_administrators):
            # Create a user for each administrator
            username = f'admin{i}'
            first_name = f'AdminFirst{i}'
            last_name = f'AdminLast{i}'
            email = f'admin{i}@example.com'
            password = 'password'
            phone = f'7927333111{i}'
            birth_date = f'200{i}-01-0{i+1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.is_staff = True  # Mark the user as staff
            user.save()

            Administrator.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone
            )
            # Create an administrator linked to the user

            self.stdout.write(self.style.SUCCESS(f'Successfully created administrator {username}'))


# fill_manytomany.py
from django.core.management.base import BaseCommand
from booking.models import ServiceProvider, Service
import random

class Command(BaseCommand):
    help = 'Populates the many-to-many relationship between Service and ServiceProvider'

    def handle(self, *args, **options):
        # Fetch all service providers and services
        service_providers = list(ServiceProvider.objects.all())
        services = list(Service.objects.all())

        if not service_providers or not services:
            self.stdout.write(self.style.ERROR('No service providers or services found. Please add some first.'))
            return

        # Optionally clear existing relationships
        for provider in service_providers:
            provider.service.clear()

        # Randomly assign services to each service provider
        for provider in service_providers:
            # Randomly choose a number of services to assign
            assigned_services = random.sample(services, k=random.randint(1, len(services)))
            provider.service.add(*assigned_services)
            provider.save()  # Save the changes

            self.stdout.write(self.style.SUCCESS(f'Assigned {len(assigned_services)} services to {provider.user.username}'))



# fill_service_providers.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import ServiceProvider, Service
import random

class Command(BaseCommand):
    help = 'Fills the ServiceProvider database with dummy data and assigns all services to them'

    def handle(self, *args, **options):
        # Number of service providers to create
        num_service_providers = 6  # You can change this number as needed

        # Fetch all services from the database
        all_services = list(Service.objects.all())

        for i in range(num_service_providers):
            # Create a user for each service provider
            username = f'master{i}'
            first_name = f'FirstName{i}'
            last_name = f'LastName{i}'
            email = f'master{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333221{i}'
            specialization = f'Specialization{i}'
            birth_date = f'200{i}-01-0{i+1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Create a service provider linked to the user
            service_provider = ServiceProvider.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone,
                specialization=specialization
            )

            # Assign all services to the service provider
            service_provider.service.add(*all_services)

            self.stdout.write(self.style.SUCCESS(f'Successfully created service provider {username} with all services assigned'))


# fill_customers.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Customer

class Command(BaseCommand):
    help = 'Fills the Customer database with dummy data'

    def handle(self, *args, **options):
        # Number of customers to create
        num_customers = 5

        for i in range(num_customers):
            # Create a user for each customer
            username = f'user{i}'
            first_name = f'First{i}'
            last_name = f'Last{i}'
            email = f'user{i}@example.com'
            password = 'password'
            phone = f'7927333222{i}'
            birth_date = f'200{i}-01-0{i+1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Create a customer linked to the user
            Customer.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created customer {username}'))


# auth.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from ..forms import RegisterForm


def signup(request):
    # Handle user signup
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user
            login(request, user)  # Log in the new user
            return redirect('/profile/')  # Redirect to profile page after signup
        else:
            return render(request, 'signup.html', {'form': form})  # Re-render the signup form with errors
    else:
        form = RegisterForm()
        return render(request, 'signup.html', {'form': form})  # Display the empty signup form


def user_login(request):
    # Handle user login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Authenticate user
        if user is not None:
            login(request, user)  # Log in the user
            return redirect('main')  # Redirect to main page after login
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})  # Show error if login fails
    else:
        return render(request, 'login.html')  # Display the login form


def user_logout(request):
    logout(request)  # Log out the user
    return redirect('main')  # Redirect to main page after logout


# booking.py
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from . import BookingValidator
from ..forms import BookingDateTimeForm, ServiceProviderForm, ServiceForm
from ..models import Booking, Customer


@login_required
@user_passes_test(lambda u: u.is_staff)
def all_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'profile/all_bookings.html', {'bookings': bookings})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingDateTimeForm(request.POST)
        provider_form = ServiceProviderForm(request.POST)
        service_form = ServiceForm(request.POST)
        if form.is_valid() and provider_form.is_valid() and service_form.is_valid():
            new_appointment_datetime = form.cleaned_data['appointment_datetime']
            new_service_provider = provider_form.cleaned_data['service_provider']
            new_service = service_form.cleaned_data['service']

            # Check if the selected time slot is available
            if BookingValidator.is_slot_available(new_service_provider.id, new_appointment_datetime):
                booking.appointment_datetime = new_appointment_datetime
                booking.service_provider = new_service_provider
                booking.service = new_service
                booking.save()
                return redirect('all_bookings')
            else:
                messages.error(request, "This time slot is not available. Please choose another time.")
    else:
        form = BookingDateTimeForm(initial={
            'month': booking.appointment_datetime.month,
            'day': booking.appointment_datetime.day,
            'hour': booking.appointment_datetime.hour,
        })
        provider_form = ServiceProviderForm(initial={'service_provider': booking.service_provider})
        service_form = ServiceForm(initial={'service': booking.service})
    return render(request, 'profile/admin_booking_update.html', {
        'form': form,
        'provider_form': provider_form,
        'service_form': service_form
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        return redirect('all_bookings')
    return render(request, 'profile/admin_booking_delete.html', {'booking': booking})


@login_required
def list_booking(request):
    user = request.user
    now = timezone.now()
    try:
        # Attempt to retrieve the customer profile associated with the current user
        customer_profile = Customer.objects.get(user=user)
        # Retrieve all bookings associated with the customer profile
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        # If no customer profile exists, return an empty list of bookings
        bookings = []
    # Render the booking list page with the bookings and current time
    return render(request, 'profile/user_booking.html', {'bookings': bookings, 'now': now})


@login_required
def user_booking_update(request, pk):
    # Retrieve the booking object or return a 404 error if not found
    booking = get_object_or_404(Booking, pk=pk)
    error_message = None

    if request.method == 'POST':
        form = BookingDateTimeForm(request.POST)
        if form.is_valid():
            # Extract the new appointment datetime from the form data
            new_appointment_datetime = form.cleaned_data['appointment_datetime']
            # Check if the new appointment time slot is available
            if BookingValidator.is_slot_available(booking.service_provider_id, new_appointment_datetime):
                # Update the booking with the new appointment datetime and save it
                booking.appointment_datetime = new_appointment_datetime
                booking.save()
                # Redirect to the booking list view after successful update
                return redirect('list_booking')
            else:
                # Set error message if the time slot is not available
                error_message = "This time slot is not available. Please choose another time."
        # Render the update form again with the error message if form is not valid or time slot not available
        return render(request, 'profile/user_booking_update.html', {'form': form, 'error_message': error_message})
    else:
        # Pre-fill the form with the existing booking details
        form = BookingDateTimeForm(initial={
            'month': booking.appointment_datetime.month,
            'day': booking.appointment_datetime.day,
            'hour': booking.appointment_datetime.hour,
        })
    # Render the update form
    return render(request, 'profile/user_booking_update.html', {'form': form, 'error_message': error_message})


# Ensure the user is authenticated before allowing access to the view
@login_required
def user_booking_delete(request, pk):
    if request.method == 'POST':
        # Retrieve the booking object or return a 404 error if not found
        booking = get_object_or_404(Booking, pk=pk)
        # Delete the booking
        booking.delete()
        # Return a success response
        return JsonResponse({'status': 'success'}, status=200)
    # Return an error response if not accessed via POST
    return JsonResponse({'status': 'error'}, status=400)


# signup.html
{% extends 'base.html' %}

{% block title %}Signup - Beauty Saloon{% endblock %}

{% block content %}
<div class="signup-container">
    <h2>Registration</h2><br>
    <form method="post">
        {% csrf_token %}
        <table>
            <tr>
                <td>First Name:</td>
                <td>{{ form.first_name }}</td>
            </tr>
            <tr>
                <td>Last Name:</td>
                <td>{{ form.last_name }}</td>
            </tr>
            <tr>
                <td>Username:</td>
                <td>{{ form.username }}</td>
            </tr>
            <tr>
                <td>Email:</td>
                <td>{{ form.email }}</td>
            </tr>
            <tr>
                <td>Phone Number:</td>
                <td>{{ form.phone }}</td>
            </tr>
            <tr>
                <td>Birth Date:</td>
                <td>{{ form.birth_date }}</td>
            </tr>
            <tr>
                <td>Password:</td>
                <td>{{ form.password1 }}</td>
            </tr>
            <tr>
                <td>Confirm Password:</td>
                <td>{{ form.password2 }}</td>
            </tr>
        </table>
        {% if form.errors %}
            <div class="form-errors" style="color: red;">
                Please correct the errors below.
            </div>
        {% endif %}
            <button type="submit" class="register-button">Register</button>
        </div>
    </form>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var birthDateInput = document.getElementById('id_birth_date');

    birthDateInput.addEventListener('keyup', function() {
        var value = this.value.replace(/[^0-9]/g, ''); // Удаляем все нечисловые символы
        if (value.length >= 2 && value.length <= 3) {
            this.value = value.slice(0, 2) + '.' + value.slice(2);
        } else if (value.length > 4) {
            this.value = value.slice(0, 2) + '.' + value.slice(2, 4) + '.' + value.slice(4);
        }
    });
});

</script>
{% endblock %}

# fill_managers.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Manager


class Command(BaseCommand):
    help = 'Fills the Manager database with dummy data'

    def handle(self, *args, **options):
        # Number of managers to create
        num_managers = 5  # You can change this number as needed

        for i in range(num_managers):
            # Create a user for each manager
            username = f'manager{i}'
            first_name = f'ManagerFirstName'
            last_name = f'ManagerLastName'
            email = f'manager{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333333{i}'
            birth_date = f'198{i}-01-0{i + 1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.is_staff = True
            user.save()

            # Create a manager linked to the user
            Manager.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created manager {username}'))


# __init__.py
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


# all_bookings.html
{% extends 'base.html' %}

{% block content %}
<div class="all-bookings-container">
    <h1>All Bookings</h1>
    <table>
        <thead>
            <tr>
                <th>Service</th>
                <th>Customer</th>
                <th>Service Provider</th>
                <th>Appointment Date and Time</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for booking in bookings %}
            <tr>
                <td>{{ booking.service.name }}</td>
                <td>{{ booking.customer.user.username }}</td>
                <td>{{ booking.service_provider.user.username }}</td>
                <td>{{ booking.appointment_datetime|date:"Y-m-d H:i" }}</td>
                <td>
                    <a href="{% url 'admin_booking_update' booking.id %}" class="btn btn-primary">Edit</a>
                    <a href="{% url 'admin_booking_delete' booking.id %}" class="btn btn-danger">Delete</a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5">No bookings found.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}


# user_booking_delete.html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>Delete Booking</h1>
    <p>Are you sure you want to delete this booking?</p>
    <form method="post">
        {% csrf_token %}
        <button type="submit">Delete</button>
    </form>
</div>
{% endblock %}

# fill_services.py
from datetime import timedelta
from django.core.management.base import BaseCommand
from booking.models import Service

class Command(BaseCommand):
    help = 'Ensures specific services are in the Service database'

    def handle(self, *args, **options):
        # Define a list of services with their details
        services_data = [
            {
                'name': 'Haircut',
                'description': 'Basic haircut',
                'duration': timedelta(hours=0, minutes=30),
                'price': 1000.00
            },
            {
                'name': 'Manicure',
                'description': 'Nail shaping and cuticle care',
                'duration': timedelta(hours=0, minutes=45),
                'price': 2000.00
            },
            {
                'name': 'Facial',
                'description': 'Skin cleansing and facial treatment',
                'duration': timedelta(hours=1, minutes=00),
                'price': 3000.00
            }
        ]

        # Iterate over the services data
        for service_data in services_data:
            # Use get_or_create to avoid creating duplicate entries
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'duration': service_data['duration'],
                    'price': service_data['price']
                }
            )

            # Check if the service was created or fetched
            if created:
                message = f'Successfully created service {service.name}'
            else:
                message = f'Service {service.name} already exists'

            # Print success message
            self.stdout.write(self.style.SUCCESS(message))


# user_review.html
{% extends 'base.html' %}

{% block content %}
<div class="reviews-container">
    <div class="review-form">
        <h1>Leave review</h1>
        <form method="post" action="{% url 'add_review' booking_id %}">
            {% csrf_token %}
            <span class="label-rating">Rating:</span> <br><br>{{ form.rating }}<br><br><br>
            <span class="label-comment">Write down your comment:</span><br><br>{{ form.comment }}<br><br><br>
            <button type="submit" class="form-control">Submit Review</button>
        </form>
    </div>
</div>
{% endblock %}


# reviews.html
{% extends 'base.html' %}

{% block content %}
<div class="reviews-container">
    <h1>Reviews for {{ service.name }}</h1>
    <table>
        {% for review in reviews %}
        <tr>
            <th>Rating</th>
            <th><strong>Comment by: {{ review.booking.customer.user.username }}</strong><br></th>
        </tr>

        <tr>
            <td>{{ review.rating }}</td>
            <td>

                Review: {{ review.comment }}<br><br>
                Review created at: <small>{{ review.created_at|date:"Y-m-d" }}</small>
            </td>
        </tr>
        {% empty %}
            <h3>No reviews available.</h3>
        {% endfor %}
    </table>
</div>
{% endblock %}


# fill_bookings.py
from django.core.management.base import BaseCommand
from booking.models import Booking, Service, Customer, ServiceProvider
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Fills the Booking database with structured data'

    def handle(self, *args, **options):
        customers = Customer.objects.all()
        services = list(Service.objects.all())
        service_providers = list(ServiceProvider.objects.all())

        if len(services) < 3 or len(service_providers) < 3:
            self.stdout.write(self.style.ERROR('Not enough services or service providers to assign 3 each.'))
            return

        for customer in customers:
            for i in range(3):  # Create 3 bookings per customer
                service = services[i % len(services)]
                service_provider = service_providers[i % len(service_providers)]
                days_ahead = i * 7  # Bookings spaced one week apart
                appointment_datetime = timezone.now() + timezone.timedelta(days=days_ahead)

                # Randomize the creation date within the past year
                days_back = random.randint(0, 365)  # Random number of days up to a year back
                created_at = timezone.now() - timezone.timedelta(days=days_back)  # Subtract days to go back in time

                Booking.objects.create(
                    customer=customer,
                    service=service,
                    service_provider=service_provider,
                    appointment_datetime=appointment_datetime,
                    created_at=created_at  # Added the created_at field with a random date within the last year
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created booking {i+1} for {customer.user.username} with {service.name} at {appointment_datetime}, created on {created_at}'))


# fill_reviews.py
from django.core.management.base import BaseCommand
from booking.models import Booking, Review, Service, Customer, ServiceProvider
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fills the Review database with structured data'

    def handle(self, *args, **options):
        customers = Customer.objects.all()
        services = list(Service.objects.all())
        service_providers = list(ServiceProvider.objects.all())

        if len(services) < 3 or len(service_providers) < 3:
            self.stdout.write(self.style.ERROR('Not enough services or service providers to assign 3 each.'))
            return

        for customer in customers:
            for i in range(3):  # Create 3 bookings and reviews per customer
                service = services[i % len(services)]
                service_provider = service_providers[i % len(service_providers)]

                # Create a booking
                booking = Booking.objects.create(
                    customer=customer,
                    service=service,
                    service_provider=service_provider,
                    appointment_datetime=timezone.now()  # Set the appointment time to now for simplicity
                )

                # Create a review for the booking
                Review.objects.create(
                    booking=booking,
                    rating=i % 5 + 1,  # Simple pattern for rating
                    comment=f'Review {i + 1} by {customer.user.username} for {service.name}'
                )

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created review {i + 1} by {customer.user.username} for {service.name}'))


# about_us.html
{% extends 'base.html' %}

{% block title %}About Us - Beauty Saloon{% endblock %}

{% block content %}
<div class="header-content">
    <h1>About Us</h1>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
        magna aliqua. Vitae suscipit tellus mauris a. Libero nunc consequat interdum varius sit amet mattis. Lectus sit
        amet est placerat in egestas. Interdum consectetur libero id faucibus nisl. Nulla malesuada pellentesque elit
        eget gravida cum sociis natoque. Ultricies mi eget mauris pharetra et ultrices neque ornare aenean. Aliquet nibh
        praesent tristique magna sit amet purus gravida. Pellentesque id nibh tortor id aliquet lectus proin nibh.
        Suspendisse ultrices gravida dictum fusce ut. Sed lectus vestibulum mattis ullamcorper velit sed ullamcorper
        morbi tincidunt. Feugiat pretium nibh ipsum consequat nisl vel.</p>

        <p>Gravida quis blandit turpis cursus in hac habitasse platea dictumst. Dictum varius duis at consectetur lorem
        donec. Cras sed felis eget velit. Faucibus scelerisque eleifend donec pretium vulputate sapien nec sagittis
        aliquam. Eget velit aliquet sagittis id. Vel elit scelerisque mauris pellentesque pulvinar pellentesque habitant
        morbi tristique. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit. In pellentesque massa placerat
        duis ultricies. Auctor neque vitae tempus quam pellentesque nec nam aliquam. Nulla malesuada pellentesque elit
        eget gravida cum sociis natoque. Velit sed ullamcorper morbi tincidunt ornare massa. Eu tincidunt tortor aliquam
        nulla facilisi cras. Sed blandit libero volutpat sed cras ornare arcu dui.</p>

        <p>Habitasse platea dictumst quisque sagittis purus. Urna neque viverra justo nec ultrices dui sapien eget. Dis
        parturient montes nascetur ridiculus. Faucibus turpis in eu mi. Enim eu turpis egestas pretium aenean pharetra
        magna ac placerat. Vitae elementum curabitur vitae nunc sed velit dignissim sodales ut. Ornare aenean euismod
        elementum nisi quis eleifend. Libero volutpat sed cras ornare arcu dui vivamus. Mi ipsum faucibus vitae aliquet
        nec ullamcorper sit. Purus gravida quis blandit turpis cursus in hac. Porttitor lacus luctus accumsan tortor
        posuere ac ut consequat. Eu sem integer vitae justo eget magna fermentum iaculis.</p>
        <p>Penatibus et magnis dis parturient. Dui nunc mattis enim ut tellus elementum sagittis vitae et. Augue eget arcu
        dictum varius duis at consectetur lorem donec. Ut venenatis tellus in metus. Ultricies lacus sed turpis
        tincidunt. Arcu bibendum at varius vel pharetra vel turpis nunc. Ipsum dolor sit amet consectetur adipiscing
        elit duis tristique sollicitudin. Pulvinar pellentesque habitant morbi tristique senectus et netus et malesuada.
        Id porta nibh venenatis cras. Proin nibh nisl condimentum id. Viverra maecenas accumsan lacus vel facilisis. Nec
        nam aliquam sem et tortor consequat id. Cras ornare arcu dui vivamus arcu felis. Diam maecenas ultricies mi eget
        mauris pharetra et. Venenatis tellus in metus vulputate. Nunc faucibus a pellentesque sit amet porttitor eget.
        Fermentum et sollicitudin ac orci phasellus egestas tellus.</p>

        <p>Sit amet massa vitae tortor condimentum. Porttitor eget dolor morbi non. Fringilla urna porttitor rhoncus dolor.
        At urna condimentum mattis pellentesque id. Quisque sagittis purus sit amet volutpat consequat mauris nunc
        congue. Dictum non consectetur a erat. Sapien et ligula ullamcorper malesuada proin libero. Aliquam malesuada
        bibendum arcu vitae elementum curabitur vitae nunc sed. Amet risus nullam eget felis. Diam quis enim lobortis
        scelerisque fermentum dui faucibus. At ultrices mi tempus imperdiet. Id donec ultrices tincidunt arcu non
        sodales neque sodales ut. Risus commodo viverra maecenas accumsan. Tristique risus nec feugiat in fermentum
        posuere urna nec. Pellentesque eu tincidunt tortor aliquam nulla facilisi cras fermentum odio. Augue interdum
        velit euismod in. Tristique risus nec feugiat in fermentum posuere urna. Augue mauris augue neque gravida. Justo
        donec enim diam vulputate ut pharetra sit amet aliquam. Sit amet porttitor eget dolor.</p>
</div>
{% endblock %}


# base.html
<!DOCTYPE html>
{% load static %}
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <title>{% block title %}Beauty Saloon{% endblock %}</title>
</head>
<body>
<header>
    <nav class="nav-container">
        <ul class="navlist">
            <li><a href="{% url 'about_us' %}" class="nav-link">ABOUT</a></li>
            <li><a href="{% url 'services' %}" class="nav-link">SERVICES</a></li>
            <li><a href="{% url 'main' %}" class="nav-link"><img src="{% static 'images/main_logo.png' %}"alt="Logo"></a></li>
            {% if request.user.is_authenticated %}
            {% if request.user.is_staff %}
            <li><a href="{% url 'manager_profile' %}" class="nav-link">MANAGER PROFILE</a></li>
            {% else %}
            <li><a href="{% url 'user_profile' %}" class="nav-link">PROFILE</a></li>
            {% endif %}
            <li><a href="{% url 'logout' %}" class="nav-link">LOGOUT</a></li>
            {% else %}
            <li><a href="{% url 'signup' %}" class="nav-link">REGISTER</a></li>
            <li><a href="{% url 'login' %}" class="nav-link">SIGN IN</a></li>
            {% endif %}
        </ul>
    </nav>
</header>
<main>
    {% block content %}
    {% endblock %}
</main>
<footer>
    <p>Â© 2024 Beauty Saloon. All rights reserved.</p>
    {% block footer %}
    {% endblock %}
</footer>
{% block javascript %}
{% endblock %}
</body>
</html>


# urls.py
from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import manager_profile,user_profile, update_profile, change_user_password, deactivate_user_profile
from .views.booking import all_bookings, list_booking, user_booking_update, user_booking_delete, admin_booking_update, \
    admin_booking_delete
from .views.review import add_review, service_reviews
from .views.service import services
from .views import main_page, about_us, temp_list_all_db

urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('services/', services, name='services'),

    path('manager/profile/', manager_profile, name='manager_profile'),
    path('manager/all_bookings/', all_bookings, name='all_bookings'),
    path('manager/booking/update/<int:pk>/', admin_booking_update, name='admin_booking_update'),
    path('manager/booking/delete/<int:pk>/', admin_booking_delete, name='admin_booking_delete'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
    path('profile/booking/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('profile/booking/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),

    path('review/add/<int:booking_id>/', add_review, name='add_review'),
    path('reviews/<int:service_id>/', service_reviews, name='service_reviews'),

    path('list/', temp_list_all_db, name='list'),
]



# admin_booking_delete.html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>Delete Booking</h1>
    <p>Are you sure you want to delete this booking?</p>
    <p>Service: {{ booking.service.name }}</p>
    <p>Customer: {{ booking.customer.user.username }}</p>
    <p>Service Provider: {{ booking.service_provider.user.username }}</p>
    <p>Appointment Date and Time: {{ booking.appointment_datetime|date:"Y-m-d H:i" }}</p>
    <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Delete</button>
        <a href="{% url 'all_bookings' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}


# profile.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from ..models import Manager, ServiceProvider, Customer
from ..forms import CustomPasswordChangeForm
import json


# View for displaying manager profile
@login_required
def manager_profile(request):
    manager = Manager.objects.get(user=request.user)
    return render(request, 'profile/manager_profile.html', {'manager': manager})


# View for displaying user profile
@login_required
def user_profile(request):
    customer = Customer.objects.get(user=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'profile/user_profile.html', {
        'password_form': password_form
    })


# View for updating user profile fields
@login_required
@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        customer = Customer.objects.get(user=request.user)

        if field == 'email':
            customer.user.email = value
            customer.user.save()
        elif field == 'phone':
            customer.phone = value
            customer.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# View for changing user password
@login_required
@csrf_exempt
def change_user_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomPasswordChangeForm(user=request.user, data=data)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session to prevent logout
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})


# View for deactivating a user profile
@login_required
@csrf_exempt
def deactivate_user_profile(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        customer.user.is_active = False
        customer.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# user_booking_update.html
{% extends 'base.html' %}

{% block content %}
<div class="container user-booking-update">
    <h1>Update Booking</h1>
    <form method="post" id="bookingForm" class="form-inline">
        {% csrf_token %}
        {{ form.as_p }}<br>
        <button type="submit" class="form-button">Save Changes</button>
    </form>
    {% if error_message %}
    <p style="color: red; text-align: center;">{{ error_message }}</p>
    {% endif %}
</div>
{% endblock %}

# run_all_fill_scripts.py
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run migrations and all fill scripts for customers, administrators, and service providers'

    def handle(self, *args, **options):
        # Run makemigrations and migrate to ensure the database is up to date
        self.stdout.write(self.style.SUCCESS('Running makemigrations...'))
        call_command('makemigrations')
        call_command('makemigrations', 'booking')
        self.stdout.write(self.style.SUCCESS('Running migrate...'))
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('Database migration completed.'))

        # Call fill_customers command
        self.stdout.write(self.style.SUCCESS('Starting to fill customers...'))
        call_command('fill_customers')
        self.stdout.write(self.style.SUCCESS('Finished filling customers.'))

        # Call fill_administrators command
        self.stdout.write(self.style.SUCCESS('Starting to fill administrators...'))
        call_command('fill_administrators')
        self.stdout.write(self.style.SUCCESS('Finished filling administrators.'))

        # Call fill_managers command
        self.stdout.write(self.style.SUCCESS('Starting to fill managers...'))
        call_command('fill_managers')
        self.stdout.write(self.style.SUCCESS('Finished filling managers.'))

        # Call fill_service_providers command
        self.stdout.write(self.style.SUCCESS('Starting to fill service providers...'))
        call_command('fill_service_providers')
        self.stdout.write(self.style.SUCCESS('Finished filling service providers.'))

        # Call fill_services command
        self.stdout.write(self.style.SUCCESS('Starting to fill services...'))
        call_command('fill_services')
        self.stdout.write(self.style.SUCCESS('Finished filling services.'))

        self.stdout.write(self.style.SUCCESS('Starting to fill reviews...'))
        call_command('fill_reviews')
        self.stdout.write(self.style.SUCCESS('Finished filling reviews.'))

        self.stdout.write(self.style.SUCCESS('Starting to fill bookings...'))
        call_command('fill_bookings')
        self.stdout.write(self.style.SUCCESS('Finished filling bookings.'))

        self.stdout.write(self.style.SUCCESS('Starting to fill manytomany...'))
        call_command('fill_manytomany')
        self.stdout.write(self.style.SUCCESS('Finished filling manytomany.'))


# service.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import BookingValidator
from ..forms import ServiceProviderForm, BookingDateTimeForm
from ..models import Service, Booking


@login_required  # Ensures that only authenticated users can access this view
def services(request):
    services = Service.objects.all()  # Retrieve all service objects from the database
    forms_list = []  # Initialize an empty list to store forms for each service

    # Iterate over each service to create and manage forms
    for service in services:
        # Create forms with a unique prefix based on service ID
        provider_form = ServiceProviderForm(prefix=f"service_{service.id}")
        date_time_form = BookingDateTimeForm(prefix=f"service_{service.id}")
        error_message = None  # Variable to store error messages
        current_data = None  # Variable to store current form data if needed

        # Check if the form is submitted and corresponds to the current service
        if request.method == 'POST' and request.POST.get('service_id') == str(service.id):
            # Populate forms with POST data
            provider_form = ServiceProviderForm(request.POST, prefix=f"service_{service.id}")
            date_time_form = BookingDateTimeForm(request.POST, prefix=f"service_{service.id}")

            # Validate forms
            if provider_form.is_valid() and date_time_form.is_valid():
                # Extract cleaned data from forms
                service_provider = provider_form.cleaned_data['service_provider']
                appointment_datetime = date_time_form.cleaned_data['appointment_datetime']

                # Check if the selected time slot is available
                if BookingValidator.is_slot_available(service_provider.id, appointment_datetime):
                    # Create and save a new booking
                    booking = Booking(
                        customer=request.user.customer,
                        service=service,
                        service_provider=service_provider,
                        appointment_datetime=appointment_datetime
                    )
                    booking.save()
                    return redirect('/profile/list_booking')  # Redirect user after booking
                else:
                    # Set error message if the time slot is not available
                    error_message = "Sorry, but this time has already been booked."
                    # Store current form data to repopulate the form
                    current_data = {
                        'service_provider': provider_form.cleaned_data['service_provider'],
                        'appointment_datetime': date_time_form.cleaned_data['appointment_datetime']
                    }

        # Append the service and its forms to the list
        forms_list.append((service, provider_form, date_time_form, error_message, current_data))

    # Render the page with the list of services and their forms
    return render(request, 'services.html', {
        'forms_list': forms_list,
    })


# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

"""
The module contains models for the basic user profile, administrator,
service provider, customer, service, booking and review in the service management system.
"""


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username


class Administrator(BaseProfile):
    pass


class Manager(BaseProfile):
    pass


class ServiceProvider(BaseProfile):
    specialization = models.CharField(max_length=100)
    service = models.ManyToManyField('Service')

    def __str__(self):
        return f"Поставщик услуг: {self.user.username}, Специализация: {self.specialization}, Телефон: {self.phone}"


class Customer(BaseProfile):
    pass


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField(
        default=timezone.now)  # TODO удалить default при релизе, нужен для заполнения бд командой
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_datetime}. Booking created at {self.created_at}"


class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.booking.customer.user.username} for {self.booking.service.name} provided by {self.booking.service_provider.user.username}"


# manager_profile.html
<!-- templates/profile/manager_profile.html -->
{% extends 'base.html' %}

{% block content %}
<div class="manager-profile-container">
    <h1>Manager Profile</h1>
    <div class="profile-section">
        <div class="profile-row">
            <div class="profile-column">
                <span>Email: </span>
                <span>{{ manager.user.email }}</span>
            </div>
        </div>
        <div class="profile-row">
            <div class="profile-column">
                <span>Phone: </span>
                <span>{{ manager.phone }}</span>
            </div>
        </div>
        <div class="profile-button-row">
            <a href="{% url 'all_bookings' %}" class="link-as-button">View All Bookings</a>
        </div>
    </div>
</div>
{% endblock %}


# temp_list_all_db.html
<!-- templates/customers_list.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>List of All Users</title>
</head>
<body>
<h1>List of All Users</h1>

<h2>Customers</h2>
<ul>
    {% for customer in customers %}
    <li>{{ customer.user.username }} - {{ customer.phone }}</li>
    {% empty %}
    <li>No customers found.</li>
    {% endfor %}
</ul>

<h2>Administrators</h2>
<ul>
    {% for admin in administrators %}
    <li>{{ admin.user.username }} - {{ admin.phone }}</li>
    {% empty %}
    <li>No administrators found.</li>
    {% endfor %}
</ul>

<h2>Service Providers</h2>
<ul>
    {% for provider in service_providers %}
    <li>{{ provider.user.username }} - {{ provider.specialization }} - {{ provider.phone }}</li>
    {% empty %}
    <li>No service providers found.</li>
    {% endfor %}
</ul>

<h2>Services</h2>
<ul>
    {% for service in services %}
    <li>{{ service.name }} - {{ service.description }} - Duration: {{ service.duration }} - Price: ${{ service.price }}</li>
    {% empty %}
    <li>No services found.</li>
    {% endfor %}
</ul>

<h2>Reviews</h2>
<ul>
    {% for review in reviews %}
    <li>Review by {{ review.customer.user.username }} for {{ review.service.name }} provided by {{ review.service_provider.user.username }} - Rating: {{ review.rating }} - Comment: {{ review.comment }}</li>
    {% empty %}
    <li>No reviews found.</li>
    {% endfor %}
</ul>

<h2>Bookings</h2>
<ul>
    {% for booking in bookings %}
    <li>{{ booking.customer.user.username }} booked {{ booking.service.name }} with {{ booking.service_provider.user.username }} at {{ booking.appointment_time }}. Booking create at {{ booking.created_at  }}</li>
    {% empty %}
    <li>No bookings found.</li>
    {% endfor %}
</ul>

</body>
</html>


# login.html
{% extends 'base.html' %}

{% block content %}
<div class="login-container">
    <h2>Login</h2><br>
    <form method="post" action="{% url 'login' %}">
        {% csrf_token %}
        <table>
            <tr>
                <td>Username:</td>
                <td><input type="text" name="username" id="username" required></td>
            </tr>
            <tr>
                <td>Password:</td>
                <td><input type="password" name="password" id="password" required></td>
            </tr>
            <tr>
                <td colspan="2"><button type="submit" class="login-button">Login</button></td>
            </tr>
        </table>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
    </form>
</div>
{% endblock %}


# services.html
{% extends 'base.html' %}

{% block content %}
<div style="display: flex; justify-content: center;">
    <table class="services">
        {% for service, provider_form, date_time_form, error_message, current_data in forms_list %}
        <tr>
            <td>
                <h2>{{ service.name }}</h2>
                <p>{{ service.description }}</p>
                <p>Duration: {{ service.duration }}</p>
                <p>Price: {{ service.price }}</p>
                <a href="{% url 'service_reviews' service.id %}" class="link-as-button">See all reviews</a>
            </td>
            <td>
                <form method="post" action="">
                    {% csrf_token %}
                    <input type="hidden" name="service_id" value="{{ service.id }}">
                    {{ provider_form.as_p }}
                    {{ date_time_form.as_p }}
                    {% if error_message %}
                    <p style="color: red;">{{ error_message }}</p>
                    {% endif %}
                    <button type="submit">Book</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</div>
{% endblock %}


# review.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Booking, Review, Service
from ..forms import ReviewForm


@login_required  # Ensures that only authenticated users can access this view
def add_review(request, booking_id):
    # Retrieve the booking object, or return a 404 error if not found
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        # Try to retrieve an existing review for the booking
        review = Review.objects.get(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = True  # Flag to indicate that this is an update operation
    except Review.DoesNotExist:
        # If no review exists, create a new review instance
        review = Review(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = False  # Flag to indicate that this is a create operation

    if request.method == 'POST':
        if form.is_valid():
            # Save the form data to the review object
            review = form.save(commit=False)
            if not update:
                # Set additional fields if this is a new review
                review.customer = booking.customer
                review.service = booking.service
                review.service_provider = booking.service_provider
            review.save()  # Save the review to the database
            return redirect('list_booking')  # Redirect to the booking list after saving
        else:
            # If the form is not valid, render the page again with the form
            return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})
    else:
        # If not a POST request, render the page with the form
        return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})


def service_reviews(request, service_id):
    # Retrieve the service object, or return a 404 error if not found
    service = get_object_or_404(Service, id=service_id)
    # Retrieve all reviews related to the service
    reviews = Review.objects.filter(booking__service=service).select_related('booking', 'booking__customer')
    # Render the reviews page with the service and its reviews
    return render(request, 'reviews.html', {'service': service, 'reviews': reviews})


# main.html
{% extends 'base.html' %}

{% block title %}
Welcome to Beauty Saloon
{% endblock %}

{% block content %}
<div class="header-content">
    <h1>Welcome to Beauty Saloon</h1>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
        magna aliqua. Vitae suscipit tellus mauris a. Libero nunc consequat interdum varius sit amet mattis. Lectus sit
        amet est placerat in egestas. Interdum consectetur libero id faucibus nisl. Nulla malesuada pellentesque elit
        eget gravida cum sociis natoque. Ultricies mi eget mauris pharetra et ultrices neque ornare aenean. Aliquet nibh
        praesent tristique magna sit amet purus gravida. Pellentesque id nibh tortor id aliquet lectus proin nibh.
        Suspendisse ultrices gravida dictum fusce ut. Sed lectus vestibulum mattis ullamcorper velit sed ullamcorper
        morbi tincidunt. Feugiat pretium nibh ipsum consequat nisl vel.</p>

    <p>Gravida quis blandit turpis cursus in hac habitasse platea dictumst. Dictum varius duis at consectetur lorem
        donec. Cras sed felis eget velit. Faucibus scelerisque eleifend donec pretium vulputate sapien nec sagittis
        aliquam. Eget velit aliquet sagittis id. Vel elit scelerisque mauris pellentesque pulvinar pellentesque habitant
        morbi tristique. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit. In pellentesque massa placerat
        duis ultricies. Auctor neque vitae tempus quam pellentesque nec nam aliquam. Nulla malesuada pellentesque elit
        eget gravida cum sociis natoque. Velit sed ullamcorper morbi tincidunt ornare massa. Eu tincidunt tortor aliquam
        nulla facilisi cras. Sed blandit libero volutpat sed cras ornare arcu dui.</p>

    <p>Habitasse platea dictumst quisque sagittis purus. Urna neque viverra justo nec ultrices dui sapien eget. Dis
        parturient montes nascetur ridiculus. Faucibus turpis in eu mi. Enim eu turpis egestas pretium aenean pharetra
        magna ac placerat. Vitae elementum curabitur vitae nunc sed velit dignissim sodales ut. Ornare aenean euismod
        elementum nisi quis eleifend. Libero volutpat sed cras ornare arcu dui vivamus. Mi ipsum faucibus vitae aliquet
        nec ullamcorper sit. Purus gravida quis blandit turpis cursus in hac. Porttitor lacus luctus accumsan tortor
        posuere ac ut consequat. Eu sem integer vitae justo eget magna fermentum iaculis.</p>
    <p>Penatibus et magnis dis parturient. Dui nunc mattis enim ut tellus elementum sagittis vitae et. Augue eget arcu
        dictum varius duis at consectetur lorem donec. Ut venenatis tellus in metus. Ultricies lacus sed turpis
        tincidunt. Arcu bibendum at varius vel pharetra vel turpis nunc. Ipsum dolor sit amet consectetur adipiscing
        elit duis tristique sollicitudin. Pulvinar pellentesque habitant morbi tristique senectus et netus et malesuada.
        Id porta nibh venenatis cras. Proin nibh nisl condimentum id. Viverra maecenas accumsan lacus vel facilisis. Nec
        nam aliquam sem et tortor consequat id. Cras ornare arcu dui vivamus arcu felis. Diam maecenas ultricies mi eget
        mauris pharetra et. Venenatis tellus in metus vulputate. Nunc faucibus a pellentesque sit amet porttitor eget.
        Fermentum et sollicitudin ac orci phasellus egestas tellus.</p>

    <p>Sit amet massa vitae tortor condimentum. Porttitor eget dolor morbi non. Fringilla urna porttitor rhoncus dolor.
        At urna condimentum mattis pellentesque id. Quisque sagittis purus sit amet volutpat consequat mauris nunc
        congue. Dictum non consectetur a erat. Sapien et ligula ullamcorper malesuada proin libero. Aliquam malesuada
        bibendum arcu vitae elementum curabitur vitae nunc sed. Amet risus nullam eget felis. Diam quis enim lobortis
        scelerisque fermentum dui faucibus. At ultrices mi tempus imperdiet. Id donec ultrices tincidunt arcu non
        sodales neque sodales ut. Risus commodo viverra maecenas accumsan. Tristique risus nec feugiat in fermentum
        posuere urna nec. Pellentesque eu tincidunt tortor aliquam nulla facilisi cras fermentum odio. Augue interdum
        velit euismod in. Tristique risus nec feugiat in fermentum posuere urna. Augue mauris augue neque gravida. Justo
        donec enim diam vulputate ut pharetra sit amet aliquam. Sit amet porttitor eget dolor.</p>
</div>
{% endblock %}


# forms.py
import calendar
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import *


# Form for user registration
class RegisterForm(UserCreationForm):
    # Define form fields with placeholders
    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=75, required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    birth_date = forms.DateField(required=True, input_formats=['%d.%m.%Y'],
                                 widget=forms.DateInput(format='%d.%m.%Y', attrs={'placeholder': 'DD.MM.YYYY'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Update placeholders for username and password fields
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create a customer profile linked to the user
            Customer.objects.create(user=user, phone=self.cleaned_data['phone'],
                                    birth_date=self.cleaned_data['birth_date'])
        return user


# Form for editing user profile
class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Customer
        fields = ['phone', 'email']

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # Initialize email field with user's current email
        self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user.email = self.cleaned_data['email']
        if commit:
            instance.user.save()
            instance.save()
        return instance


# Custom form for changing password
class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


# Custom field for displaying model choice fields
class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.specialization}"


# Form for selecting a service provider
class ServiceProviderForm(forms.Form):
    service_provider = CustomModelChoiceField(queryset=ServiceProvider.objects.all(),
                                              widget=forms.Select(attrs={'id': 'service_provider'}),
                                              label="Select master")


# Form for selecting a service
class ServiceForm(forms.Form):
    service = forms.ModelChoiceField(queryset=Service.objects.all(), label="Select Service")


# Form for booking date and time
class BookingDateTimeForm(forms.Form):
    current_year = timezone.now().year
    current_month = timezone.now().month
    current_day = timezone.now().day
    current_hour = timezone.now().hour

    # Adjust month choices based on current month
    if current_month == 12:
        month_choices = [(12, 'December'), (1, 'January')]
    else:
        month_choices = [(current_month, calendar.month_name[current_month]),
                         (current_month + 1, calendar.month_name[current_month + 1])]

    # Define fields for month, day, and hour selection
    month = forms.ChoiceField(choices=month_choices, initial=current_month)
    day = forms.ChoiceField(choices=[(i, i) for i in range(1, calendar.monthrange(current_year, current_month)[1] + 1)],
                            initial=current_day)
    hour = forms.ChoiceField(choices=[(i, i) for i in range(9, 21)],
                             initial=current_hour if 9 <= current_hour <= 20 else 9)

    def clean(self):
        cleaned_data = super().clean()
        year = self.current_year  # Use the current year
        month = cleaned_data.get('month')
        day = cleaned_data.get('day')
        hour = cleaned_data.get('hour')
        minute = 0  # Always set minutes to 00

        if month and day and hour:
            try:
                # Validate and create datetime object
                cleaned_data['appointment_datetime'] = timezone.datetime(year, int(month), int(day), int(hour), minute,
                                                                         tzinfo=timezone.get_current_timezone())
            except ValueError as e:
                raise forms.ValidationError("Invalid date or time: {}".format(e))
        else:
            raise forms.ValidationError("Please fill in all date and time fields.")

        return cleaned_data


# Form for submitting reviews
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


# user_booking.html
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="order-history">
    <h1 class="order-history__header">Booking history</h1>
    <div class="order-history__table-container">
        <table class="order-history__table">
            <thead>
            <tr>
                <th class="order-history__column-header">Service</th>
                <th class="order-history__column-header">Master</th>
                <th class="order-history__column-header">Date and time of service</th>
                <th class="order-history__column-header">Actions</th>
            </tr>
            </thead>
            <tbody>
            {% for booking in bookings %}
            <tr class="order-history__row">
                <td class="order-history__cell">{{ booking.service.name }}</td>
                <td class="order-history__cell">{{ booking.service_provider.user.username }}</td>
                <td class="order-history__cell">{{ booking.appointment_datetime|date:"Y-m-d H:i" }}</td>
                <td class="order-history__cell">
                    <div class="order-history__actions-container">
                        {% if booking.appointment_datetime > now %}
                        <a href="{% url 'user_booking_update' booking.id %}"
                           class="order-history__link order-history__link--edit">Change booking</a>
                        <a href="#" class="order-history__link order-history__link--delete" data-id="{{ booking.id }}"
                           onclick="confirmDelete(event, this)">Cancel booking</a>
                        {% else %}
                        {% if booking.review_set.exists %}
                        <a href="{% url 'add_review' booking.id %}" class="order-history__link order-history__link--review">Change review</a>
                        {% else %}
                        <a href="{% url 'add_review' booking.id %}" class="order-history__link order-history__link--review">Leave review</a>
                        {% endif %}
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% empty %}
            <tr class="order-history__row">
                <td colspan="4" class="order-history__cell">No bookings.</td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
</div>
<script src="../static/js/profile/user_booking.js"></script>
{% endblock %}


# admin_booking_update.html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>Edit Booking</h1>
    {% if messages %}
        <div class="alert alert-danger">
            {% for message in messages %}
                <p style="color:red">{{ message }}</p>
            {% endfor %}
        </div>
    {% endif %}
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        {{ provider_form.as_p }}
        {{ service_form.as_p }}
        <button type="submit" class="btn btn-primary">Save Changes</button>
    </form>
</div>
{% endblock %}


# user_profile.html
{% extends 'base.html' %}

{% load static %}

{% block content %}
<div class="user-profile-container">
    <h1>Welcome to Your Profile</h1>
    <div class="profile-section">
        <div class="profile-row">
            <div class="profile-column">
                <span>Your Email: </span>
                <span id="email-value">{{ user.email }}</span>
            </div>
            <div class="profile-column">
                <button onclick="toggleEdit('email')">Edit</button>
                <input type="email" id="email-input" value="{{ user.email }}" style="display: inline;">
                <button onclick="save('email')" style="display:none;">Save</button>
            </div>
        </div>
        <div class="profile-row">
            <div class="profile-column">
                <span>Your Phone: </span>
                <span id="phone-value">{{ user.customer.phone }}</span>
            </div>
            <div class="profile-column">
                <button onclick="toggleEdit('phone')">Edit</button>
                <input type="text" id="phone-input" value="{{ user.customer.phone }}" style="display:none;">
                <button onclick="save('phone')" style="display:none;">Save</button>
            </div>
        </div>
        <div class="profile-row">
            <div class="profile-column">
                <span>Date of Birth: </span>
                <span>{{ user.customer.birth_date|date:"j F Y" }}</span>
            </div>
            <div class="profile-column">
                <button onclick="togglePasswordChange()">Change Password</button>
                <div id="password-change" style="display:none;">
                    <input type="password" id="old-password" placeholder="Old Password">
                    <input type="password" id="new-password" placeholder="New Password">
                    <input type="password" id="confirm-password" placeholder="Confirm Password">
                    <button onclick="changePassword()">Save Password</button>
                </div>
            </div>
        </div>
        <div class="profile-button-row">
            <a href="{% url 'list_booking' %}" class="link-as-button booking-button">View Booking History</a>
        </div>
        <div class="profile-button-row">
            <button onclick="deactivateProfile()" class="link-as-button delete-profile-button">Delete Profile</button>
        </div>
    </div>
</div>
<!-- Hidden input to store URLs for JavaScript -->
<div id="data-container"
     data-update-profile-url="{% url 'update_profile' %}"
     data-change-password-url="{% url 'change_password' %}"
     data-deactivate-profile-url="{% url 'deactivate_profile' %}">
</div>

<script src="../static/js/profile/user_profile.js"></script>
{% endblock %}


# clear_db.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

class Command(BaseCommand):
    help = 'Clears all migration files, resets the migration history, and deletes the database.'

    def handle(self, *args, **options):
        # Удаление файлов миграций
        for app in settings.INSTALLED_APPS:
            try:
                app_path = os.path.join(settings.BASE_DIR, app.split('.')[-1])
                migrations_path = os.path.join(app_path, 'migrations')
                if os.path.exists(migrations_path):
                    for file in os.listdir(migrations_path):
                        file_path = os.path.join(migrations_path, file)
                        if file != '__init__.py' and file.endswith('.py') and os.path.isfile(file_path):
                            os.remove(file_path)
                            self.stdout.write(self.style.SUCCESS(f'Deleted {file} from {migrations_path}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No migrations directory found at {migrations_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {app}: {str(e)}'))

        # Очистка истории миграций в базе данных
        MigrationRecorder.Migration.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared all migration history from the database.'))



