from __future__ import annotations

from dataclasses import dataclass
import json
import os.path
from typing import Any
from typing import Optional
from typing import Self
from typing import TextIO

from ..types import HeaderInfoJson
from ..types import LineJson
from ..types import SegmentPayloadJson
from ..types import WordJson
from ..utils import format_timestamp
from ..utils import merge_text
from ..utils import replace_ext


@dataclass(slots=True)
class CoalescedSegment:
    start: float
    end: float
    text: str
    words: list[WordJson]

    def __init__(self, init: SegmentPayloadJson) -> None:
        self.start = init["start"]
        self.end = init["end"]
        self.text = init["text"]
        self.words = list(init["words"])

    def merge(self, other: SegmentPayloadJson) -> None:
        self.end = other["end"]
        self.text = merge_text(self.text, other["text"])
        self.words += other["words"]

    def tojson(self) -> SegmentPayloadJson:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "words": self.words,
        }

    def __repr__(self) -> str:
        start = format_timestamp(self.start)
        end = format_timestamp(self.end)
        return f"<{start}..{end} {self.text!r}>"


class Writer:
    ENCODER_VERSION = "1.0"

    media_filename: str
    filename: str
    _segment: Optional[CoalescedSegment]
    _file: TextIO

    merge_threshold: float  # seconds between segments, if <=, then merge with previous

    def __init__(
        self,
        media_filename: str,
        info: HeaderInfoJson,
        merge_threshold: float,
    ) -> None:
        self.media_filename = os.path.basename(media_filename)
        self.merge_threshold = merge_threshold
        self.filename = self.create_output_name(media_filename)
        self._segment = None
        self._file = open(self.filename, "w")
        self._write_header(info)

    @classmethod
    def create_output_name(self, media_filename: str) -> str:
        return replace_ext(media_filename, "jsonl")

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if not self._file.closed:
            self._finish(None)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self._finish(exc_value)

    def _write_header(self, info: HeaderInfoJson) -> None:
        self._write(
            {
                "header": {
                    "encoder_version": self.ENCODER_VERSION,
                    "info": info,
                    "media_filename": self.media_filename,
                },
            }
        )

    def _finish(self, exc_value: Any) -> None:
        if self._file.closed:
            return

        self._flush_segment()
        if exc_value is None:
            self._write({"finished": {"ok": True}})
        else:
            self._write({"finished": {"ok": False, "exc": str(exc_value)}})
        self._file.close()

    def _write(self, line: LineJson) -> None:
        json.dump(
            line,
            self._file,
            ensure_ascii=False,
            indent=None,
            separators=(",", ":"),
        )
        self._file.write("\n")
        self._file.flush()

    def _flush_segment(self) -> None:
        if self._segment is None:
            return
        self._write({"segment": self._segment.tojson()})
        self._segment = None

    def add(self, segment: SegmentPayloadJson) -> None:
        if not self._segment:
            self._segment = CoalescedSegment(segment)
        else:
            if segment["start"] - self._segment.end <= self.merge_threshold:
                self._segment.merge(segment)
            else:
                self._flush_segment()
                self._segment = CoalescedSegment(segment)
