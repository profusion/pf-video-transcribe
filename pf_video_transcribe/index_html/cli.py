from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter

from .. import log
from ..abstract_subtitles import cli as abstract_cli
from ..utils import check_dir_exists

description = """\
Lists all '.html' in a directory and creates an 'index.html'
with link to them all.

This can be used to generate a nice landing page for all generated videos.

If '.jsonl' are found without matching '.html', the html (and vtt) will
be generated automatically.
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .work import index_batch

    index_batch(
        args.directory,
        args.force,
        args.duration_threshold,
    )


def add_arguments(ap: ArgumentParser) -> None:
    abstract_cli.add_arguments(ap, False)
    ap.add_argument(
        "directory",
        nargs="+",
        help="directory to be processed",
        type=check_dir_exists,
    )


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "index_html",
        help="Creates index.html for the directories",
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
