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

