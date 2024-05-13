from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from ..models import Customer
from ..forms import CustomPasswordChangeForm
import json


# View for displaying user profile
@login_required
def user_profile(request):
    customer = Customer.objects.get(user=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'profile/user_profile.html', {
        'password_form': password_form
    })


# View for updating user profile fields
@login_required
@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        customer = Customer.objects.get(user=request.user)

        if field == 'email':
            customer.user.email = value
            customer.user.save()
        elif field == 'phone':
            customer.phone = value
            customer.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# View for changing user password
@login_required
@csrf_exempt
def change_user_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomPasswordChangeForm(user=request.user, data=data)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session to prevent logout
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})


# View for deactivating a user profile
@login_required
@csrf_exempt
def deactivate_user_profile(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        customer.user.is_active = False
        customer.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
