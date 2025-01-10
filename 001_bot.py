import os
import django
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "indomie_bot.settings")
django.setup()

from django.conf import settings
from bot.models import Product


# Initialize the bot with the token
bot = telebot.TeleBot(settings.TOKEN)

# /start command handler
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Welcome, select /list to show what I can do")

# /list command handler
@bot.message_handler(commands=["list"])
def listing(message):
    markup = InlineKeyboardMarkup()

    # Add buttons for products and help
    select_product_btn = InlineKeyboardButton("Products", callback_data="products")
    help_button = InlineKeyboardButton("Help", callback_data="help")

    markup.add(select_product_btn, help_button)

    # Send message with options
    bot.send_message(message.chat.id, "Here are a list of options to choose from:\nChoose an option:", reply_markup=markup)

# /products command handler - List products
@bot.message_handler(commands=["products"])
def products(message):
    markup = InlineKeyboardMarkup()

    # Add buttons for each product from the database
    for product in Product.objects.all():
        markup.add(
            InlineKeyboardButton(f"{product.title}", callback_data=f"product_{product.id}")
        )

    bot.send_message(message.chat.id, "Select a product to see what it's about", reply_markup=markup)


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "This is the help section. You can choose 'Products' to view available products.")










# Function to get product details based on callback data
def get_product(data):
    product_id = data.split("_")[1]
    try:
        product = Product.objects.get(id=product_id)
        msg = f"*{product.title} - {product.price}* \n{product.description}"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Place Order", callback_data=f"order_{product.id}"))

    except Product.DoesNotExist:
        msg = "Sorry, the product does not exist."
        markup = ""
    return msg, markup


# Handle callback queries (button clicks)
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "products":
        # Show the list of products
        products(call.message)
    elif call.data.startswith("product_"):
        # Show details of the selected product
        msg, markup = get_product(call.data)
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)
    elif call.data == "help":
        help(call.message)
    bot.answer_callback_query(call.id)
        

# Start the bot and keep it running
if __name__ == "__main__":
    print("Indomie Bot is running")
    bot.polling(none_stop=True)
