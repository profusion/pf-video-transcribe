from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter
import textwrap

from .. import log
from ..utils import check_file_exists

description = """\
Loads media files and transcribe their audio to JSONL (lines of json).

NOTE: the model loading requires some time. If you plan to convert multiple
files, use a single command with all the file paths at once.
This will load the model only once.

With the resulting ".jsonl" files, you can then convert to SRT, WebVTT, HTML
and so on. See the other commands in this tool set.
"""


def handle_command(args: Namespace) -> None:
    # avoid loading heavy libraries in the command line
    from .work import transcribe_batch

    transcribe_batch(
        args.file,
        args.force,
        args.language,
        args.merge_threshold,
        args.local,
        args.acceleration_device,
    )


def add_arguments(ap: ArgumentParser) -> None:
    ap.add_argument(
        "--acceleration-device",
        default="auto",
        help=textwrap.dedent(
            """\
            The hardware acceleration device to use, ex: cuda,cpu,auto

            Defaults to auto-discovery

            Note that these need specific libraries installed, see:
            https://opennmt.net/CTranslate2/installation.html
        """
        ),
    )
    ap.add_argument(
        "--local",
        default=False,
        help="Do not download any models or resources from the internet.",
        action="store_true",
    )
    ap.add_argument(
        "-l",
        "--language",
        help="Hint language the audio is in",
    )
    ap.add_argument(
        "--merge-threshold",
        type=float,
        default=1.0,
        help=textwrap.dedent(
            """\
        Audio Speech Recognition (ASR) models work on slices of the media,
        producing segments that are smaller than an actual human language
        sentence/phrase.

        The merge threshold, specified in seconds, will merge sibling segments
        if: next_segment.start - last_segment.end <= merge_threshold.

        Default: %(default)s second
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
        help="media file to be processed",
        type=check_file_exists,
    )


def add_sub_parser(sub: _SubParsersAction) -> ArgumentParser:
    ap = sub.add_parser(
        "transcribe",
        help="Transcribe media files to '.jsonl'",
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
