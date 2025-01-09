# Indomie Telegram Bot

This project is a simple Telegram bot for ordering products with Django as the backend. The bot allows users to select products from a list and view their details. The backend is powered by Django, and the bot is developed using the `pyTelegramBotAPI`.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Setting Up the Backend](#1-setting-up-the-backend)
  - [2. Setting Up the Bot](#2-setting-up-the-bot)
- [Running the Bot and Backend Separately](#running-the-bot-and-backend-separately)
- [Installing Required Packages](#installing-required-packages)
- [Configuration](#configuration)

## Prerequisites

Before running the bot and backend, ensure you have the following installed:
- Python 3.8 or higher
- Django 4.x or higher
- `pyTelegramBotAPI` library
- A Telegram bot token (you can get one by creating a bot through [BotFather](https://core.telegram.org/bots#botfather))

## Setup Instructions

### 1. Setting Up the Backend

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/indomie-bot.git
   cd indomie-bot
   ```

2. **Create a Virtual Environment**:
   It's recommended to create a virtual environment to isolate dependencies.
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   Install required packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Django Settings**:
   - Make sure your Django settings are properly configured. In particular, ensure you set the `DJANGO_SETTINGS_MODULE` environment variable correctly (in the code it's set to `indomie_bot.settings`).
   
   - For development, you can modify `settings.py` to match your project needs, including database settings and any other configurations.

6. **Apply Migrations**:
   Run the Django migrations to set up the database:
   ```bash
   python manage.py migrate
   ```

7. **Run the Django Server (Backend)**:
   You can run the Django server to manage your database and handle backend requests:
   ```bash
   python manage.py runserver
   ```

### 2. Setting Up the Bot

1. **Set Up Your Bot's Token**:
   - Obtain a bot token by creating a bot on Telegram via BotFather.
   - Store the token in a `.env` file in your project root. Example:
     ```
     TOKEN=your-telegram-bot-token-here
     ```

2. **Configure the Bot Code**:
   - In `bot.py`, ensure the `settings.TOKEN` is being fetched from your Django settings file, and the `DJANGO_SETTINGS_MODULE` environment variable is correctly set.

3. **Start the Bot**:
   Run the bot in a separate terminal or process (separate from the Django server):
   ```bash
   python bot.py
   ```

   The bot will now start, and you can interact with it on Telegram.

## Running the Bot and Backend Separately

To run the bot and the Django backend separately, you will need two terminal windows or separate processes:

1. **Run the Django Backend** (from the first terminal):
   ```bash
   python manage.py runserver
   ```

   This will start the Django backend on `localhost:8000` (or whichever host and port you've configured).

2. **Run the Bot** (from the second terminal):
   ```bash
   python bot.py
   ```

   This will start the bot and connect to Telegram, allowing users to interact with the bot.

## Installing Required Packages

Ensure that all the required packages are installed by running:

```bash
pip install -r requirements.txt
```

This will install all the necessary dependencies, including:
- Django
- `pyTelegramBotAPI` (for interacting with Telegram's API)
- Other dependencies for your project (if needed)

If you don't have `requirements.txt` in your project, you can create it with:

```bash
pip freeze > requirements.txt
```

## Configuration

### Setting Up the Token
- Ensure you have added your bot's token to a `.env` file as follows:
  ```bash
  TOKEN=your-telegram-bot-token-here
  ```

### Database Configuration
- If you're using Django's default database (`SQLite`), ensure it's configured correctly in `settings.py`. If you're using another database (e.g., PostgreSQL, MySQL), ensure the settings are properly configured.

- After configuring, run the following to set up your database:
  ```bash
  python manage.py migrate
  ```

### Testing the Bot
Once everything is set up, you should be able to send `/start` to your bot on Telegram, and it should respond with a welcome message. When you send `/list`, you will see the list of options to choose from.

---

## Troubleshooting

If you encounter any issues, try the following:

- **Check if Django is set up properly**: Ensure that `DJANGO_SETTINGS_MODULE` is correctly set and that `django.setup()` is called before any Django models are used in the bot script.
- **Check if your bot token is correct**: Ensure that you’ve set the correct bot token in the `.env` file.
- **Ensure your bot is running in a separate terminal**: The bot needs to run in a separate process from the Django server.

