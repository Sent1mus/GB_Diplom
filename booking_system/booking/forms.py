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
