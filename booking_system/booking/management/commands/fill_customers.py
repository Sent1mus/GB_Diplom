from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Customer

class Command(BaseCommand):
    help = 'Fills the Customer database with dummy data'

    def handle(self, *args, **options):
        # Number of customers to create
        num_customers = 5

        for i in range(num_customers):
            # Create a user for each customer
            username = f'user{i}'
            first_name = f'First{i}'
            last_name = f'Last{i}'
            email = f'user{i}@example.com'
            password = 'password'
            phone = f'7927333222{i}'
            birth_date = f'200{i}-01-0{i+1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Create a customer linked to the user
            Customer.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created customer {username}'))
