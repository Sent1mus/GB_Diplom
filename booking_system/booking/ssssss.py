# urls.py
from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import user_profile, edit_profile
from .views.booking import user_booking_list, user_booking_update, user_booking_delete
from .views.service import *
from .views import *


urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('services/', services, name='services'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),


    path('services/book/<int:service_id>/', book_service, name='book_service'),
    path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('user_profile/', user_profile, name='user_profile'),
    path('user_profile/edit/', edit_profile, name = 'edit_profile'),
    path('user_profile/bookings_list/', user_booking_list, name='user_booking_list'),
    path('user_profile/bookings/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('user_profile/bookings/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),
    path('list/', list_all_db, name='list'),
]



# models.py
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
    duration = models.DurationField()  # Продолжительность услуги
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_datetime}. Booking created at {self.created_at}"


class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)  # Add ServiceProvider reference
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.service.name} provided by {self.service_provider.user.username}"


# forms.py
from datetime import datetime
from time import strptime

from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm


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
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        current_hour = now.hour

        # Генерация выборов для года
        self.fields['year'] = forms.ChoiceField(choices=[(i, i) for i in range(current_year, current_year + 2)])

        # Генерация выборов для месяца
        self.fields['month'] = forms.ChoiceField(choices=[(i, i) for i in range(current_month, 13)])

        # Генерация выборов для дня
        self.fields['day'] = forms.ChoiceField(choices=[(i, i) for i in range(current_day, 31)])

        # Генерация выборов для часа (с 9 до 19)
        self.fields['hour'] = forms.ChoiceField(choices=[(i, i) for i in range(9, 20)])

        # Генерация выборов для минут (только минуты, кратные 30)
        self.fields['minute'] = forms.ChoiceField(choices=[(i, i) for i in range(0, 60, 30)])

    class Meta:
        model = Booking
        fields = ['service', 'service_provider']

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')
        day = cleaned_data.get('day')
        hour = cleaned_data.get('hour')
        minute = cleaned_data.get('minute')

        if year and month and day and hour and minute:
            try:
                appointment_datetime = datetime(int(year), int(month), int(day), int(hour), int(minute))
                cleaned_data['appointment_datetime'] = appointment_datetime
            except ValueError:
                raise forms.ValidationError("Invalid date or time.")

        return cleaned_data


class ServiceProviderForm(forms.Form):
    service_provider = forms.ModelChoiceField(queryset=None, label='Выберите поставщика услуг')

    def __init__(self, *args, **kwargs):
        available_service_providers = kwargs.pop('available_service_providers', None)
        super().__init__(*args, **kwargs)
        self.fields['service_provider'].queryset = available_service_providers


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = BaseProfile
        fields = ['phone']


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
            return redirect('main')
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


# booking.py
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import BookingForm
from ..models import Booking, Customer
from django.contrib.auth.decorators import login_required

@login_required
def user_booking_list(request):
    user = request.user
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'user_booking.html', {'bookings': bookings})

@login_required
def user_booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form})

