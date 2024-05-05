from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Administrator
import random

class Command(BaseCommand):
    help = 'Fills the Administrator database with dummy data'

    def handle(self, *args, **options):
        # Number of administrators to create
        num_administrators = 5  # You can change this number as needed

        for i in range(num_administrators):
            # Create a user for each administrator
            username = f'admin{i}'
            first_name = f'AdminFirst{i}'
            last_name = f'AdminLast{i}'
            email = f'admin{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333220{i}'

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Create an administrator linked to the user
            Administrator.objects.create(
                user=user,
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created administrator {username}'))
