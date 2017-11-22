import flask
import logging
import sqlite3
import telebot

from config import (
    API_TOKEN, CONTACTS_MAPPING, DB, MAIN_MENU, PRODUCT_MENU,
    WEBHOOK_LISTEN, WEBHOOK_PORT, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV,
    WEBHOOK_URL_BASE, WEBHOOK_URL_PATH
)
from telebot import types
from time import sleep

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'The bot is running!'


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'JSON has been received.'
    else:
        flask.abort(403)


@bot.message_handler(commands=['start'])
def start_handle(message):
    """Make main menu."""
    main_menu = types.ReplyKeyboardMarkup(True, False, row_width=1)
    main_menu.add(*MAIN_MENU)
    bot.send_message(
        message.chat.id,
        text='Добро пожаловать!',
        reply_markup=main_menu
    )


@bot.message_handler(content_types=['text'])
def text_handler(message):
    """Handle user choice."""
    if message.text == 'Наши бренды':
        menu_handler(
            message=message,
            row_width=1,
            letter_id='B',
            sql_request='SELECT * FROM Brands',
            text="Выберите бренд, чтобы получить информацию о нём."
        )
    elif message.text == 'Органическая косметика':
        menu_handler(
            message=message,
            row_width=1,
            letter_id='O',
            sql_request='SELECT * FROM Categories',
            text="Выберите категорию:"
        )
    elif message.text == 'Красота изнутри':
        menu_handler(
            message=message,
            row_width=1,
            letter_id='I',
            sql_request='SELECT * FROM Inner_beauty_categories',
            text="Выберите категорию:"
        )
    elif message.text == 'Контакты':
        contacts_menu = types.InlineKeyboardMarkup(row_width=2)
        contact_list = CONTACTS_MAPPING.keys()
        contacts_menu.add(
            *[types.InlineKeyboardButton(text=contact_type, callback_data=contact_type + 'C')
              for contact_type in contact_list]
        )
        bot.send_message(
            message.chat.id,
            text="Выберите, чтобы получить контактную информацию.",
            reply_markup=contacts_menu
        )


@bot.callback_query_handler(func=lambda c: True)
def inline_button_handler(user_choice):
    """Send information to user depends on what inline button was chosen."""
    chat_id = user_choice.message.chat.id  # chat id to send messages
    user_choice_letter_id = user_choice.data[-1]
    data = user_choice.data[:-1]
    prod_inf = user_choice.data.split(';')
    conn = sqlite3.connect(DB)  # Connect to DB.
    cursor = conn.cursor()  # Make cursor.
    # Handle brands.
    if user_choice_letter_id == 'B':
        cursor.execute('SELECT description, brand_logo FROM Brands WHERE id={}'.format(data))
        description = cursor.fetchall()
        bot.send_photo(chat_id, photo=description[0][1])  # send brand logo
        bot.send_message(chat_id, text=description[0][0])  # send brand description
    # Handle organic cosmetic.
    elif user_choice_letter_id == 'O':
        cursor.execute('SELECT * FROM All_cat WHERE category_id={}'.format(data))
        subcategories = cursor.fetchall()
        # Check subcategory availability.
        if subcategories:
            return_subcategory_menu(
                subcategories=subcategories,
                chat_id=chat_id,
                row_width=2
            )
        else:
            cursor.execute('SELECT * FROM All_regular_products WHERE category_id={}'.format(data))
            products = cursor.fetchall()
            return_products(products, chat_id, 'norm')
    # Handle inner beauty.
    elif user_choice_letter_id == 'I':
        cursor.execute('SELECT * FROM All_inner_beauty_products WHERE category_id={}'.format(data))
        products = cursor.fetchall()
        return_products(products, chat_id, 'inner')
    # Handle contacts.
    elif user_choice_letter_id == 'C':
        if data == 'Адрес':
            bot.send_chat_action(chat_id, 'find_location')
            bot.send_location(chat_id, 56.314162, 43.989215)
        bot.send_message(chat_id, CONTACTS_MAPPING[data])
    # Get product information.
    elif len(prod_inf) > 1:
        prod_inf_type = prod_inf[1]
        prod_type = prod_inf[2]
        # Check product type(inner beauty product or regular product).
        if prod_type == 'inner':
            view = 'All_inner_beauty_products'
        else:
            view = 'All_regular_products'
        cursor.execute('SELECT * FROM {} WHERE id={}'.format(view, prod_inf[0]))
        all_inf = cursor.fetchall()
        # Get product description.
        if prod_inf_type == 'Описание':
            inf = all_inf[0][5]
        # Get product components.
        elif prod_inf_type == 'Состав':
            inf = all_inf[0][4]
        # Get product application method.
        elif prod_inf_type == 'Применение':
            inf = all_inf[0][6]
        # Get product fabricator.
        else:
            inf = all_inf[0][7]
        bot.send_message(chat_id, text=inf)
    cursor.close()  # Close cursor.
    conn.close()  # Close DB connection.


def menu_handler(message, row_width, letter_id, sql_request, text):
    """Return inline menu for first two cases from main menu."""
    conn = sqlite3.connect(DB)  # Connect to DB.
    cursor = conn.cursor()  # Make cursor.
    menu = types.InlineKeyboardMarkup(row_width=row_width)
    cursor.execute(sql_request)
    data = cursor.fetchall()
    menu.add(
        *[types.InlineKeyboardButton(text=item[1], callback_data=str(item[0]) + letter_id)
          for item in data]
    )
    bot.send_message(
        message.chat.id,
        text=text,
        reply_markup=menu
    )
    cursor.close()  # Close cursor.
    conn.close()  # Close DB connection.


def return_subcategory_menu(subcategories, chat_id, row_width):
    """Return inline menu for subcategories."""
    subcategories_menu = types.InlineKeyboardMarkup(row_width=row_width)
    subcategories_menu.add(
        *[types.InlineKeyboardButton(text=subcategory[1], callback_data=str(subcategory[0]) + 'O')
          for subcategory in subcategories]
    )
    category_name = subcategories[0][3]  # Get category name.
    bot.send_message(
        chat_id,
        text="{}:".format(category_name),
        reply_markup=subcategories_menu
    )


def return_products(products, chat_id, product_type):
    """Return products info."""
    product_menu = types.InlineKeyboardMarkup(row_width=2)
    product_menu.add(*[types.InlineKeyboardButton(text=item) for item in PRODUCT_MENU])
    for product in products:
        product_id = product[0]
        product_name = product[1]
        product_capacity = product[2]
        product_price = product[3]
        product_img = product[8]
        for menu_item in product_menu.keyboard:
            for item in menu_item:
                item['callback_data'] = str(product_id) + ';' + item['text'] + ';' + product_type
        bot.send_photo(
            chat_id,
            photo=product_img,
            caption='{}, {}, {} руб.'.format(product_name, product_capacity, product_price),
            reply_markup=product_menu
        )

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

sleep(0.5)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
