#!/bin/bash
# Start the Django web server with Gunicorn
gunicorn --workers=1 --log-level debug indomie_bot.wsgi:application &

# Start the Telegram bot script
python bot.py &

# Wait for both processes to complete
wait
