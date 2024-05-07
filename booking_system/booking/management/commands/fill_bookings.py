from django.core.management.base import BaseCommand
from booking.models import Booking, Service, Customer, ServiceProvider
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Fills the Booking database with structured data'

    def handle(self, *args, **options):
        customers = Customer.objects.all()
        services = list(Service.objects.all())
        service_providers = list(ServiceProvider.objects.all())

        if len(services) < 3 or len(service_providers) < 3:
            self.stdout.write(self.style.ERROR('Not enough services or service providers to assign 3 each.'))
            return

        for customer in customers:
            for i in range(3):  # Create 3 bookings per customer
                service = services[i % len(services)]
                service_provider = service_providers[i % len(service_providers)]
                days_ahead = i * 7  # Bookings spaced one week apart
                appointment_datetime = timezone.now() + timezone.timedelta(days=days_ahead)

                # Randomize the creation date within the past year
                days_back = random.randint(0, 365)  # Random number of days up to a year back
                created_at = timezone.now() - timezone.timedelta(days=days_back)  # Subtract days to go back in time

                Booking.objects.create(
                    customer=customer,
                    service=service,
                    service_provider=service_provider,
                    appointment_datetime=appointment_datetime,
                    created_at=created_at  # Added the created_at field with a random date within the last year
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created booking {i+1} for {customer.user.username} with {service.name} at {appointment_datetime}, created on {created_at}'))
