from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import ServiceProvider, Service
import random

class Command(BaseCommand):
    help = 'Fills the ServiceProvider database with dummy data and assigns all services to them'

    def handle(self, *args, **options):
        # Number of service providers to create
        num_service_providers = 6  # You can change this number as needed

        # Fetch all services from the database
        all_services = list(Service.objects.all())

        for i in range(num_service_providers):
            # Create a user for each service provider
            username = f'master{i}'
            first_name = f'FirstName{i}'
            last_name = f'LastName{i}'
            email = f'master{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333221{i}'
            specialization = f'Specialization{i}'
            birth_date = f'200{i}-01-0{i+1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Create a service provider linked to the user
            service_provider = ServiceProvider.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone,
                specialization=specialization
            )

            # Assign all services to the service provider
            service_provider.service.add(*all_services)

            self.stdout.write(self.style.SUCCESS(f'Successfully created service provider {username} with all services assigned'))
