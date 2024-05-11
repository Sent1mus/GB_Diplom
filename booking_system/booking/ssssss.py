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
    # path('ajax/get_available_times/', get_available_times, name='get_available_times'),
    # path('services/book/<int:service_id>/', book_service, name='book_service'),
    # path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    # path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
    path('profile/booking/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('profile/booking/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),
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
        input_formats=['%d.%m.%Y'],  # Ожидаемый формат даты
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
                birth_date=self.cleaned_data['birth_date']  # Сохраняем дату рождения
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


class CustomModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        # Устанавливаем плейсхолдер с помощью empty_label
        kwargs['empty_label'] = "Выберите мастера"
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """ Форматирует отображаемое имя для объектов ServiceProvider. """
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.specialization}"


class ServiceProviderForm(forms.Form):
    service_provider = CustomModelChoiceField(
        queryset=ServiceProvider.objects.all(),
        widget=forms.Select(attrs={'id': 'service_provider'}),
        label="Select Service Provider"
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
    day = forms.ChoiceField(choices=[(i, i) for i in range(1, calendar.monthrange(current_year, current_month)[1] + 1)], initial=current_day)
    hour = forms.ChoiceField(choices=[(i, i) for i in range(9, 21)], initial=current_hour if 9 <= current_hour <= 20 else 9)

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


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

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


# profile.py
# views.py
from django.shortcuts import render, redirect
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
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import datetime

from . import BookingValidator
from ..forms import ServiceProviderForm, BookingDateTimeForm
from ..models import Service, Booking


def is_slot_available(service_provider_id, appointment_datetime):
    # Assuming each booking lasts for 1 hour
    end_time = appointment_datetime + datetime.timedelta(hours=1)
    overlapping_bookings = Booking.objects.filter(
        service_provider_id=service_provider_id,
        appointment_datetime__lt=end_time,
        appointment_datetime__gte=appointment_datetime
    ).exists()
    return not overlapping_bookings

@login_required
def services(request):
    services = Service.objects.all()
    forms_list = []

    for service in services:
        provider_form = ServiceProviderForm(prefix=f"service_{service.id}")
        date_time_form = BookingDateTimeForm(prefix=f"service_{service.id}")
        if request.method == 'POST':
            provider_form = ServiceProviderForm(request.POST, prefix=f"service_{service.id}")
            date_time_form = BookingDateTimeForm(request.POST, prefix=f"service_{service.id}")
            if provider_form.is_valid() and date_time_form.is_valid():
                service_provider = provider_form.cleaned_data['service_provider']
                appointment_datetime = date_time_form.cleaned_data['appointment_datetime']
                service_id = request.POST.get('service_id')
                service = Service.objects.get(id=service_id)

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
                    # Сохраняем текущие данные формы для повторного использования
                    current_data = {
                        'service_provider': provider_form.cleaned_data['service_provider'],
                        'appointment_datetime': date_time_form.cleaned_data['appointment_datetime']
                    }
                    forms_list.append((service, provider_form, date_time_form, "This slot is not available. Please choose another time.", current_data))
                    continue

        forms_list.append((service, provider_form, date_time_form, None, None))

    return render(request, 'services.html', {
        'forms_list': forms_list,
    })


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
        # Предполагаем, что каждое бронирование длится 1 час
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

# review.cpython-311.pyc
Д

    l9fv  с                   зT   Ќ d dl mZmZmZ ddlmZ ddlmZ d dlm	Z	 e	dё д   Ф         Z
dS )ж    )┌render┌redirect┌get_object_or_404ж   )┌
ReviewForm)┌Service)┌login_requiredc                 зе  Ќ t          t          |гд  Ф        }| j        dk    rљt          | j        д  Ф        }|а                    д   Ф         rS|а                    dгд  Ф        }| j        |_        ||_        |а                    д   Ф          t          d|j
        гд  Ф        S t          | d||dd	юд  Ф        S t          д   Ф         }t          | d||d