@login_required
def user_booking_delete(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return redirect('booking_list')
    else:
        return render(request, 'error.html', {'message': 'This action is only allowed via a POST request.'})


# profile.py
from django.shortcuts import render, redirect
from ..forms import EditProfileForm
from ..models import BaseProfile
from django.contrib.auth.decorators import login_required


@login_required
def user_profile(request):
    return render(request, 'profile/user_profile.html', {'user_profile': request.user})


@login_required
def edit_profile(request):
    profile, created = BaseProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile.html')
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


# review.py
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import ReviewForm
from ..models import Service
from django.contrib.auth.decorators import login_required

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


# service.py
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Service, ServiceProvider, Booking
from ..forms import BookingForm, ServiceProviderForm
from django.contrib.auth.decorators import login_required


def services(request):
    services = Service.objects.all()
    return render(request, 'services.html', {'services': services})


@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return redirect('select_provider', service_id=service.id)


@login_required
def select_provider(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    providers = ServiceProvider.objects.filter(service=service)
    return render(request, 'select_provider.html', {'service': service, 'providers': providers})


@login_required
def booking_confirm(request, service_id, provider_id):
    service = get_object_or_404(Service, id=service_id)
    provider = get_object_or_404(ServiceProvider, id=provider_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user.customer
            booking.service = service
            booking.service_provider = provider
            booking.save()
            return redirect('booking_list')
    else:
        form = BookingForm(initial={'service': service, 'service_provider': provider})

    return render(request, 'booking_confirm.html', {'form': form, 'service': service, 'provider': provider})


# __init__.py
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

# review.cpython-311.pyc
Д

    l9fv  с                   зT   Ќ d dl mZmZmZ ddlmZ ddlmZ d dlm	Z	 e	dё д   Ф         Z
dS )ж    )┌render┌redirect┌get_object_or_404ж   )┌
ReviewForm)┌Service)┌login_requiredc                 зе  Ќ t          t          |гд  Ф        }| j        dk    rљt          | j        д  Ф        }|а                    д   Ф         rS|а                    dгд  Ф        }| j        |_        ||_        |а                    д   Ф          t          d|j
        гд  Ф        S t          | d||dd	юд  Ф        S t          д   Ф         }t          | d||d
юд  Ф        S )N)┌id┌POSTF)┌commit┌service_reviews)┌
service_idzadd_review.htmlzForm is not valid)┌form┌service┌error)r   r   )r   r   ┌methodr   r   ┌is_valid┌save┌userr   r   r   r   )┌requestr   r   r   ┌reviews        ЩBW:\Study\000 Diplom\Project\booking_system\booking\views\review.py┌
add_reviewr      s╩   ђ тЦеJл7Л7н7ђGпё~ўмлПў'ю,Л'н'ѕпЈ=і=Ѕ?ї?­ 	xпЌYњYаeљYЛ,н,ѕFп!ю,ѕFїKп$ѕFїNпЈKіKЅMїMѕMПл-И'╝*лEЛEнEлEтў'л#4ИtлPWлbuл6vл6vЛwнwлwтЅ|ї|ѕПљ'л,░t╚л.Pл.PЛQнQлQз    N)┌django.shortcutsr   r   r   ┌formsr   ┌modelsr   ┌django.contrib.auth.decoratorsr	   r   Е r   r   Щ<module>r!      sЂ   ­п @л @л @л @л @л @л @л @л @л @п л л л л л п л л л л л п 9л 9л 9л 9л 9л 9Я­R­ Rы ё­R­ R­ Rr   

# __init__.cpython-311.pyc
Д

    u9fш  с                   зX   Ќ d dl mZ ddlT ddlT dё Zdё Zdё Zdё Zdё Zd	ё Z	d
ё Z
dё Zdё Zd
S )ж    Е┌renderж   )┌*c                 з"   Ќ t          | dд  Ф        S )Nz	main.htmlr   Е┌requests    ЩDW:\Study\000 Diplom\Project\booking_system\booking\views\__init__.py┌	main_pager      s   ђ Пљ'ў;Л'н'л'з    c                 з"   Ќ t          | dд  Ф        S )Nz
about_us.htmlr   r   s    r
   ┌about_usr   
   s   ђ Пљ'ў?Л+н+л+r   c                  з>   Ќ t           j        а                    д   Ф         S ЕN)┌Customer┌objects┌allЕ r   r
   ┌
