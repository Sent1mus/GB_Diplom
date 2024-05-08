from django.shortcuts import render, redirect, get_object_or_404
from ..forms import BookingForm
from ..models import Booking, Customer
from django.contrib.auth.decorators import login_required

@login_required
def list_booking(request):
    user = request.user
    try:
        customer_profile = Customer.objects.get(user=user)
        bookings = customer_profile.booking_set.all()
    except Customer.DoesNotExist:
        bookings = []
    return render(request, 'profile/user_booking.html', {'bookings': bookings})

@login_required
def user_booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form})

@login_required
def user_booking_delete(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return redirect('booking_list')
    else:
        return render(request, 'error.html', {'message': 'This action is only allowed via a POST request.'})
