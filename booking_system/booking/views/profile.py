from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EditProfileForm
from ..models import Customer
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def user_profile(request):
    customer = Customer.objects.get(user=request.user)
    form = EditProfileForm(instance=customer)
    password_form = PasswordChangeForm(request.user)
    return render(request, 'profile/user_profile.html', {
        'form': form,
        'password_form': password_form
    })

@login_required
def edit_profile(request):
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        return redirect('user_profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('user_profile')
    else:
        return redirect('user_profile')

@login_required
def deactivate_profile(request):
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        customer.is_active = False
        customer.save()
        return redirect('logout')
    else:
        return redirect('user_profile')