get_customersr      s   ђ ПнОмЛ!н!л!r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌
Administratorr   r   r   r   r
   ┌get_administratorsr      s   ђ Пн О$м$Л&н&л&r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌ServiceProviderr   r   r   r   r
   ┌get_service_providersr      s   ђ Пн"О&м&Л(н(л(r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌Servicer   r   r   r   r
   ┌get_servicesr      з   ђ Пї?ОмЛ н л r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌Reviewr   r   r   r   r
   ┌get_reviewsr"   !   s   ђ Пї>ОмЛнлr   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌Bookingr   r   r   r   r
   ┌get_bookingsr%   %   r   r   c                 зк   Ќ t          д   Ф         t          д   Ф         t          д   Ф         t          д   Ф         t	          д   Ф         t          д   Ф         dю}t
          | d|д  Ф        S )N)┌	customers┌administrators┌service_providers┌services┌reviews┌bookingszlist_all_db.html)r   r   r   r   r"   r%   r   )r	   ┌contexts     r
   ┌list_all_dbr.   )   sQ   ђ т"Љ_ћ_П,Л.н.П2Л4н4П ЉNћNПЉ=ћ=П ЉNћN­
­ ђGш љ'л-еwЛ7н7л7r   N)
┌django.shortcutsr   ┌models┌viewsr   r   r   r   r   r   r"   r%   r.   r   r   r
   Щ<module>r2      s└   ­п #л #л #л #л #л #Я л л л п л л л ­(­ (­ (­
,­ ,­ ,­"­ "­ "­'­ '­ '­)­ )­ )­!­ !­ !­ ­  ­  ­!­ !­ !­	8­ 	8­ 	8­ 	8­ 	8r   

# urls.py
from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import user_profile, edit_profile
from .views.booking import user_booking_list, user_booking_update, user_booking_delete
from .views.service import *
from .views import *


urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('services/', services, name='services'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),


    path('services/book/<int:service_id>/', book_service, name='book_service'),
    path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('user_profile/', user_profile, name='user_profile'),
    path('user_profile/edit/', edit_profile, name = 'edit_profile'),
    path('user_profile/bookings_list/', user_booking_list, name='user_booking_list'),
    path('user_profile/bookings/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('user_profile/bookings/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),
    path('list/', list_all_db, name='list'),
]



# models.py
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
    duration = models.DurationField()  # Продолжительность услуги
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.user.username} booked {self.service.name} with {self.service_provider.user.username} at {self.appointment_datetime}. Booking created at {self.created_at}"


class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)  # Add ServiceProvider reference
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.service.name} provided by {self.service_provider.user.username}"


# forms.py
from datetime import datetime
from time import strptime

from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm


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
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        current_hour = now.hour

        # Генерация выборов для года
        self.fields['year'] = forms.ChoiceField(choices=[(i, i) for i in range(current_year, current_year + 2)])

        # Генерация выборов для месяца
        self.fields['month'] = forms.ChoiceField(choices=[(i, i) for i in range(current_month, 13)])

        # Генерация выборов для дня
        self.fields['day'] = forms.ChoiceField(choices=[(i, i) for i in range(current_day, 31)])

        # Генерация выборов для часа (с 9 до 19)
        self.fields['hour'] = forms.ChoiceField(choices=[(i, i) for i in range(9, 20)])

        # Генерация выборов для минут (только минуты, кратные 30)
        self.fields['minute'] = forms.ChoiceField(choices=[(i, i) for i in range(0, 60, 30)])

    class Meta:
        model = Booking
        fields = ['service', 'service_provider']

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')
        day = cleaned_data.get('day')
        hour = cleaned_data.get('hour')
        minute = cleaned_data.get('minute')

        if year and month and day and hour and minute:
            try:
                appointment_datetime = datetime(int(year), int(month), int(day), int(hour), int(minute))
                cleaned_data['appointment_datetime'] = appointment_datetime
            except ValueError:
                raise forms.ValidationError("Invalid date or time.")

        return cleaned_data


class ServiceProviderForm(forms.Form):
    service_provider = forms.ModelChoiceField(queryset=None, label='Выберите поставщика услуг')

    def __init__(self, *args, **kwargs):
        available_service_providers = kwargs.pop('available_service_providers', None)
        super().__init__(*args, **kwargs)
        self.fields['service_provider'].queryset = available_service_providers


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = BaseProfile
        fields = ['phone']


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
            return redirect('main')
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


