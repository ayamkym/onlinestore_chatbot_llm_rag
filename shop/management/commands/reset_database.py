from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Reset the database by deleting all data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Warning: This will delete all data from the database!'))

        # Optionally, prompt for confirmation
        confirm = input("Are you sure you want to proceed? Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Operation cancelled. No data was deleted.'))
            return

        # Flush the database (deletes all data but keeps schema)
        call_command('flush', '--no-input')

        # Alternatively, use the following to reset the database entirely
        # You might need to run migrations again afterward
        # call_command('migrate', 'zero', '--fake')
        # call_command('migrate')

        self.stdout.write(self.style.SUCCESS('Successfully deleted all data from the database.'))
