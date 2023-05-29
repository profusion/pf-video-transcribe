from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter

from .. import log
from ..abstract_subtitles import cli as abstract_cli

description = """\
Loads transcribed jsonl (JSON Lines) file and generate WebVTT.

WebVTT files can be used with Web Browsers, see
https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .converter import VTTConverter

    VTTConverter.batch(
        args.file,
        args.force,
        duration_threshold=args.duration_threshold,
    )


def add_arguments(ap: ArgumentParser, add_files: bool = True) -> None:
    abstract_cli.add_arguments(ap, add_files)


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "vtt",
        help="Convert '.jsonl' into WebVTT (web browser subtitles)",
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