# booking.py
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import BookingForm
from ..models import Booking, Customer
from django.contrib.auth.decorators import login_required

@login_required
def user_booking_list(request):
    user = request.user
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'user_booking.html', {'bookings': bookings})

@login_required
def user_booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form})

@login_required
def user_booking_delete(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return redirect('booking_list')
    else:
        return render(request, 'error.html', {'message': 'This action is only allowed via a POST request.'})


# profile.py
from django.shortcuts import render, redirect
from ..forms import EditProfileForm
from ..models import BaseProfile
from django.contrib.auth.decorators import login_required


@login_required
def user_profile(request):
    return render(request, 'profile/user_profile.html', {'user_profile': request.user})


@login_required
def edit_profile(request):
    profile, created = BaseProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile.html')
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


# review.py
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import ReviewForm
from ..models import Service
from django.contrib.auth.decorators import login_required

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


# service.py
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Service, ServiceProvider, Booking
from ..forms import BookingForm, ServiceProviderForm
from django.contrib.auth.decorators import login_required


def services(request):
    services = Service.objects.all()
    return render(request, 'services.html', {'services': services})


@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return redirect('select_provider', service_id=service.id)


@login_required
def select_provider(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    providers = ServiceProvider.objects.filter(service=service)
    return render(request, 'select_provider.html', {'service': service, 'providers': providers})


@login_required
def booking_confirm(request, service_id, provider_id):
    service = get_object_or_404(Service, id=service_id)
    provider = get_object_or_404(ServiceProvider, id=provider_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user.customer
            booking.service = service
            booking.service_provider = provider
            booking.save()
            return redirect('booking_list')
    else:
        form = BookingForm(initial={'service': service, 'service_provider': provider})

    return render(request, 'booking_confirm.html', {'form': form, 'service': service, 'provider': provider})


# __init__.py
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

# review.cpython-311.pyc
Д

    l9fv  с                   зT   Ќ d dl mZmZmZ ddlmZ ddlmZ d dlm	Z	 e	dё д   Ф         Z
dS )ж    )┌render┌redirect┌get_object_or_404ж   )┌
ReviewForm)┌Service)┌login_requiredc                 зе  Ќ t          t          |гд  Ф        }| j        dk    rљt          | j        д  Ф        }|а                    д   Ф         rS|а                    dгд  Ф        }| j        |_        ||_        |а                    д   Ф          t          d|j
        гд  Ф        S t          | d||dd	юд  Ф        S t          д   Ф         }t          | d||d
юд  Ф        S )N)┌id┌POSTF)┌commit┌service_reviews)┌
service_idzadd_review.htmlzForm is not valid)┌form┌service┌error)r   r   )r   r   ┌methodr   r   ┌is_valid┌save┌userr   r   r   r   )┌requestr   r   r   ┌reviews        ЩBW:\Study\000 Diplom\Project\booking_system\booking\views\review.py┌
add_reviewr      s╩   ђ тЦеJл7Л7н7ђGпё~ўмлПў'ю,Л'н'ѕпЈ=і=Ѕ?ї?­ 	xпЌYњYаeљYЛ,н,ѕFп!ю,ѕFїKп$ѕFїNпЈKіKЅMїMѕMПл-И'╝*лEЛEнEлEтў'л#4ИtлPWлbuл6vл6vЛwнwлwтЅ|ї|ѕПљ'л,░t╚л.Pл.PЛQнQлQз    N)┌django.shortcutsr   r   r   ┌formsr   ┌modelsr   ┌django.contrib.auth.decoratorsr	   r   Е r   r   Щ<module>r!      sЂ   ­п @л @л @л @л @л @л @л @л @л @п л л л л л п л л л л л п 9л 9л 9л 9л 9л 9Я­R­ Rы ё­R­ R­ Rr   

