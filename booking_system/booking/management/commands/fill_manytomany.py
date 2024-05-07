from django.core.management.base import BaseCommand
from booking.models import ServiceProvider, Service
import random

class Command(BaseCommand):
    help = 'Populates the many-to-many relationship between Service and ServiceProvider'

    def handle(self, *args, **options):
        # Fetch all service providers and services
        service_providers = list(ServiceProvider.objects.all())
        services = list(Service.objects.all())

        if not service_providers or not services:
            self.stdout.write(self.style.ERROR('No service providers or services found. Please add some first.'))
            return

        # Optionally clear existing relationships
        for provider in service_providers:
            provider.service.clear()

        # Randomly assign services to each service provider
        for provider in service_providers:
            # Randomly choose a number of services to assign
            assigned_services = random.sample(services, k=random.randint(1, len(services)))
            provider.service.add(*assigned_services)
            provider.save()  # Save the changes

            self.stdout.write(self.style.SUCCESS(f'Assigned {len(assigned_services)} services to {provider.user.username}'))

