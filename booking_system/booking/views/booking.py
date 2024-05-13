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
        # Attempt to retrieve the customer profile associated with the current user
        customer_profile = Customer.objects.get(user=user)
        # Retrieve all bookings associated with the customer profile
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        # If no customer profile exists, return an empty list of bookings
        bookings = []
    # Render the booking list page with the bookings and current time
    return render(request, 'profile/user_booking.html', {'bookings': bookings, 'now': now})


@login_required
def user_booking_update(request, pk):
    # Retrieve the booking object or return a 404 error if not found
    booking = get_object_or_404(Booking, pk=pk)
    error_message = None

    if request.method == 'POST':
        form = BookingDateTimeForm(request.POST)
        if form.is_valid():
            # Extract the new appointment datetime from the form data
            new_appointment_datetime = form.cleaned_data['appointment_datetime']
            # Check if the new appointment time slot is available
            if BookingValidator.is_slot_available(booking.service_provider_id, new_appointment_datetime):
                # Update the booking with the new appointment datetime and save it
                booking.appointment_datetime = new_appointment_datetime
                booking.save()
                # Redirect to the booking list view after successful update
                return redirect('list_booking')
            else:
                # Set error message if the time slot is not available
                error_message = "This time slot is not available. Please choose another time."
        # Render the update form again with the error message if form is not valid or time slot not available
        return render(request, 'profile/user_booking_update.html', {'form': form, 'error_message': error_message})
    else:
        # Pre-fill the form with the existing booking details
        form = BookingDateTimeForm(initial={
            'month': booking.appointment_datetime.month,
            'day': booking.appointment_datetime.day,
            'hour': booking.appointment_datetime.hour,
        })
    # Render the update form
    return render(request, 'profile/user_booking_update.html', {'form': form, 'error_message': error_message})


# Ensure the user is authenticated before allowing access to the view
@login_required
def user_booking_delete(request, pk):
    if request.method == 'POST':
        # Retrieve the booking object or return a 404 error if not found
        booking = get_object_or_404(Booking, pk=pk)
        # Delete the booking
        booking.delete()
        # Return a success response
        return JsonResponse({'status': 'success'}, status=200)
    # Return an error response if not accessed via POST
    return JsonResponse({'status': 'error'}, status=400)
