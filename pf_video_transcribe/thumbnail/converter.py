import functools
import logging

import ffmpeg
from termcolor import colored

from ..converter import AbstractConverter
from ..jsonl.reader import Reader
from ..types import Size

_logger = logging.getLogger(__name__.replace(".work", ""))
_inf = functools.partial(_logger.log, logging.INFO)
_err = functools.partial(_logger.log, logging.ERROR)


def get_media_filename(f: str) -> str:
    if f.endswith(".jsonl"):
        return Reader(f).media_filename

    return f


class ThumbnailConverter(AbstractConverter):
    ext = "jpeg"
    logger = _inf

    size: Size

    def __init__(
        self,
        input_filename: str,
        force: bool,
        size: Size,
    ) -> None:
        self.size = size
        super().__init__(get_media_filename(input_filename), force)

    def generate(self) -> None:
        pipeline = (
            ffmpeg.input(self.input_filename)
            .filter("scale", *self.size)
            .filter("thumbnail", 60)
            .output(self.filename, vframes=1)
            .overwrite_output()
            .global_args("-v", "error")
            .global_args("-pattern_type", "none")
        )
        try:
            pipeline.run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            _err(
                "Could not generate: "
                + colored(self.filename, "red")
                + f" (from: {self.input_filename}): "
                + colored(e.stderr.decode(), "red")
            )
            raise
