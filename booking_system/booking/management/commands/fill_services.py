from datetime import timedelta
from django.core.management.base import BaseCommand
from booking.models import Service

class Command(BaseCommand):
    help = 'Ensures specific services are in the Service database'

    def handle(self, *args, **options):
        # Define a list of services with their details
        services_data = [
            {
                'name': 'Haircut',
                'description': 'Basic haircut',
                'duration': timedelta(hours=0, minutes=30),
                'price': 1000.00
            },
            {
                'name': 'Manicure',
                'description': 'Nail shaping and cuticle care',
                'duration': timedelta(hours=1, minutes=0),
                'price': 2000.00
            },
            {
                'name': 'Facial',
                'description': 'Skin cleansing and facial treatment',
                'duration': timedelta(hours=1, minutes=30),
                'price': 3000.00
            }
        ]

        # Iterate over the services data
        for service_data in services_data:
            # Use get_or_create to avoid creating duplicate entries
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'duration': service_data['duration'],
                    'price': service_data['price']
                }
            )

            # Check if the service was created or fetched
            if created:
                message = f'Successfully created service {service.name}'
            else:
                message = f'Service {service.name} already exists'

            # Print success message
            self.stdout.write(self.style.SUCCESS(message))
