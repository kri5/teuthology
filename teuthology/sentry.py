import logging
import raven
import raven.handlers.logging
from .config import config

log = logging.getLogger(__name__)

client = None
handler = None


def get_client():
    global client
    if client:
        return client

    dsn = config.sentry_dsn
    if dsn:
        client = raven.Client(dsn=dsn)
        return client


def setup_logging():
    global client
    client = get_client()
    if not client:
        return

    global handler
    handler = raven.handlers.logging.SentryHandler(client)
    handler.setLevel(logging.ERROR)
    raven.conf.setup_logging(handler)