# __init__.cpython-311.pyc
Д

    u9fш  с                   зX   Ќ d dl mZ ddlT ddlT dё Zdё Zdё Zdё Zdё Zd	ё Z	d
ё Z
dё Zdё Zd
S )ж    Е┌renderж   )┌*c                 з"   Ќ t          | dд  Ф        S )Nz	main.htmlr   Е┌requests    ЩDW:\Study\000 Diplom\Project\booking_system\booking\views\__init__.py┌	main_pager      s   ђ Пљ'ў;Л'н'л'з    c                 з"   Ќ t          | dд  Ф        S )Nz
about_us.htmlr   r   s    r
   ┌about_usr   
   s   ђ Пљ'ў?Л+н+л+r   c                  з>   Ќ t           j        а                    д   Ф         S ЕN)┌Customer┌objects┌allЕ r   r
   ┌
get_customersr      s   ђ ПнОмЛ!н!л!r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌
Administratorr   r   r   r   r
   ┌get_administratorsr      s   ђ Пн О$м$Л&н&л&r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌ServiceProviderr   r   r   r   r
   ┌get_service_providersr      s   ђ Пн"О&м&Л(н(л(r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌Servicer   r   r   r   r
   ┌get_servicesr      з   ђ Пї?ОмЛ н л r   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌Reviewr   r   r   r   r
   ┌get_reviewsr"   !   s   ђ Пї>ОмЛнлr   c                  з>   Ќ t           j        а                    д   Ф         S r   )┌Bookingr   r   r   r   r
   ┌get_bookingsr%   %   r   r   c                 зк   Ќ t          д   Ф         t          д   Ф         t          д   Ф         t          д   Ф         t	          д   Ф         t          д   Ф         dю}t
          | d|д  Ф        S )N)┌	customers┌administrators┌service_providers┌services┌reviews┌bookingszlist_all_db.html)r   r   r   r   r"   r%   r   )r	   ┌contexts     r
   ┌list_all_dbr.   )   sQ   ђ т"Љ_ћ_П,Л.н.П2Л4н4П ЉNћNПЉ=ћ=П ЉNћN­
­ ђGш љ'л-еwЛ7н7л7r   N)
┌django.shortcutsr   ┌models┌viewsr   r   r   r   r   r   r"   r%   r.   r   r   r
   Щ<module>r2      s└   ­п #л #л #л #л #л #Я л л л п л л л ­(­ (­ (­
,­ ,­ ,­"­ "­ "­'­ '­ '­)­ )­ )­!­ !­ !­ ­  ­  ­!­ !­ !­	8­ 	8­ 	8­ 	8­ 	8r   

# about_us.html
{% extends 'base.html' %}

{% block title %}About Us - Beauty Saloon{% endblock %}

{% block content %}
<div class="header-content">
    <h1>About Us</h1>
    <p>Welcome to our Beauty Saloon. Here you can find the best services for your beauty needs. Our team is professional and highly skilled.</p>
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
    <div class="nav-container">
        <ul>
            <li><a href="{% url 'main' %}" class="nav-link">Главная</a></li>
            <li><a href="{% url 'about_us' %}" class="nav-link">О салоне</a></li>
            <li><a href="{% url 'services' %}" class="nav-link">Наши услуги</a></li>
            {% if request.user.is_authenticated %}
            <li><a href="{% url 'user_profile' %}" class="nav-link">Профиль</a></li>
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


# booking_confirm.html
{% extends 'base.html' %}

