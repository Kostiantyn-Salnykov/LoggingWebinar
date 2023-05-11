"""
CRITICAL = 50  # PANIC  - before Exception
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""
import copy
import datetime
import functools
import logging
import logging.config
import logging.handlers
import os
import ssl
import typing
from logging.handlers import DEFAULT_HTTP_LOGGING_PORT, DEFAULT_TCP_LOGGING_PORT, DEFAULT_UDP_LOGGING_PORT

import click

__all__ = ["setup_logging", "get_logger", "format_time"]


EMAIL, PASSWORD = os.getenv(key="MY_EMAIL", default="kostiantyn.salnykov@gmail.com"), os.getenv("MY_PASSWORD")
HOST = "localhost"

TRACE = 5
SUCCESS = 25
LOG_USE_COLORS: bool = True
LOG_LEVEL: int = TRACE
# LOG_LEVEL: int = logging.WARNING
LOG_FORMAT = "{name} | {filename}:{lineno} | {funcName} | {levelname} | {message} | ({asctime}/{created})"
LOG_DEBUG_FORMAT = "{levelname} {name} | {filename}:{lineno} | {funcName} | {message} | ({asctime}/{created})"
DATE_TIME_FORMAT_ISO_8601 = "%Y-%m-%dT%H:%M:%S.%fZ"  # ISO 8601
DATE_TIME_FORMAT_WITHOUT_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"  # ISO 8601 without microseconds


class NoFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        logging.warning(msg="FILTERED!!!")
        return False  # ALWAYS FILTER
        # return True  # HANDLER.emit()


LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": LOG_FORMAT,
            "style": "{",
            "datefmt": DATE_TIME_FORMAT_WITHOUT_MICROSECONDS,
            "validate": True,  # 🤷
        },
        "colorful_formatter": {
            "()": "loggers.ColorfulFormatter",
            "style": "{",
            "date_time_format": DATE_TIME_FORMAT_WITHOUT_MICROSECONDS,
            "validate": True,
            "link_format": False,
        },
        "debug_link_formatter": {
            "()": "loggers.ColorfulFormatter",
            "style": "{",
            "date_time_format": DATE_TIME_FORMAT_ISO_8601,
            "validate": True,
        },
    },
    "filters": {"disable_filter": {"()": NoFilter}},
    "handlers": {
        "default_handler": {"class": "logging.StreamHandler", "level": LOG_LEVEL, "formatter": "default_formatter"},
        "colorful_handler": {"class": "logging.StreamHandler", "level": LOG_LEVEL, "formatter": "colorful_formatter"},
        "debug_handler": {"class": "logging.StreamHandler", "level": LOG_LEVEL, "formatter": "debug_link_formatter"},
        "json_handler": {
            "class": "log_handlers.json_handler.JSONHandler",
            "level": LOG_LEVEL,
            "formatter": "default_formatter",
            # "filters": ["disable_filter"],
        },
        "slack_handler": {
            "class": "log_handlers.slack_handler.SlackHandler",
            "level": logging.CRITICAL,
            "formatter": "default_formatter",
            "host": "hooks.slack.com",
            "url": "/services/T6A7QCU5U/B0337B2MH8R/kPjIx56Z7N3tg5Qotz5STMlV",
            "method": "POST",
            "secure": True,
            "context": ssl.create_default_context(),
        },
        "google_handler": {
            "class": "log_handlers.google_smtp_handler.TLS_SMTPHandler",
            "level": logging.CRITICAL,
            "mailhost": ("smtp.gmail.com", 587),
            "credentials": (EMAIL, PASSWORD),
            "subject": "SMTP LOGGER",
            "fromaddr": EMAIL,
            "toaddrs": EMAIL,
            "timeout": 5,
        },
        "http_handler": {
            "class": "logging.handlers.HTTPHandler",
            "host": f"localhost:{DEFAULT_HTTP_LOGGING_PORT}",
            "method": "POST",
            "url": "/log/",
            "credentials": (EMAIL, PASSWORD),
        },
        "tcp_handler": {"class": "logging.handlers.SocketHandler", "host": HOST, "port": DEFAULT_TCP_LOGGING_PORT},
        "udp_handler": {"class": "logging.handlers.DatagramHandler", "host": HOST, "port": DEFAULT_UDP_LOGGING_PORT},
        "file_handler": {
            "class": "logging.FileHandler",
            "formatter": "default_formatter",
            "filename": "logs/file_handler.log",
        },
        "rotating_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default_formatter",
            "filename": "logs/rotating_file_handler.log",
            "maxBytes": 256,
            "backupCount": 3,
            "encoding": "utf-8",
        },
        "timed_rotating_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default_formatter",
            "filename": "logs/timed_rotating_file_handler.log",
            # "S" - Seconds, "M" - Minutes, "H" - Hours, "D" - Days, "W0 - W6" - Weekdays (0=Monday), "midnight"
            "when": "S",
            "backupCount": 3,
            "utc": True,
            "encoding": "utf-8",
        },
        "queue_handler": {
            "class": "log_handlers.queue_handler.QueueListenerHandler",
            "formatter": "default_formatter",
            "handlers": ["cfg://handlers.http_handler"],
        },
    },
    "root": {"level": LOG_LEVEL, "handlers": ["default_handler"]},
    "loggers": {
        "gunicorn": {"level": "WARNING", "handlers": ["default_handler"], "propagate": False},
        "uvicorn": {"level": "WARNING", "handlers": ["default_handler"], "propagate": False},
        "color": {"level": TRACE, "handlers": ["colorful_handler"], "propagate": False},
        "local": {"level": TRACE, "handlers": ["debug_handler"], "propagate": False},
        "json": {"level": TRACE, "handlers": ["json_handler"], "propagate": False},
        "slack": {"level": TRACE, "handlers": ["slack_handler"], "propagate": False},
        "google": {"level": TRACE, "handlers": ["google_handler"], "propagate": False},
        "http": {"level": TRACE, "handlers": ["http_handler"], "propagate": False},
        "tcp": {"level": TRACE, "handlers": ["tcp_handler"], "propagate": False},
        "udp": {"level": TRACE, "handlers": ["udp_handler"], "propagate": False},
        "file": {"level": TRACE, "handlers": ["file_handler"], "propagate": False},
        "rotating_file": {"level": TRACE, "handlers": ["rotating_file_handler"], "propagate": False},
        "timed_rotating_file": {"level": TRACE, "handlers": ["timed_rotating_handler"], "propagate": False},
        "queue": {"level": TRACE, "handlers": ["queue_handler"], "propagate": False},
    },
}


class ExtendedLogger(logging.getLoggerClass()):
    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(level=TRACE):
            self._log(level=TRACE, msg=msg, args=args, **kwargs)

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(level=SUCCESS):
            self._log(level=SUCCESS, msg=msg, args=args, **kwargs)


logging.setLoggerClass(klass=ExtendedLogger)  # install custom Logger class


def setup_logging() -> None:
    logging.addLevelName(level=TRACE, levelName="TRACE")
    logging.addLevelName(level=SUCCESS, levelName="SUCCESS")
    logging.config.dictConfig(config=LOGGING_CONFIG)


class _Styler:
    _default_kwargs: list[dict[str, int | str | float | tuple | list | bool]] = [
        {"level": TRACE, "fg": (158, 158, 158)},
        {"level": logging.DEBUG, "fg": (121, 85, 72)},
        {"level": logging.INFO, "fg": "bright_blue"},
        {"level": SUCCESS, "fg": "green"},
        {"level": logging.WARNING, "fg": "bright_yellow"},
        {"level": logging.ERROR, "fg": "bright_red"},
        {"level": logging.CRITICAL, "fg": (126, 87, 194), "bold": True, "underline": True},
    ]

    def __init__(self) -> None:
        self.colors_map: dict[int, functools.partial] = {}

        for kwargs in self.__class__._default_kwargs:
            self.set_style(**kwargs)  # type: ignore

    def get_style(self, level: int) -> functools.partial | typing.Callable:
        return self.colors_map.get(level, lambda text: text)

    def set_style(
        self,
        level: int,
        fg: tuple[int, int, int] | str | None = None,
        bg: tuple[int, int, int] | str | None = None,
        bold: bool | None = None,
        dim: bool | None = None,
        underline: bool | None = None,
        overline: bool | None = None,
        italic: bool | None = None,
        blink: bool | None = None,
        reverse: bool | None = None,
        strikethrough: bool | None = None,
        reset: bool = True,
    ) -> None:
        self.colors_map[level] = functools.partial(
            click.style,
            fg=fg,
            bg=bg,
            bold=bold,
            dim=dim,
            underline=underline,
            overline=overline,
            italic=italic,
            blink=blink,
            reverse=reverse,
            strikethrough=strikethrough,
            reset=reset,
        )


def format_time(record: logging.LogRecord, date_time_format: str = DATE_TIME_FORMAT_ISO_8601) -> str:
    date_time_utc = datetime.datetime.utcfromtimestamp(record.created)
    return datetime.datetime.strftime(date_time_utc, date_time_format)


class ColorfulFormatter(logging.Formatter):
    def __init__(
        self,
        log_format: str = LOG_DEBUG_FORMAT,
        date_time_format: str = DATE_TIME_FORMAT_ISO_8601,
        style: typing.Literal["%", "$", "{"] = "{",
        validate: bool = True,
        # Custom setup
        accent_color: str | tuple[int, int, int] = "bright_cyan",
        styler: _Styler = _Styler(),
        link_format: bool = True,
    ) -> None:
        self.accent_color = accent_color
        self._styler = styler
        if link_format:
            FILE_FORMAT = click.style(text='╰───📑File "', fg="bright_white", bold=True)
            LINE_FORMAT = click.style(text='", line ', fg="bright_white", bold=True)
            log_format += f"\n{FILE_FORMAT}{{pathname}}{LINE_FORMAT}{{lineno}}"
        super().__init__(fmt=log_format, datefmt=date_time_format, style=style, validate=validate)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = DATE_TIME_FORMAT_ISO_8601) -> str:
        """Override default date time format method."""
        return format_time(record=record, date_time_format=datefmt or DATE_TIME_FORMAT_ISO_8601)

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy.copy(record)
        for key in record_copy.__dict__:
            if key == "message":
                record_copy.__dict__["message"] = self._styler.get_style(level=record_copy.levelno)(
                    text=record_copy.message
                )
            elif key == "levelname":
                separator = " " * (8 - len(record_copy.levelname))
                record_copy.__dict__["levelname"] = (
                    self._styler.get_style(level=record_copy.levelno)(text=record_copy.levelname)
                    + click.style(text=":", fg=self.accent_color)
                    + separator
                )
            elif key == "levelno":
                continue  # set it after iterations (because using in other cases)
            else:
                record_copy.__dict__[key] = click.style(text=str(record.__dict__[key]), fg=self.accent_color)

        record_copy.__dict__["levelno"] = click.style(text=str(record.__dict__["levelno"]), fg=self.accent_color)

        return super().formatMessage(record=record_copy)


def get_logger(name: str | None = "local") -> ExtendedLogger:
    """Get logger instance by name.

    Args:
        name(str): Name of logger

    Returns:
        logging.Logger: Instance of logging.Logger

    Examples:
        from loggers import get_logger

        logger = get_logger(name=__name__)
        logger.debug(msg="Debug message")
    """
    logger: ExtendedLogger = logging.getLogger(name=name)  # type: ignore
    return logger
