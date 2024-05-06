from datetime import timedelta
import random
from django.core.management.base import BaseCommand
from booking.models import Service

class Command(BaseCommand):
    help = 'Fills the Service database with dummy data'

    def handle(self, *args, **options):
        num_services = 10  # Number of services to create

        for i in range(num_services):
            name = f'Service{i}'
            description = f'This is a description of Service{i}'
            duration_minutes = random.randint(30, 180)  # Duration in minutes
            price = random.uniform(50.0, 500.0)

            # Create a timedelta object for duration
            duration = timedelta(minutes=duration_minutes)

            Service.objects.create(
                name=name,
                description=description,
                duration=duration,
                price=round(price, 2)
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created service {name}'))