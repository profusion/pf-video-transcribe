from dataclasses import dataclass
from dataclasses import KW_ONLY

from ..converter import AbstractJsonlConverter
from ..jsonl.reader import Reader
from ..utils import iter_split_segments


@dataclass
class AbstractSubtitlesConverter(AbstractJsonlConverter):
    _: KW_ONLY
    duration_threshold: float

    def get_template_context(self, reader: Reader) -> dict:
        return {"segments": iter_split_segments(iter(reader), self.duration_threshold)}
