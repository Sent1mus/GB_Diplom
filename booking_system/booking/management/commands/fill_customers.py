from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Customer
import random

class Command(BaseCommand):
    help = 'Fills the Customer database with dummy data'

    def handle(self, *args, **options):
        # Number of customers to create
        num_customers = 10  # You can change this number as needed

        for i in range(num_customers):
            # Create a user for each customer
            username = f'user{i}'
            first_name = f'First{i}'
            last_name = f'Last{i}'
            email = f'user{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333222{i}'

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Create a customer linked to the user
            Customer.objects.create(
                user=user,
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created customer {username}'))
