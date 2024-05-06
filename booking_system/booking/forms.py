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
