import logging

logger = logging.getLogger("brand_yml")
if len(logger.handlers) == 0:
    logger.addHandler(logging.NullHandler())


def log_add_console_stream_handler():
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s - %(name)s - %(funcName)s - %(message)s"
    )
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def log_set_debug():
    log_add_console_stream_handler()
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled")
