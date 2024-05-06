import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

class Command(BaseCommand):
    help = 'Clears all migration files, resets the migration history, and deletes the database.'

    def handle(self, *args, **options):
        # Удаление файлов миграций
        for app in settings.INSTALLED_APPS:
            try:
                app_path = os.path.join(settings.BASE_DIR, app.split('.')[-1])
                migrations_path = os.path.join(app_path, 'migrations')
                if os.path.exists(migrations_path):
                    for file in os.listdir(migrations_path):
                        file_path = os.path.join(migrations_path, file)
                        if file != '__init__.py' and file.endswith('.py') and os.path.isfile(file_path):
                            os.remove(file_path)
                            self.stdout.write(self.style.SUCCESS(f'Deleted {file} from {migrations_path}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No migrations directory found at {migrations_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {app}: {str(e)}'))

        # Очистка истории миграций в базе данных
        MigrationRecorder.Migration.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared all migration history from the database.'))

