# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)
    # Внутренний класс для настройки модели
    class Meta:
        abstract = True  # Указываем, что модель является абстрактной и не должна создаваться в базе данных

    def __str__(self):
        return self.user.username


class Administrator(BaseProfile):
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
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField(default=timezone.now) #TODO удалить default после сдачи, нужно для заполнения бд командой
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_datetime}. Booking created at {self.created_at}"


class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the review is created

    def __str__(self):
        return f"Review by {self.booking.customer.user.username} for {self.booking.service.name} provided by {self.booking.service_provider.user.username}"

# user_profile.html
{% extends 'base.html' %}

{% load static %}

{% block content %}
<div class="user-profile-container">
    <h1>Добро пожаловать в личный кабинет</h1>
    <div class="profile-section">
        <div class="profile-row">
            <div class="profile-column">
                <span>Ваш Email: </span>
                <span id="email-value">{{ user.email }}</span>
            </div>
            <div class="profile-column">
                <button onclick="toggleEdit('email')">Изменить</button>
                <input type="email" id="email-input" value="{{ user.email }}" style="display: inline;">
                <button onclick="save('email')" style="display:none;">Сохранить</button>
            </div>
        </div>
        <div class="profile-row">
            <div class="profile-column">
                <span>Ваш Телефон: </span>
                <span id="phone-value">{{ user.customer.phone }}</span>
            </div>
            <div class="profile-column">
                <button onclick="toggleEdit('phone')">Изменить</button>
                <input type="text" id="phone-input" value="{{ user.customer.phone }}" style="display:none;">
                <button onclick="save('phone')" style="display:none;">Сохранить</button>
            </div>
        </div>
        <div class="profile-row">
            <div class="profile-column">
                <span>Дата рождения: </span>
                <span>{{ user.customer.birth_date|date:"j F Y г." }}</span>
            </div>
            <div class="profile-column">
                <button onclick="togglePasswordChange()">Изменить пароль</button>
                <div id="password-change" style="display:none;">
                    <input type="password" id="old-password" placeholder="Старый пароль">
                    <input type="password" id="new-password" placeholder="Новый пароль">
                    <input type="password" id="confirm-password" placeholder="Подтвердите пароль">
                    <button onclick="changePassword()">Сохранить пароль</button>
                </div>
            </div>
        </div>
        <div class="profile-button-row">
            <a href="{% url 'list_booking' %}" class="link-as-button booking-button">Просмотреть историю бронирований</a>
        </div>
        <div class="profile-button-row">
            <button onclick="deactivateProfile()" class="link-as-button delete-profile-button">Удалить профиль</button>
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


# user_booking.html
{% extends 'base.html' %}

{% block content %}
<div class="order-history">
    <h1 class="order-history__header">История заказов</h1>
    <div class="order-history__table-container">
        <table class="order-history__table">
            <thead>
            <tr>
                <th class="order-history__column-header">Услуга</th>
                <th class="order-history__column-header">Мастер</th>
                <th class="order-history__column-header">Время предоставления услуги</th>
                <th class="order-history__column-header">Действия</th>
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
                           class="order-history__link order-history__link--edit">Изменить</a>
                        <a href="#" class="order-history__link order-history__link--delete" data-id="{{ booking.id }}"
                           onclick="confirmDelete(event, this)">Удалить заказ</a>
                        {% else %}
                        <a href="{% url 'add_review' booking.id %}" class="order-history__link order-history__link--review">Оставить отзыв</a>
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% empty %}
            <tr class="order-history__row">
                <td colspan="4" class="order-history__cell">Нет заказов.</td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
</div>
<script src="../static/js/profile/user_booking.js"></script>
{% endblock %}


# main.html
{% extends 'base.html' %}

{% block title %}
Welcome to Beauty Saloon
{% endblock %}

{% block content %}
<div class="header-content">
    <h1>Добро пожаловать в Beauty Saloon</h1>
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


# review.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Booking, Review
from ..forms import ReviewForm

@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        # Try to get an existing review
        review = Review.objects.get(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = True  # Flag to indicate updating an existing review
    except Review.DoesNotExist:
        # If no review exists, create a new one
        review = Review(booking=booking)  # Initialize review with booking
        form = ReviewForm(request.POST or None, instance=review)
        update = False

    if request.method == 'POST':
        if form.is_valid():
            review = form.save(commit=False)
            if not update:
                # Set foreign keys only if it's a new review
                review.customer = booking.customer  # Assuming customer field exists in Booking
                review.service = booking.service  # Assuming service field exists in Booking
                review.service_provider = booking.service_provider  # Assuming service_provider field exists in Booking
            review.save()
            return redirect('list_booking')  # Redirect to a suitable page after saving
        else:
            return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})
    else:
        return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})


# urls.py
from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import user_profile, update_profile, change_user_password, deactivate_user_profile
from .views.booking import list_booking, user_booking_update, user_booking_delete
from .views.review import add_review
from .views.service import services
from .views import main_page, about_us, list_all_db

urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('services/', services, name='services'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
    path('profile/booking/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('profile/booking/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),

    path('review/add/<int:booking_id>/', add_review, name='add_review'),

    path('list/', list_all_db, name='list'),
]



# booking.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from . import BookingValidator
from ..forms import BookingDateTimeForm
from ..models import Booking, Customer
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def list_booking(request):
    user = request.user
    now = timezone.now()
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'profile/user_booking.html', {'bookings': bookings, 'now': now})


