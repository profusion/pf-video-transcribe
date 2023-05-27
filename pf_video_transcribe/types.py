from __future__ import annotations

from typing import Literal
from typing import NamedTuple
from typing import Tuple
from typing import TypedDict
from typing import Union

WordJson = TypedDict(
    "WordJson",
    {
        "start": float,
        "end": float,
        "text": str,
        "probability": float,
    },
)

SegmentPayloadJson = TypedDict(
    "SegmentPayloadJson",
    {
        "start": float,
        "end": float,
        "text": str,
        "words": list[WordJson],
    },
)

SegmentLineJson = TypedDict("SegmentLineJson", {"segment": SegmentPayloadJson})

HeaderInfoJson = TypedDict(
    "HeaderInfoJson",
    {
        "duration": float,
        "language": str,
        "language_probability": float,
        "all_language_probs": list[Tuple[str, float]],
    },
)

HeaderPayloadJson = TypedDict(
    "HeaderPayloadJson",
    {
        "encoder_version": str,
        "media_filename": str,
        "info": HeaderInfoJson,
    },
)

HeaderLineJson = TypedDict("HeaderLineJson", {"header": HeaderPayloadJson})

FinishedOkPayloadJson = TypedDict(
    "FinishedOkPayloadJson",
    {
        "ok": Literal[True],
    },
)

FinishedFailedPayloadJson = TypedDict(
    "FinishedFailedPayloadJson",
    {
        "ok": Literal[False],
        "exc": str,
    },
)

FinishedPayloadJson = Union[FinishedOkPayloadJson, FinishedFailedPayloadJson]

FinishedLineJson = TypedDict("FinishedLineJson", {"finished": FinishedPayloadJson})

LineJson = Union[HeaderLineJson, SegmentLineJson, FinishedLineJson]


class Size(NamedTuple):
    width: int
    height: int

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"
