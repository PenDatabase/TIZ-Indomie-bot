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

# ======================= COMMAND HANDLERS =======================

# /start command handler
@bot.message_handler(commands=["start"])
def start(message):
    """
    Handles the /start command. Greets the user and suggests available options.
    """
    bot.reply_to(message, "Welcome! Select /list to see what I can do.")


# /list command handler
@bot.message_handler(commands=["list"])
def listing(message):
    """
    Handles the /list command. Displays a menu with options for the user.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Products", callback_data="products"))
    markup.add(InlineKeyboardButton("Help", callback_data="help"))
    bot.send_message(message.chat.id, "Here are a list of options to choose from:", reply_markup=markup)


# /products command handler - List products
@bot.message_handler(commands=["products"])
def products(message):
    """
    Lists all available products retrieved from the database.
    """
    markup = InlineKeyboardMarkup()
    for product in Product.objects.all():
        markup.add(InlineKeyboardButton(f"{product.title}", callback_data=f"product_{product.id}"))
    bot.send_message(message.chat.id, "Select a product:", reply_markup=markup)


# /help command handler
@bot.message_handler(commands=["help"])
def help_command(message):
    """
    Provides help information about the bot.
    """
    bot.send_message(message.chat.id, "You can choose 'Products' to view available items and place an order.")


# /cart command handler
@bot.message_handler(commands=["cart"])
def view_cart(message):
    """
    Displays the user's current cart with all added items.
    """
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, completed=False)
    if orders.exists():
        msg = "Your cart:\n\n"
        for order in orders:
            items = OrderItem.objects.filter(order=order)
            for item in items:
                msg += f"Order id: *{order.id}*\n"
                msg += f"_{item.product.title}_ x{item.quantity} (₦{item.product.price * item.quantity})\n"
                msg += f"To be delivered to: *{order.room_no}*\n\n"
        msg += "\nUse /checkout to complete your order."

        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Your cart is empty.")


# /checkout command handler
@bot.message_handler(commands=["checkout"])
def checkout(message):
    """
    Handles the /checkout command. Proceeds to payment.
    """
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, completed=False)
    if orders.exists():
        # Integrate Paystack checkout here
        bot.send_message(message.chat.id, "Proceeding to payment (Paystack integration required).")
    else:
        bot.send_message(message.chat.id, "Your cart is empty.")

# ======================= CALLBACK HANDLERS =======================

# Handle callback queries (button clicks)
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order_callback(call):
    """
    Handles all callback queries from inline buttons.
    """
    product_id = int(call.data.split("_")[1])
    user_orders[call.from_user.id] = {"product_id": product_id, "quantity": None, "hall": None, "room_no": None}
    bot.send_message(call.message.chat.id, "Please enter the quantity:")
    bot.register_next_step_handler(call.message, get_quantity)
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("hall_"))
def handle_hall_selection(call):
    """
    Handles hall selection callback.
    """
    user_id = call.from_user.id
    if user_id in user_orders:
        hall = call.data.split("_")[1]  # Extract hall name from callback data
        user_orders[user_id]["hall"] = hall
        
        bot.answer_callback_query(call.id)
        
        # Ask for room number
        msg = bot.send_message(call.message.chat.id, f"So you are located in *{hall} hall* \nNow enter your room number:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, get_room_no)
    else:
        # Debug: User order not found
        print(f"User {user_id} has no active order.")
        
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "No active order found. Place order for a new item and try again")


@bot.callback_query_handler(func= lambda call: call.data.startswith("product_"))
def get_product(call):
    """
    Retrieves product details based on the callback data.
    """
    product_id = call.data.split("_")[1]
    try:
        product = Product.objects.get(id=product_id)
        msg = f"*{product.title} - ₦{product.price}*\n{product.description}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Place Order", callback_data=f"order_{product.id}"))
    except Product.DoesNotExist:
        msg = "Sorry, this product does not exist."
        markup = None
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_other_callbacks(call):
    if call.data == "products":
        products(call.message)

    bot.answer_callback_query(call.id)
# ======================= HELPER FUNCTIONS =======================



def get_quantity(message):
    """
    Handles the quantity input from the user.
    """
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


def get_room_no(message):
    """
    Handles room number input and saves the order.
    """
    room_no = message.text
    pattern = "^[A-G]{1}+[1-4]{1}+[0-8]{2}$"
    if re.match(pattern, room_no):
        bot.reply_to(message, f"Your room number is {room_no}")
    else:
        bot.reply_to(message, "Please enter a valid Room number (e.g., A203).")
        bot.register_next_step_handler(message, get_room_no)
        return # Exit function if invalid

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
            room_no=order_data["room_no"],
            completed=False,
        )
        if created:
            OrderItem.objects.create(order=order, product=product, quantity=order_data["quantity"])
        else:
            bot.reply_to(message, "Something went wrong. Please try again.")

        bot.send_message(
            message.chat.id,
            f"Order for {product.title} added to cart. Use /cart to view your cart."
        )
    else:
        bot.reply_to(message, "No active order found.")

# ======================= BOT STARTUP =======================

if __name__ == "__main__":
    print("Indomie Bot is running")
    bot.polling(none_stop=True)
