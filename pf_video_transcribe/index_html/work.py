from __future__ import annotations

import functools
import logging
import os
from typing import Iterator
from typing import Sequence

from termcolor import colored

from .html_info import HtmlInfo
from .html_info import parse_html_info
from ..html.converter import HTMLConverter
from ..templates import get_template
from ..vtt.converter import VTTConverter


_logger = logging.getLogger(__name__.replace(".work", ""))
_inf = functools.partial(_logger.log, logging.INFO)


def collect(directory: str) -> dict[str, set[str]]:
    collected: dict[str, set[str]] = {}

    for root, dirs, files in os.walk(directory):
        for dname in tuple(dirs):
            if dname.startswith("."):
                dirs.remove(dname)
        for fname in files:
            if fname.startswith(".") or fname == "index.html":
                continue
            path = os.path.join(root, fname)
            ext = os.path.splitext(path)[1]
            collected.setdefault(ext, set()).add(path)

    return collected


def generate_vtt(
    jsonl_filenames: Sequence[str], force: bool, duration_threshold: float
) -> Iterator[str]:
    for c in VTTConverter.batch(
        jsonl_filenames,
        force,
        duration_threshold=duration_threshold,
    ):
        yield c.filename


def generate_html(jsonl_filenames: Sequence[str], force: bool) -> Iterator[str]:
    for c in HTMLConverter.batch(jsonl_filenames, force):
        yield c.filename


def index(directory: str, force: bool, duration_threshold: float) -> None:
    by_ext = collect(directory)
    jsonl_filenames = tuple(by_ext[".jsonl"])

    for f in generate_vtt(jsonl_filenames, force, duration_threshold):
        by_ext[".vtt"].add(f)

    for f in generate_html(jsonl_filenames, force):
        by_ext[".html"].add(f)

    html_paths = sorted(by_ext[".html"])
    prefix_len = len(directory + os.path.sep)
    groups: dict[str, list[HtmlInfo]] = {}
    recent_mtime = 0.0
    for path in html_paths:
        dname = os.path.dirname(path)
        groups.setdefault(dname, []).append(parse_html_info(prefix_len, path))
        mtime = os.stat(path).st_mtime
        if recent_mtime < mtime:
            recent_mtime = mtime

    filename = os.path.join(directory, "index.html")
    try:
        mtime = os.stat(filename).st_mtime
    except OSError:
        mtime = 0
    if mtime > recent_mtime and not force:
        _inf("Up to date: " + colored(filename, "green"))
        return

    tmpl = get_template("index.html.jinja2")
    with open(filename, "w") as out:
        for chunk in tmpl.generate(groups=sorted(groups.items())):
            out.write(chunk)

    _inf("Saved: " + colored(filename, "cyan"))


def index_batch(
    directories: Sequence[str], force: bool, duration_threshold: float
) -> None:
    for d in directories:
        index(d, force, duration_threshold)
