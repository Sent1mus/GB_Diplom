from django.shortcuts import render
from .models import Customer, Administrator, ServiceProvider

def list_customers(request):
    customers = Customer.objects.all()
    administrator = Administrator.objects.all()
    serviceProvider = ServiceProvider.objects.all()

    # Correctly formatted context dictionary
    context = {
        'customers': customers,
        'administrator': administrator,
        'serviceProvider': serviceProvider
    }

    return render(request, 'customers_list.html', context)
