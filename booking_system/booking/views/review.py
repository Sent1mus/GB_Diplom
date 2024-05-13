from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Booking, Review, Service
from ..forms import ReviewForm


@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        # Try to get an existing review
        review = Review.objects.get(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = True  # Flag to indicate updating an existing review
    except Review.DoesNotExist:
        # If no review exists, create a new one
        review = Review(booking=booking)  # Initialize review with booking
        form = ReviewForm(request.POST or None, instance=review)
        update = False

    if request.method == 'POST':
        if form.is_valid():
            review = form.save(commit=False)
            if not update:
                # Set foreign keys only if it's a new review
                review.customer = booking.customer  # Assuming customer field exists in Booking
                review.service = booking.service  # Assuming service field exists in Booking
                review.service_provider = booking.service_provider  # Assuming service_provider field exists in Booking
            review.save()
            return redirect('list_booking')  # Redirect to a suitable page after saving
        else:
            return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})
    else:
        return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})


def service_reviews(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reviews = Review.objects.filter(booking__service=service).select_related('booking', 'booking__customer')
    return render(request, 'reviews.html', {'service': service, 'reviews': reviews})
