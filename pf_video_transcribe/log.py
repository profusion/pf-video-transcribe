from argparse import ArgumentParser
from argparse import Namespace
import logging
import textwrap

from termcolor import colored


class CustomFormatter(logging.Formatter):
    sub_formatters = {
        k: logging.Formatter(
            colored("%(levelname)3.3s", v) + ":%(name)s: %(message)s",
        )
        for k, v in (
            (logging.DEBUG, "blue"),
            (logging.INFO, "cyan"),
            (logging.WARNING, "yellow"),
            (logging.ERROR, "red"),
            (logging.CRITICAL, "light_red"),
        )
    }

    def format(self, record: logging.LogRecord) -> str:
        formatter = self.sub_formatters.get(
            record.levelno,
            self.sub_formatters[logging.ERROR],
        )
        return formatter.format(record)


def config(args: Namespace) -> None:
    logger_stream_handler = logging.StreamHandler()
    logger_stream_handler.setFormatter(CustomFormatter())
    logger = logging.getLogger()
    logger.addHandler(logger_stream_handler)
    logger.setLevel("INFO")

    for cfg in args.log:
        parts = cfg.split(":", 1)
        if len(parts) == 1:
            logging.getLogger().setLevel(cfg)
        else:
            logging.getLogger(parts[0]).setLevel(parts[1])


def add_arguments(ap: ArgumentParser) -> None:
    ap.add_argument(
        "--log",
        action="append",
        default=[],
        help=textwrap.dedent(
            """\
            Configure the log level. If the string contains ":", then
            it's assumed to be "domain:level"
        """
        ),
    )
