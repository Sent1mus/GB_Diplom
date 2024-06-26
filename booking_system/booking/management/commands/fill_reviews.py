from django.core.management.base import BaseCommand
from booking.models import Booking, Review, Service, Customer, ServiceProvider
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fills the Review database with structured data'

    def handle(self, *args, **options):
        customers = Customer.objects.all()
        services = list(Service.objects.all())
        service_providers = list(ServiceProvider.objects.all())

        if len(services) < 3 or len(service_providers) < 3:
            self.stdout.write(self.style.ERROR('Not enough services or service providers to assign 3 each.'))
            return

        for customer in customers:
            for i in range(3):  # Create 3 bookings and reviews per customer
                service = services[i % len(services)]
                service_provider = service_providers[i % len(service_providers)]

                # Create a booking
                booking = Booking.objects.create(
                    customer=customer,
                    service=service,
                    service_provider=service_provider,
                    appointment_datetime=timezone.now()  # Set the appointment time to now for simplicity
                )

                # Create a review for the booking
                Review.objects.create(
                    booking=booking,
                    rating=i % 5 + 1,  # Simple pattern for rating
                    comment=f'Review {i + 1} by {customer.user.username} for {service.name}'
                )

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created review {i + 1} by {customer.user.username} for {service.name}'))
