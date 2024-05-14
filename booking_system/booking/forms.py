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
