web: gunicorn --workers=1 --log-level debug indomie_bot.wsgi:application
worker: python manage.py run_bot
release: python manage.py migrate