@login_required
def user_booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    error_message = None  # Initialize an error message variable

    if request.method == 'POST':
        form = BookingDateTimeForm(request.POST)
        if form.is_valid():
            new_appointment_datetime = form.cleaned_data['appointment_datetime']
            if BookingValidator.is_slot_available(booking.service_provider_id, new_appointment_datetime):
                booking.appointment_datetime = new_appointment_datetime
                booking.save()
                return redirect('list_booking')
            else:
                error_message = "This time slot is not available. Please choose another time."
        return render(request, 'profile/user_booking_update.html', {'form': form, 'error_message': error_message})
    else:
        form = BookingDateTimeForm(initial={
            'month': booking.appointment_datetime.month,
            'day': booking.appointment_datetime.day,
            'hour': booking.appointment_datetime.hour,
        })
    return render(request, 'profile/user_booking_update.html', {'form': form})

@login_required
def user_booking_delete(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'error'}, status=400)


# user_review.html
{% extends 'base.html' %}

{% block content %}
<div class="review-form">
    <h1>Оставить отзыв</h1>
    <form method="post" action="{% url 'add_review' booking_id %}">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit Review</button>
    </form>
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
            <li><a href="{% url 'main' %}" class="nav-link"><img src="{% static 'images/main_logo.png' %}" alt="Logo"></a></li>
            {% if request.user.is_authenticated %}
            <li><a href="{% url 'user_profile' %}" class="nav-link">PROFILE</a></li>
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


# __init__.py
import datetime

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


class BookingValidator:
    @staticmethod
    def is_slot_available(service_provider_id, appointment_datetime):
        end_time = appointment_datetime + datetime.timedelta(hours=1)
        overlapping_bookings = Booking.objects.filter(
            service_provider_id=service_provider_id,
            appointment_datetime__lt=end_time,
            appointment_datetime__gte=appointment_datetime
        ).exists()
        return not overlapping_bookings


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

# profile.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from ..models import Customer
from ..forms import CustomPasswordChangeForm
import json


@login_required
def user_profile(request):
    customer = Customer.objects.get(user=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'profile/user_profile.html', {
        'password_form': password_form
    })


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


@login_required
@csrf_exempt
def change_user_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomPasswordChangeForm(user=request.user, data=data)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'success': True})
        else:
            print(form.errors)  # Log form errors to the console
            return JsonResponse({'success': False, 'errors': form.errors})


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
    <form method="post" id="bookingForm">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save Changes</button>
    </form>
</div>

{% if error_message %}
<script src="../static/js/profile/user_update.js"></script>
{% endif %}
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

# forms.py
import calendar
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import *


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        max_length=75,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})
    )
    birth_date = forms.DateField(
        required=True,
        input_formats=['%d.%m.%Y'],
        widget=forms.DateInput(format='%d.%m.%Y', attrs={'placeholder': 'DD.MM.YYYY'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
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
            Customer.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date']
            )
        return user


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Customer
        fields = ['phone', 'email']

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user.email = self.cleaned_data['email']
        if commit:
            instance.user.save()
            instance.save()
        return instance


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.specialization}"


class ServiceProviderForm(forms.Form):
    service_provider = CustomModelChoiceField(
        queryset=ServiceProvider.objects.all(),
        widget=forms.Select(attrs={'id': 'service_provider'}),
        label="Select master"
    )


class BookingDateTimeForm(forms.Form):
    current_year = timezone.now().year
    current_month = timezone.now().month
    current_day = timezone.now().day
    current_hour = timezone.now().hour

    # Adjust month choices
    if current_month == 12:
        month_choices = [(12, 'December'), (1, 'January')]
    else:
        month_choices = [(current_month, calendar.month_name[current_month]),
                         (current_month + 1, calendar.month_name[current_month + 1])]

    # Fields
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
                cleaned_data['appointment_datetime'] = timezone.datetime(year, int(month), int(day), int(hour), minute,
                                                                         tzinfo=timezone.get_current_timezone())
            except ValueError as e:
                raise forms.ValidationError("Invalid date or time: {}".format(e))
        else:
            raise forms.ValidationError("Please fill in all date and time fields.")

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


# list_all_db.html
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


# auth.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from ..forms import RegisterForm


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/profile/')
        else:
            return render(request, 'signup.html', {'form': form})
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
    logout(request)
    return redirect('main')


# service.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import BookingValidator
from ..forms import ServiceProviderForm, BookingDateTimeForm
from ..models import Service, Booking


@login_required
def services(request):
    services = Service.objects.all()
    forms_list = []

    for service in services:
        provider_form = ServiceProviderForm(prefix=f"service_{service.id}")
        date_time_form = BookingDateTimeForm(prefix=f"service_{service.id}")
        error_message = None
        current_data = None

        if request.method == 'POST' and request.POST.get('service_id') == str(service.id):
            provider_form = ServiceProviderForm(request.POST, prefix=f"service_{service.id}")
            date_time_form = BookingDateTimeForm(request.POST, prefix=f"service_{service.id}")
            if provider_form.is_valid() and date_time_form.is_valid():
                service_provider = provider_form.cleaned_data['service_provider']
                appointment_datetime = date_time_form.cleaned_data['appointment_datetime']

                if BookingValidator.is_slot_available(service_provider.id, appointment_datetime):
                    booking = Booking(
                        customer=request.user.customer,
                        service=service,
                        service_provider=service_provider,
                        appointment_datetime=appointment_datetime
                    )
                    booking.save()
                    return redirect('/profile/list_booking')
                else:
                    error_message = "Sorry, but this time has already been booked."
                    current_data = {
                        'service_provider': provider_form.cleaned_data['service_provider'],
                        'appointment_datetime': date_time_form.cleaned_data['appointment_datetime']
                    }

        forms_list.append((service, provider_form, date_time_form, error_message, current_data))

    return render(request, 'services.html', {
        'forms_list': forms_list,
    })


