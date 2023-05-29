from __future__ import annotations

from dataclasses import dataclass
from dataclasses import KW_ONLY
import functools
import importlib.resources
import logging
from mimetypes import guess_type
import os.path
import re
import shutil
from typing import ClassVar

from termcolor import colored

from ..converter import AbstractJsonlConverter
from ..jsonl.reader import Reader
from ..thumbnail.converter import ThumbnailConverter
from ..vtt.converter import VTTConverter


_logger = logging.getLogger(__name__.replace(".converter", ""))
_inf = functools.partial(_logger.log, logging.INFO)

_clean_title_from_path_re = re.compile(
    r"[^a-zA-Z0-9:_]",
)


def _gen_title_from_filename(filename: str) -> str:
    name = os.path.splitext(os.path.basename(filename))[0]
    return _clean_title_from_path_re.sub(" ", name).title()


@dataclass
class HTMLConverter(AbstractJsonlConverter):
    ext = "html"
    template_name = "write.html.jinja2"
    logger = _inf

    default_resource_name: ClassVar[str] = __name__.replace(".html.converter", "")
    _: KW_ONLY
    html_head_entry: list[str]
    stylesheet: str
    javascript: str

    def get_template_context(self, reader: Reader) -> dict:
        media_filename = reader.media_filename
        base_media_filename = os.path.basename(media_filename)
        mime_type = guess_type(media_filename)[0]
        vtt_filename = VTTConverter.create_output_name(base_media_filename)
        image = ThumbnailConverter.create_output_name(media_filename)
        if os.path.isfile(image):
            image = os.path.basename(image)
        else:
            image = ""

        return {
            "javascript": self._get_and_copy_javascript(),
            "stylesheet": self._get_and_copy_stylesheet(),
            "html_head_entry": self.html_head_entry,
            "image": image,
            "language": reader.language,
            "media_filename": base_media_filename,
            "mime_type": mime_type,
            "title": _gen_title_from_filename(media_filename),
            "vtt_filename": vtt_filename,
            "segments": iter(reader),
        }

    def _get_and_copy_stylesheet(self) -> str:
        if self.stylesheet:
            return self.stylesheet
        return self._get_and_copy_default("css")

    def _get_and_copy_javascript(self) -> str:
        if self.javascript:
            return self.javascript
        return self._get_and_copy_default("js")

    def _get_and_copy_default(self, ext: str) -> str:
        dst_name = f"{self.default_resource_name}{os.path.extsep}{ext}"
        dst_path = os.path.join(os.path.dirname(self.filename), dst_name)
        if os.path.exists(dst_path):
            _inf("Already exists " + colored(dst_path, "cyan"))
            return dst_name
        src = importlib.resources.open_text(__package__, f"default.{ext}")
        with open(dst_path, "x") as dst:
            _inf("Created " + colored(dst_path, "cyan"))
            shutil.copyfileobj(src, dst)
        return dst_name
