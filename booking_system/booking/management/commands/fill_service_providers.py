from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import ServiceProvider
import random

class Command(BaseCommand):
    help = 'Fills the ServiceProvider database with dummy data'

    def handle(self, *args, **options):
        # Number of service providers to create
        num_service_providers = 8  # You can change this number as needed

        for i in range(num_service_providers):
            # Create a user for each service provider
            username = f'master{i}'
            first_name = f'MasterFirst{i}'
            last_name = f'MasterLast{i}'
            email = f'master{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333221{i}'
            specialization = f'Specialization{i}'

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Create a service provider linked to the user
            ServiceProvider.objects.create(
                user=user,
                phone=phone,
                specialization=specialization
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created service provider {username}'))
