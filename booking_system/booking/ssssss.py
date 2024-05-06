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


from django.urls import path
from .views import main_page, about_us, services, signup, user_login, user_logout, list_all_db, profile

urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('services/', services, name='services'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('list/', list_all_db, name='list'),
]


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    # Внутренний класс для настройки модели
    class Meta:
        abstract = True  # Указываем, что модель является абстрактной и не должна создаваться в базе данных

    def __str__(self):
        return self.user.username


class Administrator(BaseProfile):
    pass

    def __str__(self):
        return f"Администратор: {self.user.username}, Телефон: {self.phone}"


class ServiceProvider(BaseProfile):
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Поставщик услуг: {self.user.username}, Специализация: {self.specialization}, Телефон: {self.phone}"


class Customer(BaseProfile):
    pass

    def __str__(self):
        return f"Клиент: {self.user.username}, Телефон: {self.phone}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField()  # Продолжительность услуги
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_time}. Booking created at {self.created_at}"


class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)  # Add ServiceProvider reference
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.service.name} provided by {self.service_provider.user.username}"



from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BaseProfile, Booking, Review
import datetime

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=75, required=True)
    phone = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            BaseProfile.objects.create(user=user, phone=self.cleaned_data['phone'])
        return user


class BookingForm(forms.ModelForm):
    appointment_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=True)

    class Meta:
        model = Booking
        fields = ['service_provider', 'appointment_time']

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data.get('appointment_time')
        if appointment_time:
            # Check if the appointment time is not in the past
            if appointment_time < datetime.datetime.now():
                raise forms.ValidationError("The appointment time cannot be in the past.")
            # Check if the time is on the hour or half-hour
            if appointment_time.minute % 30 != 0:
                raise forms.ValidationError("Booking time must be on the hour or half-hour.")
        return appointment_time


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = BaseProfile
        fields = ['phone']


{% extends 'base.html' %}

{% block title %}About Us - Beauty Saloon{% endblock %}

{% block content %}
<div class="header-content">
    <h1>About Us</h1>
    <p>Welcome to our Beauty Saloon. Here you can find the best services for your beauty needs. Our team is professional and highly skilled.</p>
</div>
{% endblock %}


<!DOCTYPE html>
{% load static %}
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <title>{% block title %}Beauty Saloon{% endblock %}</title>
</head>
<body>
    <div class="nav-container">
        <ul>
            <li><a href="{% url 'main' %}" class="nav-link">Главная</a></li>
            <li><a href="{% url 'about_us' %}" class="nav-link">О салоне</a></li>
            <li><a href="{% url 'services' %}" class="nav-link">Наши услуги</a></li>
            {% if user.is_authenticated %}
            <li><a href="{% url 'profile' %}" class="nav-link">Профиль</a></li>
            <li>
                <a href="{% url 'logout' %}" class="nav-link">Выйти</a>
            </li>
            {% else %}
            <li><a href="{% url 'signup' %}" class="nav-link">Регистрация</a></li>
            <li><a href="{% url 'login' %}" class="nav-link">Войти</a></li>
            {% endif %}
        </ul>
    </div>
    {% block content %}
    {% endblock %}
    <footer>
        {% block footer %}
        {% endblock %}
    </footer>
</body>
</html>


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


{% extends 'base.html' %}

{% block content %}
<div class="login-container">
    <h2>Login</h2>
    <form method="post" action="{% url 'login' %}">
        {% csrf_token %}
        <label for="username">Username:</label>
        <input type="text" name="username" id="username" required>
        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required>
        <button type="submit">Login</button>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
    </form>
</div>
{% endblock %}


{% extends 'base.html' %}

{% block title %}
Welcome to Beauty Saloon
{% endblock %}

{% block content %}
<div class="header-content">
    <h1>Добро пожаловать в Beauty Saloon</h1>
    <p>Откройте для себя наши мировоклассные услуги и процедуры по уходу за красотой, адаптированные именно под вас. Почувствуйте разницу с нашими квалифицированными специалистами и передовыми устройствами.</p>
    <div>
        <h2>Избранные услуги</h2>
        <ul>
            <li>Люкс-фациальные процедуры</li>
            <li>Терапевтические сеансы массажа</li>
            <li>Профессиональное парикмахерское обслуживание</li>
        </ul>
    </div>
</div>
{% endblock %}


{% extends 'base.html' %}

{% block title %}
Welcome to Beauty Saloon
{% endblock %}

{% block content %}
<div class="header-content">
    <h1> Личный кабинет </h1>
    <div>
    </div>
</div>
{% endblock %}


{% extends 'base.html' %}

{% block content %}
<div class="services-container">
    {% for service in services %}
    <div class="service">
        <h2>{{ service.name }}</h2>
        <p>{{ service.description }}</p>
        <p>Duration: {{ service.duration }}</p>
        <p>Price: {{ service.price }}</p>
        {% if user.is_authenticated %}
        <button onclick="openBookingModal('{{ service.id }}')">Book</button>
        {% endif %}
    </div>
    {% if forloop.counter|divisibleby:3 and not forloop.last %}
    </div><div class="services-container">
    {% endif %}
    {% endfor %}
</div>

<!-- Booking Modal -->
<div id="bookingModal" style="display:none;">
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Confirm Booking</button>
    </form>
</div>

<script>
function openBookingModal(serviceId) {
    // JavaScript to handle modal opening and setting serviceId dynamically
    document.getElementById('bookingModal').style.display = 'block';
}
</script>
{% endblock %}


{% extends 'base.html' %}

{% block title %}Signup - Beauty Saloon{% endblock %}

{% block content %}
<div class="content-container">
    <h1>Signup</h1>
    <p>Create your account to book services and get exclusive offers.</p>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Register</button>
    </form>
</div>
{% endblock %}


