from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter
import os.path

from .. import log

description = """\
Serve HTTP for the given directory (where you place your videos).

It's Python's http.server enabled to serve Range requests, required by
browsers to implement video seek.

NOTE: this server is meant to help during development and not to be used
in production! For production use a proper server such as nginx, apache;
or a CDN.
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .work import serve

    serve(args.port, args.directory)


def check_directory(s: str) -> str:
    s = os.path.abspath(s)
    s = os.path.relpath(s, os.getcwd())
    if not os.path.isdir(s):
        raise ValueError(f"not a directory: {s}")
    return s


def add_arguments(ap: ArgumentParser) -> None:
    ap.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to start the HTTP server. Default: %(default)s",
    )
    ap.add_argument(
        "directory",
        nargs="?",
        default="videos",
        type=check_directory,
        help="Directory/folder to serve. Default: %(default)s",
    )


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "serve",
        help="Serve static files (development helper)",
        description=description,
        formatter_class=RawTextHelpFormatter,
    )
    add_arguments(ap)
    ap.set_defaults(handle=handle_command)
    return ap


def create_argument_parser() -> ArgumentParser:
    ap = ArgumentParser(
        description=description,
        formatter_class=RawTextHelpFormatter,
    )
    log.add_arguments(ap)
    add_arguments(ap)
    return ap


def main() -> None:
    ap = create_argument_parser()
    args = ap.parse_args()
    log.config(args)
    handle_command(args)
