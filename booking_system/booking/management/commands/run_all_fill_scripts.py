from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run migrations and all fill scripts for customers, administrators, and service providers'

    def handle(self, *args, **options):
        # Run makemigrations and migrate to ensure the database is up to date
        self.stdout.write(self.style.SUCCESS('Running makemigrations...'))
        call_command('makemigrations')
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

        # Call fill_serviceproviders command
        self.stdout.write(self.style.SUCCESS('Starting to fill service providers...'))
        call_command('fill_service_providers')
        self.stdout.write(self.style.SUCCESS('Finished filling service providers.'))
