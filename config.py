# Token to connect the bot.
API_TOKEN = "465633546:AAGQNVuoqn5gouyOieqCj1yQbo2riAyebSM"

# Path to bd.
DB = "db_and_certs/Shefflera.db"

CONTACTS_MAPPING = {
    'VK': 'Мы в VK: https://vk.com/shefflera_organic',
    'Instagram': 'Мы в Instagram: https://instagram.com/shefflera_',
    'Телефон': 'Наш телефон: 8 999 120 02 90',
    'Адрес': 'ул. Новая 51, ТЦ «НОВАЯ 51», цокольный этаж'
}

MAIN_MENU = ('Наши бренды', 'Органическая косметика', 'Красота изнутри', 'Контакты')

PRODUCT_MENU = ('Описание', 'Состав', 'Применение', 'Изготовитель')

WEBHOOK_HOST = 'https://104.131.96.14/'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '127.0.0.1'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './db_and_certs/webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './db_and_certs/webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

WEBHOOK_REQ = 'https://api.telegram.org/bot{token}/setWebhook?url={host}:{port}/{token}/&certificate={certificate}'
