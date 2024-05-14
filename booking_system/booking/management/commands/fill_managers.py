from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Manager


class Command(BaseCommand):
    help = 'Fills the Manager database with dummy data'

    def handle(self, *args, **options):
        # Number of managers to create
        num_managers = 5  # You can change this number as needed

        for i in range(num_managers):
            # Create a user for each manager
            username = f'manager{i}'
            first_name = f'ManagerFirstName'
            last_name = f'ManagerLastName'
            email = f'manager{i}@example.com'
            password = 'password'  # You might want to generate a more secure password
            phone = f'7927333333{i}'
            birth_date = f'198{i}-01-0{i + 1}'

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.is_staff = True
            user.save()

            # Create a manager linked to the user
            Manager.objects.create(
                user=user,
                birth_date=birth_date,
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created manager {username}'))
