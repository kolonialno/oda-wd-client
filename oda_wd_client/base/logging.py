try:
    from structlog import getLogger

    _structlog = True
except ImportError:
    from logging import getLogger

    _structlog = False


_logger = getLogger()


def log(method: str, *args, **kwargs) -> None:
    """
    Drop kwargs if we don't have structlog

    :param method: Log method, i.e. "error" or "debug"
    :param args: positional args which will be passed on as-is to the logger
    :param kwargs: kwargs will be passed on to structlog and dropped else-wise
    :return: None
    """
    if _structlog:
        getattr(_logger, method)(*args, **kwargs)
    else:
        getattr(_logger, method)(*args)
