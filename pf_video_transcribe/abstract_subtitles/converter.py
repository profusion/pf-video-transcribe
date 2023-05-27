from typing import TypedDict

from ..converter import AbstractJsonlConverter
from ..jsonl.reader import Reader
from ..utils import iter_split_segments

KT = TypedDict(
    "KT",
    {
        "duration_threshold": float,
    },
)


class AbstractSubtitlesConverter(AbstractJsonlConverter[KT]):
    def get_template_context(self, reader: Reader) -> dict:
        duration_threshold = self.kwargs["duration_threshold"]
        return {"segments": iter_split_segments(iter(reader), duration_threshold)}
