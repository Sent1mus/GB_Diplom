# urls.py
from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import user_profile, update_profile, change_user_password, deactivate_user_profile
from .views.booking import list_booking, user_booking_update, user_booking_delete
from .views.service import *
from .views import *


urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('services/', services, name='services'),
    # path('services/book/<int:service_id>/', book_service, name='book_service'),
    # path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    # path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
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
    appointment_datetime = models.DateTimeField(default=timezone.now) #TODO удалить default после сдачи, нужно для заполнения бд коммандой
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


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        """ Форматирует отображаемое имя для объектов ServiceProvider. """
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.specialization}"

class BookingForm(forms.ModelForm):
    # Assuming these fields are already defined as shown in your initial snippet
    year = forms.ChoiceField(choices=[(i, i) for i in range(timezone.now().year, timezone.now().year + 2)])
    month = forms.ChoiceField(choices=[(i, i) for i in range(1, 13)])
    day = forms.ChoiceField(choices=[(i, i) for i in range(1, 32)])
    hour = forms.ChoiceField(choices=[(i, i) for i in range(0, 24)])
    minute = forms.ChoiceField(choices=[(i, i) for i in range(0, 60, 30)])
    service_provider = CustomModelChoiceField(queryset=ServiceProvider.objects.all())

    class Meta:
        model = Booking
        fields = ['service_provider']

    def clean(self):
        cleaned_data = super().clean()
        year = int(cleaned_data.get('year'))
        month = int(cleaned_data.get('month'))
        day = int(cleaned_data.get('day'))
        hour = int(cleaned_data.get('hour'))
        minute = int(cleaned_data.get('minute'))

        # Constructing the datetime object
        try:
            cleaned_data['appointment_datetime'] = timezone.datetime(year, month, day, hour, minute)
        except ValueError as e:
            raise forms.ValidationError("Invalid date or time: {}".format(e))

        return cleaned_data



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


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
def list_booking(request):
    user = request.user
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'profile/user_booking.html', {'bookings': bookings})

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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from ..models import Customer
from django.contrib.auth.forms import PasswordChangeForm
import json


@login_required
def user_profile(request):
    customer = Customer.objects.get(user=request.user)
    password_form = PasswordChangeForm(request.user)
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
        new_password = data.get('new_password')
        user = request.user
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Important to keep the user logged in
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@csrf_exempt
def deactivate_user_profile(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        customer.is_active = False
        customer.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


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
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from ..forms import BookingForm
from ..models import Service, Booking


@login_required
def services(request):
    services = Service.objects.all()
    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.customer = request.user.customer

        # Get service from POST data
        service_id = request.POST.get('service_id')
        booking.service = get_object_or_404(Service, pk=service_id)

        # Get service_provider from form cleaned data
        booking.service_provider = form.cleaned_data['service_provider']

        # Assume appointment_datetime is constructed correctly in the form clean method
        booking.appointment_datetime = form.cleaned_data['appointment_datetime']
        booking.save()
        return redirect('/profile/list_booking')
    return render(request, 'services.html', {'services': services, 'form': form})



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
from .views.profile import user_profile, update_profile, change_user_password, deactivate_user_profile
from .views.booking import list_booking, user_booking_update, user_booking_delete
from .views.service import *
from .views import *


urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('services/', services, name='services'),
    # path('services/book/<int:service_id>/', book_service, name='book_service'),
    # path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    # path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
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
    appointment_datetime = models.DateTimeField(default=timezone.now) #TODO удалить default после сдачи, нужно для заполнения бд коммандой
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


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        """ Форматирует отображаемое имя для объектов ServiceProvider. """
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.specialization}"

class BookingForm(forms.ModelForm):
    # Assuming these fields are already defined as shown in your initial snippet
    year = forms.ChoiceField(choices=[(i, i) for i in range(timezone.now().year, timezone.now().year + 2)])
    month = forms.ChoiceField(choices=[(i, i) for i in range(1, 13)])
    day = forms.ChoiceField(choices=[(i, i) for i in range(1, 32)])
    hour = forms.ChoiceField(choices=[(i, i) for i in range(0, 24)])
    minute = forms.ChoiceField(choices=[(i, i) for i in range(0, 60, 30)])
    service_provider = CustomModelChoiceField(queryset=ServiceProvider.objects.all())

    class Meta:
        model = Booking
        fields = ['service_provider']

    def clean(self):
        cleaned_data = super().clean()
        year = int(cleaned_data.get('year'))
        month = int(cleaned_data.get('month'))
        day = int(cleaned_data.get('day'))
        hour = int(cleaned_data.get('hour'))
        minute = int(cleaned_data.get('minute'))

        # Constructing the datetime object
        try:
            cleaned_data['appointment_datetime'] = timezone.datetime(year, month, day, hour, minute)
        except ValueError as e:
            raise forms.ValidationError("Invalid date or time: {}".format(e))

        return cleaned_data



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


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
def list_booking(request):
    user = request.user
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'profile/user_booking.html', {'bookings': bookings})

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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from ..models import Customer
from django.contrib.auth.forms import PasswordChangeForm
import json