{% block content %}
<div class="booking-confirm-container">
    <h1>Confirm Booking for {{ service.name }} with {{ provider.user.username }}</h1>
    <form method="post" action="">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Confirm Booking</button>
    </form>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var yearSelect = document.getElementById('id_year');
    var monthSelect = document.getElementById('id_month');
    var daySelect = document.getElementById('id_day');
    var hourSelect = document.getElementById('id_hour');

    function updateMonths() {
        var year = yearSelect.value;
        var currentYear = new Date().getFullYear();
        var currentMonth = new Date().getMonth() + 1;

        monthSelect.innerHTML = '';

        for (var i = 1; i <= 12; i++) {
            if (year == currentYear && i < currentMonth) continue;

            var option = document.createElement('option');
            option.text = i;
            option.value = i;
            monthSelect.add(option);
        }
    }

    function updateDays() {
        var year = yearSelect.value;
        var month = monthSelect.value;
        var currentYear = new Date().getFullYear();
        var currentMonth = new Date().getMonth() + 1;
        var currentDay = new Date().getDate();

        daySelect.innerHTML = '';

        var day = new Date(year, month, 0).getDate();

        for (var i = 1; i <= day; i++) {
            if (year == currentYear && month == currentMonth && i < currentDay) continue;

            var option = document.createElement('option');
            option.text = i;
            option.value = i;
            daySelect.add(option);
        }
    }

    function updateHours() {
        hourSelect.innerHTML = '';

        for (var i = 9; i <= 19; i++) {
            var option = document.createElement('option');
            option.text = i;
            option.value = i;
            hourSelect.add(option);
        }
    }

    yearSelect.addEventListener('change', function() {
        updateMonths();
        updateDays();
    });
    monthSelect.addEventListener('change', updateDays);
    daySelect.addEventListener('change', updateHours);

    updateMonths();
    updateDays();
    updateHours();
});
</script>
{% endblock %}


# booking_form.html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>Book a Service</h1>
    {% if not provider_form %}
        <form method="post" action="">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">Select Date and Time</button>
        </form>
    {% else %}
        <form method="post" action="">
            {% csrf_token %}
            {{ provider_form.as_p }}
            <button type="submit" class="btn btn-primary">Select Provider and Book</button>
        </form>
    {% endif %}
</div>
{% endblock %}

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


# login.html
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


# main.html
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


# select_provider.html
{% extends 'base.html' %}

{% block content %}
<div class="providers-container">
    <h1>Select a Provider for {{ service.name }}</h1>
    {% for provider in providers %}
    <div class="provider-item">
        <p>{{ provider.user.username }} - {{ provider.specialization }}</p>
        <form method="get" action="{% url 'booking_confirm' service.id provider.id %}">
            <button type="submit">Select</button>
        </form>
    </div>
    {% endfor %}
</div>
{% endblock %}


# services.html
{% extends 'base.html' %}

{% block content %}
<div class="services-container">
    {% for service in services %}
    <div class="service-item">
        <h2>{{ service.name }}</h2>
        <p>{{ service.description }}</p>
        <p>Duration: {{ service.duration }}</p>
        <p>Price: {{ service.price }}</p>
        <form method="get" action="{% url 'book_service' service.id %}">
            <button type="submit">Book</button>
        </form>
    </div>
    {% endfor %}
</div>
{% endblock %}


# signup.html
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


# user_booking.html
{% extends 'base.html' %}

{% block content %}
<div class="page-header">
    <h1>История заказов</h1>
</div>
<table>
    <thead>
        <tr>
            <th>Услуга</th>
            <th>Мастер</th>
            <th>Полная и время предоставления услуги</th>
            <th>Действия</th>
        </tr>
    </thead>
    <tbody>
        {% for booking in bookings %}
        <tr>
            <td>{{ booking.service.name }}</td>
            <td>{{ booking.service_provider.user.username }}</td>
            <td>{{ booking.appointment_datetime|date:"Y-m-d H:i" }}</td>
            <td>
                <a href="{% url 'user_booking_update' booking.id %}">Изменить</a>
                <a href="{% url 'user_booking_delete' booking.id %}">Удалить заказ</a>
            </td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="4">Нет заказов.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}


# user_profile.html
{% extends 'base.html' %}

{% block content %}
<div>
    <h1>User Profile</h1>
    <p>Welcome, {{ user.username }}!</p>
    <a href="{% url 'user_booking_list' %}">View Your Bookings</a>
</div>
{% endblock %}


