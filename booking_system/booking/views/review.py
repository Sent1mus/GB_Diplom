from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Booking, Review, Service
from ..forms import ReviewForm


@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        review = Review.objects.get(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = True
    except Review.DoesNotExist:
        review = Review(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = False

    if request.method == 'POST':
        if form.is_valid():
            review = form.save(commit=False)
            if not update:
                review.customer = booking.customer
                review.service = booking.service
                review.service_provider = booking.service_provider
            review.save()
            return redirect('list_booking')
        else:
            return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})
    else:
        return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})


def service_reviews(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reviews = Review.objects.filter(booking__service=service).select_related('booking', 'booking__customer')
    return render(request, 'reviews.html', {'service': service, 'reviews': reviews})
