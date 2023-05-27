from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter

from .. import log
from ..abstract_subtitles import cli as abstract_cli

description = """\
Loads transcribed jsonl (JSON Lines) file and generate SRT.

SRT files can be used with media players such as VLC.
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .converter import SRTConverter

    SRTConverter.batch(
        args.file,
        args.force,
        duration_threshold=args.duration_threshold,
    )


def add_arguments(ap: ArgumentParser) -> None:
    abstract_cli.add_arguments(ap, True)


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "srt",
        help="Convert '.jsonl' into SRT (subtitles)",
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
