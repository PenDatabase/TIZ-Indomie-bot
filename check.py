import os, re, requests, django, telebot

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ForceReply

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "indomie_bot.settings")
django.setup()


from django.utils import timezone

print(timezone.now().date())