from __future__ import annotations

import json
import os
from typing import Any
from typing import cast
from typing import Iterator
from typing import Optional
from typing import Self
from typing import TextIO

from ..types import FinishedPayloadJson
from ..types import HeaderInfoJson
from ..types import HeaderLineJson
from ..types import LineJson
from ..types import SegmentPayloadJson


class Reader:
    ENCODER_VERSION = "1.0"

    filename: str
    _file: TextIO
    info: HeaderInfoJson
    media_filename: str
    finished: Optional[FinishedPayloadJson]

    def __init__(
        self,
        filename: str,
    ) -> None:
        self.filename = filename
        self._file = open(self.filename, "r")
        self.finished = None
        self._read_header()

    def __del__(self) -> None:
        # object may have failed to open
        file = getattr(self, "_file", None)
        if file is not None and not file.closed:
            file.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self._file.close()

    def __iter__(self) -> Iterator[SegmentPayloadJson]:
        return self

    def __next__(self) -> SegmentPayloadJson:
        while True:
            data = self._read_line()
            finished = data.get("finished")
            if finished:
                self.finished = cast(FinishedPayloadJson, finished)
                raise StopIteration
            segment = data.get("segment")
            if segment:
                return cast(SegmentPayloadJson, segment)

    def _read_line(self) -> LineJson:
        line = self._file.readline()
        if not line:
            raise StopIteration
        return json.loads(line)

    def _read_header(self) -> None:
        data = cast(HeaderLineJson, self._read_line())
        try:
            header = data["header"]
            version = header["encoder_version"]
            if version != self.ENCODER_VERSION:
                # TODO: whenever we change, add some migration
                raise ValueError(f"unsupported encoder_version: {version}")
            self.info = header["info"]
            self.media_filename = os.path.join(
                os.path.dirname(self.filename), header["media_filename"]
            )
        except (TypeError, KeyError) as e:
            raise ValueError(f"Invalid header {data!r}: {e}") from e

    @property
    def language(self) -> str:
        return self.info["language"]
