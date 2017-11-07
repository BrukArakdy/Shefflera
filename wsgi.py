from bot import app
from config import WEBHOOK_LISTEN, WEBHOOK_PORT, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV

if __name__ == "__main":
    # Start flask server
    app.run(
        host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True
    )