юд  Ф        S )N)┌id┌POSTF)┌commit┌service_reviews)┌
service_idzadd_review.htmlzForm is not valid)┌form┌service┌error)r   r   )r   r   ┌methodr   r   ┌is_valid┌save┌userr   r   r   r   )┌requestr   r   r   ┌reviews        ЩBW:\Study\000 Diplom\Project\booking_system\booking\views\review.py┌
add_reviewr      s╩   ђ тЦеJл7Л7н7ђGпё~ўмлПў'ю,Л'н'ѕпЈ=і=Ѕ?ї?­ 	xпЌYњYаeљYЛ,н,ѕFп!ю,ѕFїKп$ѕFїNпЈKіKЅMїMѕMПл-И'╝*лEЛEнEлEтў'л#4ИtлPWлbuл6vл6vЛwнwлwтЅ|ї|ѕПљ'л,░t╚л.Pл.PЛQнQлQз    N)┌django.shortcutsr   r   r   ┌formsr   ┌modelsr   ┌django.contrib.auth.decoratorsr	   r   Е r   r   Щ<module>r!      sЂ   ­п @л @л @л @л @л @л @л @л @л @п л л л л л п л л л л л п 9л 9л 9л 9л 9л 9Я­R­ Rы ё­R­ R­ Rr   

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
    # path('ajax/get_available_times/', get_available_times, name='get_available_times'),
    # path('services/book/<int:service_id>/', book_service, name='book_service'),
    # path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    # path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
    path('profile/booking/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('profile/booking/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),
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
        input_formats=['%d.%m.%Y'],  # Ожидаемый формат даты
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
                birth_date=self.cleaned_data['birth_date']  # Сохраняем дату рождения
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


class CustomModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        # Устанавливаем плейсхолдер с помощью empty_label
        kwargs['empty_label'] = "Выберите мастера"
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """ Форматирует отображаемое имя для объектов ServiceProvider. """
        return f"{obj.user.first_name} {obj.user.last_name} - {obj.specialization}"


class ServiceProviderForm(forms.Form):
    service_provider = CustomModelChoiceField(
        queryset=ServiceProvider.objects.all(),
        widget=forms.Select(attrs={'id': 'service_provider'}),
        label="Select Service Provider"
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
    day = forms.ChoiceField(choices=[(i, i) for i in range(1, calendar.monthrange(current_year, current_month)[1] + 1)], initial=current_day)
    hour = forms.ChoiceField(choices=[(i, i) for i in range(9, 21)], initial=current_hour if 9 <= current_hour <= 20 else 9)

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


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

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


# profile.py
# views.py
from django.shortcuts import render, redirect
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
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import datetime

from . import BookingValidator
from ..forms import ServiceProviderForm, BookingDateTimeForm
from ..models import Service, Booking


def is_slot_available(service_provider_id, appointment_datetime):
    # Assuming each booking lasts for 1 hour
    end_time = appointment_datetime + datetime.timedelta(hours=1)
    overlapping_bookings = Booking.objects.filter(
        service_provider_id=service_provider_id,
        appointment_datetime__lt=end_time,
        appointment_datetime__gte=appointment_datetime
    ).exists()
    return not overlapping_bookings

@login_required
def services(request):
    services = Service.objects.all()
    forms_list = []

    for service in services:
        provider_form = ServiceProviderForm(prefix=f"service_{service.id}")
        date_time_form = BookingDateTimeForm(prefix=f"service_{service.id}")
        if request.method == 'POST':
            provider_form = ServiceProviderForm(request.POST, prefix=f"service_{service.id}")
            date_time_form = BookingDateTimeForm(request.POST, prefix=f"service_{service.id}")
            if provider_form.is_valid() and date_time_form.is_valid():
                service_provider = provider_form.cleaned_data['service_provider']
                appointment_datetime = date_time_form.cleaned_data['appointment_datetime']
                service_id = request.POST.get('service_id')
                service = Service.objects.get(id=service_id)

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
                    # Сохраняем текущие данные формы для повторного использования
                    current_data = {
                        'service_provider': provider_form.cleaned_data['service_provider'],
                        'appointment_datetime': date_time_form.cleaned_data['appointment_datetime']
                    }
                    forms_list.append((service, provider_form, date_time_form, "This slot is not available. Please choose another time.", current_data))
                    continue

        forms_list.append((service, provider_form, date_time_form, None, None))

    return render(request, 'services.html', {
        'forms_list': forms_list,
    })


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
        # Предполагаем, что каждое бронирование длится 1 час
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

# review.cpython-311.pyc
Д

    l9fv  с                   зT   Ќ d dl mZmZmZ ddlmZ ddlmZ d dlm	Z	 e	dё д   Ф         Z
dS )ж    )┌render┌redirect┌get_object_or_404ж   )┌
ReviewForm)┌Service)┌login_requiredc                 зе  Ќ t          t          |гд  Ф        }| j        dk    rљt          | j        д  Ф        }|а                    д   Ф         rS|а                    dгд  Ф        }| j        |_        ||_        |а                    д   Ф          t          d|j
        гд  Ф        S t          | d||dd	юд  Ф        S t          д   Ф         }t          | d||d
