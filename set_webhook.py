import os
from django.conf import settings
from telebot import TeleBot
import requests
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indomie_bot.settings')

import django
django.setup()



bot_token = settings.TOKEN
webhook_url = settings.WEBSITE_LINK

response = requests.post(
    f"https://api.telegram.org/bot{bot_token}/setWebhook",
    data={"url": webhook_url},
)

print(response.json())  # Check the response
