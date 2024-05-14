from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run migrations and all fill scripts for customers, administrators, and service providers'

    def handle(self, *args, **options):
        # Run makemigrations and migrate to ensure the database is up to date
        self.stdout.write(self.style.SUCCESS('Running makemigrations...'))
        call_command('makemigrations')
        call_command('makemigrations', 'booking')
        self.stdout.write(self.style.SUCCESS('Running migrate...'))
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('Database migration completed.'))

        # Call fill_customers command
        self.stdout.write(self.style.SUCCESS('Starting to fill customers...'))
        call_command('fill_customers')
        self.stdout.write(self.style.SUCCESS('Finished filling customers.'))

        # Call fill_administrators command
        self.stdout.write(self.style.SUCCESS('Starting to fill administrators...'))
        call_command('fill_administrators')
        self.stdout.write(self.style.SUCCESS('Finished filling administrators.'))

        # Call fill_managers command
        self.stdout.write(self.style.SUCCESS('Starting to fill managers...'))
        call_command('fill_managers')
        self.stdout.write(self.style.SUCCESS('Finished filling managers.'))

        # Call fill_service_providers command
        self.stdout.write(self.style.SUCCESS('Starting to fill service providers...'))
        call_command('fill_service_providers')
        self.stdout.write(self.style.SUCCESS('Finished filling service providers.'))

        # Call fill_services command
        self.stdout.write(self.style.SUCCESS('Starting to fill services...'))
        call_command('fill_services')
        self.stdout.write(self.style.SUCCESS('Finished filling services.'))

        self.stdout.write(self.style.SUCCESS('Starting to fill reviews...'))
        call_command('fill_reviews')
        self.stdout.write(self.style.SUCCESS('Finished filling reviews.'))

        self.stdout.write(self.style.SUCCESS('Starting to fill bookings...'))
        call_command('fill_bookings')
        self.stdout.write(self.style.SUCCESS('Finished filling bookings.'))

        self.stdout.write(self.style.SUCCESS('Starting to fill manytomany...'))
        call_command('fill_manytomany')
        self.stdout.write(self.style.SUCCESS('Finished filling manytomany.'))