юд  Ф        S )N)┌id┌POSTF)┌commit┌service_reviews)┌
service_idzadd_review.htmlzForm is not valid)┌form┌service┌error)r   r   )r   r   ┌methodr   r   ┌is_valid┌save┌userr   r   r   r   )┌requestr   r   r   ┌reviews        ЩBW:\Study\000 Diplom\Project\booking_system\booking\views\review.py┌
add_reviewr      s╩   ђ тЦеJл7Л7н7ђGпё~ўмлПў'ю,Л'н'ѕпЈ=і=Ѕ?ї?­ 	xпЌYњYаeљYЛ,н,ѕFп!ю,ѕFїKп$ѕFїNпЈKіKЅMїMѕMПл-И'╝*лEЛEнEлEтў'л#4ИtлPWлbuл6vл6vЛwнwлwтЅ|ї|ѕПљ'л,░t╚л.Pл.PЛQнQлQз    N)┌django.shortcutsr   r   r   ┌formsr   ┌modelsr   ┌django.contrib.auth.decoratorsr	   r   Е r   r   Щ<module>r!      sЂ   ­п @л @л @л @л @л @л @л @л @л @п л л л л л п л л л л л п 9л 9л 9л 9л 9л 9Я­R­ Rы ё­R­ R­ Rr   

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
    <p>© 2024 Beauty Saloon. Все права защищены.</p>
    {% block footer %}
    {% endblock %}
</footer>
{% block javascript %}
{% endblock %}
</body>
</html>


# DELETE_booking_confirm.html
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


# DELETE_booking_form.html
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

# DELETE_select_provider.html
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
<!-- TODO DELETE IF NOT NEEDED
<script>
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('#service_provider').forEach(providerSelect => {
            providerSelect.addEventListener('change', function() {
                var providerId = this.value;
                var serviceId = this.closest('form').querySelector('input[name="service_id"]').value;
                var dateTimeForm = document.getElementById('date_time_form_' + serviceId);
                fetch(`/ajax/get_available_times/?provider_id=${providerId}`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }).then(response => response.json())
                .then(data => {
                    dateTimeForm.style.display = 'block';
                    updateDateTimeFormFields(data, serviceId);
                }).catch(error => console.error('Error:', error));
            });
        });
    });

    function updateDateTimeFormFields(data, serviceId) {
        const fields = ['month', 'day', 'hour']; // Updated fields array
        fields.forEach(field => {
            const selectElement = document.getElementById('id_' + field + '_' + serviceId);
            if (!selectElement) {
                console.error(`Select element not found for ${field} and service ID ${serviceId}`);
                return;
            }
            selectElement.innerHTML = ''; // Clear existing options
            data[field + 's'].forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.text = option;
                selectElement.appendChild(optionElement);
            });
        });
    }
</script>
-->
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
                        <a>Нельзя изменить или удалить данный заказ</a>
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
<script>
    function confirmDelete(e, element) {
    e.preventDefault();
    var bookingId = element.getAttribute('data-id');
    if (confirm('Are you sure you want to delete this booking?')) {
        fetch(`/profile/booking/delete/${bookingId}/`, {  // Added trailing slash here
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Something went wrong');
        })
        .then(data => {
            alert('Booking deleted successfully');
            window.location.reload();  // Reload the page or remove the element from DOM
        })
        .catch(error => console.error('Error:', error));
    }
}

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
</script>
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
<script>
    alert("{{ error_message|escapejs }}");
</script>
{% endif %}
{% endblock %}


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

<script src="../static/js/user_profile.js"></script>
{% endblock %}


