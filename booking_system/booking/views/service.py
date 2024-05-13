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
