import os
import django
import re
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ForceReply

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "indomie_bot.settings")
django.setup()

from django.conf import settings
from bot.models import Product, Order, OrderItem

# Initialize the bot with the token
bot = telebot.TeleBot(settings.TOKEN)

# Dictionary to track user orders
user_orders = {}

# /start command handler
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Welcome! Select /list to see what I can do.")

# /list command handler
@bot.message_handler(commands=["list"])
def listing(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Products", callback_data="products"))
    markup.add(InlineKeyboardButton("Help", callback_data="help"))
    bot.send_message(message.chat.id, "Here are a list of options to choose from:", reply_markup=markup)

# /products command handler - List products
@bot.message_handler(commands=["products"])
def products(message):
    markup = InlineKeyboardMarkup()
    for product in Product.objects.all():
        markup.add(InlineKeyboardButton(f"{product.title}", callback_data=f"product_{product.id}"))
    bot.send_message(message.chat.id, "Select a product:", reply_markup=markup)

# /help command handler
@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, "You can choose 'Products' to view available items and place an order.")

# Function to get product details based on callback data
def get_product(data):
    product_id = data.split("_")[1]
    try:
        product = Product.objects.get(id=product_id)
        msg = f"*{product.title} - ₦{product.price}*\n{product.description}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Place Order", callback_data=f"order_{product.id}"))
    except Product.DoesNotExist:
        msg = "Sorry, this product does not exist."
        markup = None
    return msg, markup

# Handle callback queries (button clicks)
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "products":
        products(call.message)
    elif call.data.startswith("product_"):
        msg, markup = get_product(call.data)
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)
    elif call.data.startswith("order_"):
        product_id = int(call.data.split("_")[1])
        user_orders[call.from_user.id] = {"product_id": product_id, "quantity": None, "hall": None, "room_no": None}
        bot.send_message(call.message.chat.id, "Please enter the quantity:")
        bot.register_next_step_handler(call.message, get_quantity)
    bot.answer_callback_query(call.id)

def get_quantity(message):
    try:
        quantity = int(message.text)
        user_id = message.from_user.id
        if user_id in user_orders:
            user_orders[user_id]["quantity"] = quantity
            # Show hall options with buttons
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("Paul Hall", callback_data="hall_Paul"),
                InlineKeyboardButton("Joseph Hall", callback_data="hall_Joseph"),
                InlineKeyboardButton("Mary Hall", callback_data="hall_Mary"),
                InlineKeyboardButton("Others", callback_data="hall_Others"),
            )
            bot.send_message(message.chat.id, "Choose your hall:", reply_markup=markup)
        else:
            bot.reply_to(message, "No active order found.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid number for the quantity.")
        bot.register_next_step_handler(message, get_quantity)  # Retry quantity input

@bot.callback_query_handler(func=lambda call: call.data.startswith("hall_"))
def handle_hall_selection(call):
    user_id = call.from_user.id
    if user_id in user_orders:
        hall = call.data.split("_")[1]  # Extract hall name from callback data
        user_orders[user_id]["hall"] = hall
        bot.send_message(call.message.chat.id, f"You selected: {hall} hall. Now enter your room number:")
        bot.register_next_step_handler(call.message, get_room_no)
    else:
        bot.reply_to(call.message, "No active order found.")
    bot.answer_callback_query(call.id)

def get_room_no(message):
    room_no = message.text
    pattern = "^[A-G][1-4][1-8]{2}$"
    if re.search(room_no, pattern):
        bot.reply_to(message, f"Your room number is {room_no}")
    else:
        bot.reply_to(message, "Please enter a valid Room number.")
        bot.register_next_step_handler(message, get_room_no)
    user_id = message.from_user.id
    if user_id in user_orders:
        user_orders[user_id]["room_no"] = room_no
        order_data = user_orders[user_id]

        # Save the incomplete order to the database
        product = Product.objects.get(id=order_data["product_id"])
        order, created = Order.objects.get_or_create(
            user_id=message.from_user.id,
            username=message.from_user.username or "Anonymous",
            hall=order_data["hall"],
            romm_no=order_data["room_no"],
            completed=False,
        )
        if created:
            OrderItem.objects.create(order=order, product=product, quantity=order_data["quantity"])
        else:
            bot.reply_to(message, "Sorry, something went wrong, Click on Place Order again and restart the process")

        bot.send_message(
            message.chat.id,
            f"Order for {product.title} added to cart. Use /cart to view your cart."
        )
    else:
        bot.reply_to(message, "No active order found.")


# /cart command handler
@bot.message_handler(commands=["cart"])
def view_cart(message):
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, completed=False)
    if orders.exists():
        msg = "Your cart:\n\n"
        for order in orders:
            items = OrderItem.objects.filter(order=order)
            for item in items:
                msg += f"- {item.product.title} x{item.quantity} (₦{item.product.price * item.quantity})\n"
        msg += "\nUse /checkout to complete your order."
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "Your cart is empty.")

# /checkout command handler
@bot.message_handler(commands=["checkout"])
def checkout(message):
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, completed=False)
    if orders.exists():
        # Integrate Paystack checkout here
        bot.send_message(message.chat.id, "Proceeding to payment (Paystack integration required).")
    else:
        bot.send_message(message.chat.id, "Your cart is empty.")

# Start the bot and keep it running
if __name__ == "__main__":
    print("Indomie Bot is running")
    bot.polling(none_stop=True)
