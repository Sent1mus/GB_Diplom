from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Administrator

class Command(BaseCommand):
    help = 'Fills the Administrator database with dummy data'

    def handle(self, *args, **options):
        # Number of administrators to create
        num_administrators = 3

        for i in range(num_administrators):
            # Create a user for each administrator
            username = f'admin{i}'
            first_name = f'AdminFirst{i}'
            last_name = f'AdminLast{i}'
            email = f'admin{i}@example.com'
            password = 'password'
            phone = f'7927333111{i}'
            birth_date = f'200{i}-01-0{i+1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.is_staff = True  # Mark the user as staff
            user.save()

            Administrator.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone
            )
            # Create an administrator linked to the user

            self.stdout.write(self.style.SUCCESS(f'Successfully created administrator {username}'))
