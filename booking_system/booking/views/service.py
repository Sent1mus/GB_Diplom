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
            booking.appointment_datetime = form.cleaned_data['appointment_datetime']
            booking.save()
            return redirect('user_booking_list')
    else:
        form = BookingForm(initial={'service': service, 'service_provider': provider})

    return render(request, 'booking_confirm.html', {'form': form, 'service': service, 'provider': provider})
