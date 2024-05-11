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
