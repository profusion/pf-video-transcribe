from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter
import textwrap

from .. import log
from ..types import Size
from ..utils import check_file_exists
from ..utils import parse_size

description = """\
Loads media files and generate an image thumbnail (JPEG).

NOTE: this converter relies on ffmpeg being installed.
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .converter import ThumbnailConverter

    ThumbnailConverter.batch(
        args.file,
        args.force,
        size=args.size,
    )


def add_arguments(ap: ArgumentParser, add_files: bool = True) -> None:
    ap.add_argument(
        "--size",
        type=parse_size,
        default=Size(320, -1),
        help=textwrap.dedent(
            """\
            Specify the thumbnail (JPEG) size.

            Use format: WIDTHxHEIGHT.

            If one of WIDTH or HEIGHT are -1, they will be calculated based
            on the other dimension.

            Default: %(default)s
        """
        ),
    )
    ap.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help=textwrap.dedent(
            """\
            Force regeneration of existing files.

            By default, if the generated file timestamp (mtime) is newer than the
            source (media), then it will be skipped.
        """
        ),
    )
    ap.add_argument(
        "file",
        nargs="+",
        help="media or jsonl file to be processed",
        type=check_file_exists,
    )


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "thumbnail",
        help="Create thumbnail (JPEG) of the given media file",
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
