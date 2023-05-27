from __future__ import annotations

import os.path
from typing import Iterator
from typing import Optional
from typing import Sequence

from termcolor import colored

from .types import SegmentPayloadJson
from .types import Size
from .types import WordJson


def color_prob(prob: float, low: float = 0.7, high: float = 0.8) -> str:
    if prob < low:
        return "red"
    elif prob > high:
        return "green"
    else:
        return "yellow"


def format_color_prob(prob: float, low: float = 0.7, high: float = 0.8) -> str:
    return colored(f" {prob * 100:.0f}%", color_prob(prob, low=low, high=high))


def format_timestamp(
    seconds: float,
    always_include_hours: bool = False,
    decimal_marker: Optional[str] = ".",
) -> str:
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    main_part = f"{hours_marker}{minutes:02d}:{seconds:02d}"
    if not decimal_marker:
        return main_part
    return f"{main_part}{decimal_marker}{milliseconds:03d}"


def check_file_exists(s: str) -> str:
    if not os.path.isfile(s):
        raise ValueError(f"not a file: {s}")
    return s


def check_dir_exists(s: str) -> str:
    if not os.path.isdir(s):
        raise ValueError(f"not a directory: {s}")
    return s


def needs_generate(src: str, dst: str) -> bool:
    try:
        src_stat = os.stat(src)
        dst_stat = os.stat(dst)
        return dst_stat.st_mtime < src_stat.st_mtime
    except OSError:
        return True


def replace_ext(path: str, ext: str) -> str:
    return os.path.splitext(path)[0] + os.path.extsep + ext


def merge_text(text: str, other: str) -> str:
    if not text.endswith(" ") and not other.startswith(" "):
        other = " " + other
    return text + other


def add_word_to_segment(segment: SegmentPayloadJson, word: WordJson) -> None:
    segment["end"] = word["end"]
    segment["text"] = merge_text(segment["text"], word["text"])
    segment["words"].append(word)


def create_single_word_segment(word: WordJson) -> SegmentPayloadJson:
    return {
        "start": word["start"],
        "end": word["end"],
        "text": word["text"],
        "words": [word],
    }


def merge_words(
    words: Sequence[WordJson],
    duration_threshold: float,
) -> Iterator[SegmentPayloadJson]:
    if not words:
        return

    segment = create_single_word_segment(words[0])
    for word in words[1:]:
        if word["end"] - segment["start"] > duration_threshold:
            yield segment
            segment = create_single_word_segment(word)
        else:
            add_word_to_segment(segment, word)


def iter_split_segments(
    iterator: Iterator[SegmentPayloadJson],
    duration_threshold: float,
) -> Iterator[SegmentPayloadJson]:
    """Iterate over segments and split them whenever needed.

    If segments are longer than ``duration_threshold``, then they will be
    split based on words to fit in that duration. No words will be split.
    """
    for segment in iterator:
        if segment["end"] - segment["start"] < duration_threshold:
            yield segment
        else:
            for ms in merge_words(segment["words"], duration_threshold):
                yield ms


def parse_size(s: str) -> Size:
    try:
        width, height = s.split("x", 1)
        return Size(int(width), int(height))
    except (IndexError, TypeError) as e:
        raise ValueError("invalid size") from e
