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
