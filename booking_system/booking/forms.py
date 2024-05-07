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
