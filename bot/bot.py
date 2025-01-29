import re
import requests
from urllib.parse import urlencode

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


from django.conf import settings
from django.urls import reverse
from bot.models import Product, Order, OrderItem, Reciept, DeliveryDate


# Initialize the bot with the token
bot = telebot.TeleBot(settings.TOKEN)
website_link = settings.WEBSITE_LINK

# Dictionary to track user orders
user_orders = {}


# ======================= COMMAND HANDLERS =======================

# /start command handler
@bot.message_handler(commands=["start"])
def start(message):
    """
    Handles the /list command. Displays a menu with options for the user.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Products", callback_data="products"))
    markup.add(InlineKeyboardButton("Help", callback_data="help"))
    msg = """
🌟 Hey there! I’m the *CU Indomie Guy!* 🎉
*----------------------------------------------------------------------*

I’m here to make your _Indomie_ cravings super easy to satisfy! 🛒
Whether it’s a carton (or more 👀), I’ll hook you up with premium-quality _Indomie_ straight from our trusted vendor.

🚚 Delivery? No stress! Your order will land at your hall 🏠 within *7 days* max—guaranteed.

👇 Tap one of the options below to see what magic we can cook up together! 🔥"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)


# /products command handler - List products
@bot.message_handler(commands=["products"])
def products(message):
    """
    Lists all available products retrieved from the database.
    """
    markup = InlineKeyboardMarkup()
    for product in Product.objects.all():
        markup.add(InlineKeyboardButton(f"{product.title}", callback_data=f"product_{product.id}"))
    bot.send_message(message.chat.id, "🔥 Time to stock up on Indomie! 🍜 Choose your favorite pack below and let's get cooking! 😋👇", reply_markup=markup)


# /help command handler
@bot.message_handler(commands=["help"])
def help_command(message):
    """
    Provides help information about the bot with a progressive view.
    """
    # Short initial text with a "Continue Reading" button
    msg = (
        "*Help Section*\n"
        "*----------------------------------------------------------------------*\n"
        "👋 Hello, welcome to the help section! I’m here to guide you on how to use this bot to satisfy your Indomie cravings 🍜.\n"
        "Click the button below to learn more about what I can do for you! 👇"
    )
    
    # Create an inline keyboard with a "Continue Reading" button
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📖 Continue Reading", callback_data="help_intro"))

    # Send the short initial text
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=keyboard)



# /cart command handler
@bot.message_handler(commands=["cart"])
def view_cart(message):
    """
    Displays the user's cart with options to checkout, remove orders, or clear the cart.
    """
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, payed=False)

    if orders.exists():
        msg = "*Hi, Here's your Cart items 🛒:*\n..................☆*: .｡. o(≧▽≦)o .｡.:*☆.....................\n\n"
        markup = InlineKeyboardMarkup()

        # List all unpayed orders
        for order in orders:
            items = OrderItem.objects.filter(order=order)
            order_details = ""
            for item in items:
                order_details += f"- {item.product.title} x{item.quantity} (₦{item.product.price * item.quantity})\n"
            msg += f"Order id: #{order.id}:\n{order_details}\n\n"

        # Add buttons for checkout and remove
        checkout_single = InlineKeyboardButton("Checkout an Order", callback_data="checkout_single_order")
        remove_from_cart = InlineKeyboardButton("Remove an Order from Cart", callback_data="remove_order_cart")

        # Add buttons to the markup
        markup.add(checkout_single, remove_from_cart)

        bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Your cart is empty.")


# /payed_orders command handler
@bot.message_handler(commands=["payed"])
def payed_orders(message):
    """
    Displays the users payed orders and their delivery status
    """
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, payed=True)

    if orders.exists():
        msg = "*Your Checked out Orders*\n\n"

        for order in orders:
            items = OrderItem.objects.filter(order=order).select_related("product")
            reciept = Reciept.objects.get(order=order)
            delivery_url = website_link + reverse("paystack_callback") + f"?order_id={reciept.order.id}&trxref={reciept.trxref}&reference={reciept.reference}"
            order_details = ""
            for item in items:
                order_details += f"{item.product.title} x {item.quantity} - (₦{item.product.price * item.quantity}) \n*Delivery date: {order.delivery_date}*\n*Delivered: {order.delivered}*"

            msg += f"*Order id: #{order.id}*: \n[Click here to see receipt]({delivery_url}) \n{order_details}\n\n"
            """"""
        print(msg)
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "You haven't checked out any orders \nUse /cart to view unpayed orders \nUse /checkout to checkout an order \nUse /products to view available products")



