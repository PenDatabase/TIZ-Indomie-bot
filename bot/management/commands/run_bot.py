from django.core.management.base import BaseCommand
from bot.bot import start_bot

class Command(BaseCommand):
    help = "Run the Telegram bot"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the Telegram bot...")
        start_bot()
