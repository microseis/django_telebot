import logging

from django.conf import settings

logger = logging.getLogger(__name__)

if settings.DEBUG:

    logger.setLevel(settings.LOG_LEVEL)

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
