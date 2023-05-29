from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter
import textwrap

from .. import log
from ..types import Size
from ..utils import parse_size
from ..vtt import cli as vtt

description = """\
Loads transcribed jsonl (JSON Lines) file and generate HTML.

The generated HTML page will include a video viewer using WebVTT and
the transcriptions.

By default it will use its own CSS and JavaScript, that will keep
the video and transcriptions in sync. These files will be copied to
the same folder as the generated HTML.

However, if custom stylesheet or script are to be used, they can be overridden
with ``stylesheet`` and ``--javascript``. In such case, no files will be
copied.
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .converter import HTMLConverter
    from ..vtt.converter import VTTConverter
    from ..thumbnail.converter import ThumbnailConverter

    VTTConverter.batch(
        args.file,
        args.force,
        duration_threshold=args.duration_threshold,
    )
    ThumbnailConverter.batch(args.file, args.force, size=args.thumb_size)
    HTMLConverter.batch(
        args.file,
        args.force,
        html_head_entry=args.html_head_entry,
        stylesheet=args.stylesheet,
        javascript=args.javascript,
    )


def add_arguments(ap: ArgumentParser, add_files: bool = True) -> None:
    vtt.add_arguments(ap, add_files)
    ap.add_argument(
        "--html-head-entry",
        action="append",
        default=[],
        help=textwrap.dedent(
            """\
            Lines to be added to <head>.

            They will be passed as is and won't be checked/parsed.
            """
        ),
    )
    ap.add_argument(
        "--stylesheet",
        default="",
        help=textwrap.dedent(
            """\
            Use the CSS stylesheet instead of the built-in.

            Note that the stylesheet must provide all the theme, it's
            NOT an override.

            Note it will be passed as is, it can be an URL of a remote file
            or a relative path. The given value will NOT be accessed or
            copied.
            """
        ),
    )
    ap.add_argument(
        "--javascript",
        default="",
        help=textwrap.dedent(
            """\
            Use the JavaScript instead of the built-in.

            Note that the script must implement all the behavior, it's
            NOT an override.

            Note it will be passed as is, it can be an URL of a remote file
            or a relative path. The given value will NOT be accessed or
            copied.
            """
        ),
    )
    ap.add_argument(
        "--thumb-size",
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


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "html",
        help="Convert '.jsonl' into HTML with video and transcriptions",
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