@login_required
def user_profile(request):
    customer = Customer.objects.get(user=request.user)
    password_form = PasswordChangeForm(request.user)
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
        new_password = data.get('new_password')
        user = request.user
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Important to keep the user logged in
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@csrf_exempt
def deactivate_user_profile(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        customer.is_active = False
        customer.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


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
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from ..forms import BookingForm
from ..models import Service, Booking


@login_required
def services(request):
    services = Service.objects.all()
    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.customer = request.user.customer

        # Get service from POST data
        service_id = request.POST.get('service_id')
        booking.service = get_object_or_404(Service, pk=service_id)

        # Get service_provider from form cleaned data
        booking.service_provider = form.cleaned_data['service_provider']

        # Assume appointment_datetime is constructed correctly in the form clean method
        booking.appointment_datetime = form.cleaned_data['appointment_datetime']
        booking.save()
        return redirect('/profile/list_booking')
    return render(request, 'services.html', {'services': services, 'form': form})



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
<div style="display: flex; justify-content: center;">
    <table>
        {% for service in services %}
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
                    <div class="form-row">
                        {{ form.year }}
                        {{ form.month }}
                        {{ form.day }}
                        {{ form.hour }}
                        {{ form.minute }}
                    </div>
                    <br><br>
                    {{ form.service_provider }}
                    <button type="submit">Confirm Booking</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
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
            <th>Время предоставления услуги</th>
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
    <h1>Добро пожаловать в личный кабинет</h1>
    <div id="email-container">
        <span>Ваш Email: </span>
        <span id="email-value">{{ user.email }}</span>
        <button onclick="toggleEdit('email')">Изменить</button>
        <input type="email" id="email-input" value="{{ user.email }}" style="display:none;">
        <button onclick="save('email')" style="display:none;">Сохранить</button>
    </div>
    <div id="phone-container">
        <span>Ваш Телефон: </span>
        <span id="phone-value">{{ user.customer.phone }}</span>
        <button onclick="toggleEdit('phone')">Изменить</button>
        <input type="text" id="phone-input" value="{{ user.customer.phone }}" style="display:none;">
        <button onclick="save('phone')" style="display:none;">Сохранить</button>
    </div>
    <div>
        <span>Дата рождения: </span>
        <span>{{ user.customer.birth_date|date:"j F Y г." }}</span>
    </div>
    <button onclick="togglePasswordChange()">Изменить пароль</button>
    <div id="password-change" style="display:none;">
        <input type="password" id="new-password" placeholder="Новый пароль">
        <input type="password" id="confirm-password" placeholder="Подтвердите пароль">
        <button onclick="changePassword()">Сохранить пароль</button>
    </div>
    <button onclick="deactivateProfile()">Удалить профиль</button>
    <a href="{% url 'list_booking' %}">Просмотреть историю бронирований</a>
</div>

<!-- Hidden input to store URLs for JavaScript -->
<input type="hidden" id="updateProfileUrl" value="{% url 'update_profile' %}">
<input type="hidden" id="changePasswordUrl" value="{% url 'change_password' %}">
<input type="hidden" id="deactivateProfileUrl" value="{% url 'deactivate_profile' %}">

<script>
function getCSRFToken() {
    let cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    return null;
}

function toggleEdit(field) {
    let span = document.getElementById(field + '-value');
    let input = document.getElementById(field + '-input');
    let editButton = span.nextElementSibling;
    let saveButton = input.nextElementSibling;

    if (input.style.display === 'none') {
        span.style.display = 'none';
        input.style.display = 'inline';
        editButton.style.display = 'none';
        saveButton.style.display = 'inline';
    } else {
        span.style.display = 'inline';
        input.style.display = 'none';
        editButton.style.display = 'inline';
        saveButton.style.display = 'none';
    }
}

function save(field) {
    let input = document.getElementById(field + '-input');
    let span = document.getElementById(field + '-value');
    let value = input.value;
    let csrfToken = getCSRFToken();
    let updateProfileUrl = document.getElementById('updateProfileUrl').value;

    fetch(updateProfileUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({field: field, value: value})
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            span.textContent = value;
            toggleEdit(field);
        } else {
            alert('Ошибка при сохранении данных');
        }
    });
}

function togglePasswordChange() {
    let container = document.getElementById('password-change');
    container.style.display = container.style.display === 'none' ? 'block' : 'none';
}

function changePassword() {
    let newPassword = document.getElementById('new-password').value;
    let confirmPassword = document.getElementById('confirm-password').value;
    let csrfToken = getCSRFToken();
    let changePasswordUrl = document.getElementById('changePasswordUrl').value;

    // Проверка на пустоту пароля
    if (!newPassword.trim() || !confirmPassword.trim()) {
        alert('Пароль не может быть пустым');
        return;
    }

    // Проверка на совпадение паролей
    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }

    fetch(changePasswordUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({new_password: newPassword})
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Пароль успешно изменен');
            togglePasswordChange();
        } else {
            alert('Ошибка при изменении пароля');
        }
    });
}

function deactivateProfile() {
    let csrfToken = getCSRFToken();
    let deactivateProfileUrl = document.getElementById('deactivateProfileUrl').value;

    fetch(deactivateProfileUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    }).then(response => {
        if (response.ok) {
            window.location.href = "/logout/";
        } else {
            alert('Ошибка при удалении профиля');
        }
    });
}
</script>
{% endblock %}