# /checkout command handler
@bot.message_handler(commands=["checkout"])
def checkout_single_order_command(message):
    """
    Prompt the user to select a single order to checkout.
    """
    user_id = message.from_user.id
    orders = Order.objects.filter(user_id=user_id, payed=False)

    if orders.exists():
        markup = InlineKeyboardMarkup()
        for order in orders:
            markup.add(InlineKeyboardButton(f"Order id: #{order.id}", callback_data=f"checkout_order_{order.id}"))
        bot.send_message(message.chat.id, "Select an order to checkout:", reply_markup=markup)

    bot.send_message(message.chat.id, "You have no incomplete orders to checkout.")
    

# ======================= CALLBACK HANDLERS =======================

# Handle callback queries (button clicks)
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order_callback(call):
    """
    Handles all callback queries from inline buttons.
    """
    product_id = int(call.data.split("_")[1])
    user_orders[call.from_user.id] = {"product_id": product_id, "quantity": None, "hall": None, "room_no": None}
    bot.send_message(call.message.chat.id, "Please enter the number of cartons you want to order e.g 5:")
    bot.register_next_step_handler(call.message, get_quantity)
    
    bot.answer_callback_query(call.id)



# Callback query handler for progressive reading
@bot.callback_query_handler(func=lambda call: call.data.startswith("help_"))
def help_callback(call):
    """
    Handles progressive text display for the help command.
    """
    if call.data == "help_intro":
        # Detailed introduction text
        intro_msg = (
            "**#Intro**\n\n"
            "So you're wondering what I'm about, right? 🤔\n\n"
            "Simple! I'm a bot for ordering *Indomie* 🍜 from the convenience of your room. 🏠\n\n"
            "All you have to do is place your order, and I'll forward it to my team to deliver straight to your hall within **7 days**. 🚀\n\n"
            "Oh, and my name is **CU Indomie Guy**, just in case you missed it. 😊\n\n"
            "Ready to see the commands? Tap below! 👇"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📜 View Commands", callback_data="help_commands"))
        bot.edit_message_text(
            intro_msg, 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=keyboard
        )
    
    elif call.data == "help_commands":
        # Commands list
        commands_msg = (
            "*#Commands*\n\n"
            "/start - 🍜 Hello! I'm CU Indomie Guy 😎 — Your one-stop shop for tasty Indomie!\n"
            "/help - 🤔 Confused? No worries, click here to find out how I can help you!\n"
            "/products - 🍴 Explore all the delicious Indomie options available.\n"
            "/cart - 🛒 View your cart and ensure you're ready to munch.\n"
            "/checkout - 💳 Settle up and get your orders delivered.\n"
            "/payed - 💰 Check all your paid and confirmed orders.\n"
            "Want to know how to place an order? Tap below! 👇"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📦 How to Place an Order", callback_data="help_how_to_order"))
        bot.edit_message_text(
            commands_msg, 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=keyboard
        )
    
    elif call.data == "help_how_to_order":
        # Step-by-step order instructions
        order_msg = (
            "**#How to Place an Order**\n\n"
            "Here's how you can place an order in **7 easy steps**: 🛒\n\n"
            "1️⃣ Click on /products and select a product.\n"
            "2️⃣ Click on 'Add to Cart'. 🛍️\n"
            "3️⃣ Enter the number of cartons you need (e.g., 1, 5). 🔢\n"
            "4️⃣ Enter your email (e.g., youremail@example.com). 📧\n"
            "5️⃣ Enter the full name of the recipient. 👤\n"
            "6️⃣ Choose the recipient's hall (e.g., Paul Hall). 🏢\n"
            "7️⃣ Enter the room number (e.g., A204). 🚪\n\n"
            "Use `/cart` to view your cart and proceed to checkout. Easy, right? 😉"
        )
        bot.edit_message_text(
            order_msg, 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            parse_mode="Markdown"
        )





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
        msg = bot.send_message(call.message.chat.id, f"So you are located in *{hall} hall* \nNow enter your room number e.g. A204, B108:", parse_mode="Markdown")
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
        markup.add(InlineKeyboardButton("Add to Cart", callback_data=f"order_{product.id}"))
    except Product.DoesNotExist:
        msg = "Sorry, this product does not exist."
        markup = None
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


# Handle "Remove an order from cart" callback
@bot.callback_query_handler(func=lambda call: call.data == "remove_order_cart")
def handle_remove_order_cart(call):
    """
    Handles the removal of an entire order from the cart.
    """
    user_id = call.from_user.id
    orders = Order.objects.filter(user_id=user_id, payed=False)
    
    if orders.exists():
        # Create buttons for each order
        markup = InlineKeyboardMarkup()
        for order in orders:
            total_items = OrderItem.objects.filter(order=order).count()
            callback_data = f"remove_order_{order.id}"  # Use order ID for removal
            markup.add(InlineKeyboardButton(f"Order id: #{order.id} \nCartons: ({total_items})", callback_data=callback_data))
        
        bot.send_message(call.message.chat.id, "Select an order to remove:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Your cart is empty.")
    
    bot.answer_callback_query(call.id)


# Handle specific order removal
@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_order_"))
def handle_remove_order(call):
    """
    Handles the removal of a specific order.
    """
    order_id = int(call.data.split("_")[2])  # Extract order ID from callback data
    
    try:
        # Find and delete the order along with its items
        order = Order.objects.get(id=order_id)
        order.delete()
        
        msg = f"Order *#{order_id}* has been removed from your cart. \nClick /cart and confirm"
        
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    except Order.DoesNotExist:
        bot.send_message(call.message.chat.id, "Order not found. Please try again.")
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "checkout_single_order")
def checkout_single_order(call):
    """
    Prompt the user to select a single order to checkout.
    """
    user_id = call.from_user.id
    orders = Order.objects.filter(user_id=user_id, payed=False)

    if orders.exists():
        markup = InlineKeyboardMarkup()
        for order in orders:
            markup.add(InlineKeyboardButton(f"Order id: #{order.id}", callback_data=f"checkout_order_{order.id}"))
        bot.send_message(call.message.chat.id, "Select an order to checkout:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "You have no incomplete orders to checkout.")
    
    bot.answer_callback_query(call.id)




# Handle the checkout callback for a single order
@bot.callback_query_handler(func=lambda call: call.data.startswith("checkout_order_"))
def process_single_checkout(call):
    """
    Handles the checkout for a specific order and redirects to Paystack for payment.
    """
    order_id = int(call.data.split("_")[2])
    try:
        order = Order.objects.get(id=order_id, payed=False)
        total_amount = 0
        items = OrderItem.objects.filter(order=order)
        item_details = ""

        for item in items:
            total_amount += item.product.price * item.quantity
            item_details += f"- {item.product.title} x{item.quantity} (₦{item.product.price * item.quantity})\n"

        # Create a Paystack transaction request
        payment_url = create_paystack_payment(total_amount, order_id)

        # Send message with payment link
        bot.send_message(
            call.message.chat.id,
            f"You're checking out Order id: #{order_id}:\n{item_details}\nTotal: ₦{total_amount}\n\n"
            "Click the link below to complete your payment:\n" + payment_url
        )
        order.save()
    except Order.DoesNotExist:
        bot.send_message(call.message.chat.id, "Order not found or already checked out.")
    
    bot.answer_callback_query(call.id)



# Handle other callbacks without specific query handlers
@bot.callback_query_handler(func=lambda call: True)
def handle_other_callbacks(call):
    if call.data == "products":
        products(call.message)
    if call.data == "help":
        help_command(call.message)

    bot.answer_callback_query(call.id)
# ======================= HELPER FUNCTIONS =======================



def create_paystack_payment(amount, order_id):
    """
    Creates a Paystack payment link and returns the URL to redirect the user for payment.
    """
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    data = {
        'amount': amount * 100,  # Convert to kobo (Paystack expects the amount in kobo)
        'email': 'user_email@example.com',  # Replace with the user's email
        'order_id': order_id,  # Your custom order ID (you may pass this from your order model)
        'callback_url': f'{website_link}/paystack/callback/?order_id={order_id}',  # Include order_id in callback URL
    }

    response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=data)
    response_data = response.json()

    if response_data['status']:
        payment_url = response_data['data']['authorization_url']
        return payment_url
    else:
        return None




def get_quantity(message):
    """
    Handles the quantity (number of cartons) input from the user.
    """
    try:
        quantity = int(message.text)
        user_id = message.from_user.id
        if user_id in user_orders and quantity:
            user_orders[user_id]["quantity"] = quantity
            msg = bot.send_message(message.chat.id, "What's your email?")
            bot.register_next_step_handler(msg, get_email)
        else:
            bot.reply_to(message, "No active order found.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid number of cartons.")
        bot.register_next_step_handler(message, get_quantity)  # Retry quantity input


def get_email(message):
    email = message.text
    user_id = message.from_user.id

    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        if user_id in user_orders:
            user_orders[user_id]["email"] = email
            msg = bot.send_message(message.chat.id, "What is the *fullname* of person your order is to be delivered to?", parse_mode="Markdown")
            bot.register_next_step_handler(msg, get_fullname)
        else:
            bot.reply_to(message, "No active order found")
    else:
        bot.send_message(message.chat.id, "Please enter a valid email")
        bot.register_next_step_handler(message, get_email)

    



def get_fullname(message):
    fullname = message.text
    user_id = message.from_user.id

    if user_id in user_orders:
        user_orders[user_id]["fullname"] = fullname
        
        # Show hall options with buttons
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Paul Hall", callback_data="hall_Paul"),
            InlineKeyboardButton("Joseph Hall", callback_data="hall_Joseph"),
            InlineKeyboardButton("Peter Hall", callback_data="hall_Mary"),
            InlineKeyboardButton("John Hall", callback_data="hall_John"),
            InlineKeyboardButton("Daniel Hall", callback_data="hall_Daniel"),
            InlineKeyboardButton("Mary Hall", callback_data="hall_Mary"),
            InlineKeyboardButton("Lydia Hall", callback_data="hall_Lydia"),
            InlineKeyboardButton("Deborah Hall", callback_data="hall_Deborah"),
            InlineKeyboardButton("Dorcas Hall", callback_data="hall_Dorcas"),
            InlineKeyboardButton("Esther Hall", callback_data="hall_Esther"),
        )
        bot.send_message(message.chat.id, "Choose your hall:", reply_markup=markup)
    else:
        bot.reply_to(message, "No active order found")





def get_room_no(message):
    """
    Handles room number input and saves the order.
    """
    try:
        room_no = message.text
        pattern = "^[A-H]{1}+[1-4]{1}+[0-8]{2}$"
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
                full_name = order_data["fullname"],
                username=message.from_user.username or "Anonymous",
                hall=order_data["hall"],
                email = order_data["email"],
                room_no=order_data["room_no"],
                payed=False,
                delivery_date = DeliveryDate.objects.order_by("-id").first()
            )
            if created:
                OrderItem.objects.create(order=order, product=product, quantity=order_data["quantity"])
                bot.send_message(
                    message.chat.id,
                    f"Order for {product.title} added to cart. Use /cart to view your cart."
                )
            else:
                raise Exception

        else:
            bot.reply_to(message, "No active order found.")

    except Exception as e:
        bot.reply_to(message, "Sorry, something went wrong \nThis is probably from our end and not yours \nPlease try again later")
        print(e)




# ======================= BOT STARTUP =======================

def start_bot():
    print("Indomie Bot is running")
    bot.polling(none_stop=True)