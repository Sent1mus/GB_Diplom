from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Booking, Review, Service
from ..forms import ReviewForm


@login_required  # Ensures that only authenticated users can access this view
def add_review(request, booking_id):
    # Retrieve the booking object, or return a 404 error if not found
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        # Try to retrieve an existing review for the booking
        review = Review.objects.get(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = True  # Flag to indicate that this is an update operation
    except Review.DoesNotExist:
        # If no review exists, create a new review instance
        review = Review(booking=booking)
        form = ReviewForm(request.POST or None, instance=review)
        update = False  # Flag to indicate that this is a create operation

    if request.method == 'POST':
        if form.is_valid():
            # Save the form data to the review object
            review = form.save(commit=False)
            if not update:
                # Set additional fields if this is a new review
                review.customer = booking.customer
                review.service = booking.service
                review.service_provider = booking.service_provider
            review.save()  # Save the review to the database
            return redirect('list_booking')  # Redirect to the booking list after saving
        else:
            # If the form is not valid, render the page again with the form
            return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})
    else:
        # If not a POST request, render the page with the form
        return render(request, 'profile/user_review.html', {'form': form, 'booking_id': booking_id})


def service_reviews(request, service_id):
    # Retrieve the service object, or return a 404 error if not found
    service = get_object_or_404(Service, id=service_id)
    # Retrieve all reviews related to the service
    reviews = Review.objects.filter(booking__service=service).select_related('booking', 'booking__customer')
    # Render the reviews page with the service and its reviews
    return render(request, 'reviews.html', {'service': service, 'reviews': reviews})
