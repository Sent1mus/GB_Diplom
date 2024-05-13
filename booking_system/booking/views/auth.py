from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from ..forms import RegisterForm


def signup(request):
    # Handle user signup
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user
            login(request, user)  # Log in the new user
            return redirect('/profile/')  # Redirect to profile page after signup
        else:
            return render(request, 'signup.html', {'form': form})  # Re-render the signup form with errors
    else:
        form = RegisterForm()
        return render(request, 'signup.html', {'form': form})  # Display the empty signup form


def user_login(request):
    # Handle user login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Authenticate user
        if user is not None:
            login(request, user)  # Log in the user
            return redirect('main')  # Redirect to main page after login
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})  # Show error if login fails
    else:
        return render(request, 'login.html')  # Display the login form


def user_logout(request):
    logout(request)  # Log out the user
    return redirect('main')  # Redirect to main page after logout
