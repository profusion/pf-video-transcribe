from __future__ import annotations

import functools
import logging

from ..abstract_subtitles.converter import AbstractSubtitlesConverter


_logger = logging.getLogger(__name__.replace(".converter", ""))
_inf = functools.partial(_logger.log, logging.INFO)


class SRTConverter(AbstractSubtitlesConverter):
    ext = "srt"
    template_name = "write.srt.jinja2"
    logger = _inf
