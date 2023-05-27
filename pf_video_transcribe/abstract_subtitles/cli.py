from argparse import ArgumentParser
import textwrap

from ..utils import check_file_exists


def add_arguments(ap: ArgumentParser, add_files: bool) -> None:
    ap.add_argument(
        "-t",
        "--duration-threshold",
        type=float,
        default=10.0,
        help=textwrap.dedent(
            """\
            Duration (in seconds) to split each segment. The split will
            happen at word boundary, no words will be split.

            Default: %(default)s seconds
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
            source (jsonl), then it will be skipped.
        """
        ),
    )

    if add_files:
        ap.add_argument(
            "file",
            nargs="+",
            help="jsonl file to be processed",
            type=check_file_exists,
        )
