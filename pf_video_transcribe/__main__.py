import argparse

from . import log
from .html import cli as html
from .index_html import cli as index_html
from .serve import cli as serve
from .srt import cli as srt
from .thumbnail import cli as thumbnail
from .transcribe import cli as transcribe
from .vtt import cli as vtt


def create_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    log.add_arguments(ap)

    sub = ap.add_subparsers()
    transcribe.add_sub_parser(sub)
    html.add_sub_parser(sub)
    vtt.add_sub_parser(sub)
    srt.add_sub_parser(sub)
    thumbnail.add_sub_parser(sub)
    index_html.add_sub_parser(sub)
    serve.add_sub_parser(sub)

    return ap


def cli() -> None:
    ap = create_arg_parser()
    args = ap.parse_args()
    log.config(args)

    handle = getattr(args, "handle", None)
    if handle is not None:
        handle(args)


if __name__ == "__main__":
    cli()
