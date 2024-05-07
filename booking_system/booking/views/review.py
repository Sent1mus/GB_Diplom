from django.shortcuts import render, redirect, get_object_or_404
from ..forms import ReviewForm
from ..models import Service
from django.contrib.auth.decorators import login_required

@login_required
def add_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.service = service
            review.save()
            return redirect('service_reviews', service_id=service.id)
        else:
            return render(request, 'add_review.html', {'form': form, 'service': service, 'error': 'Form is not valid'})
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'service': service})
