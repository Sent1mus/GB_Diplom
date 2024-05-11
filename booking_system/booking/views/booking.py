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
