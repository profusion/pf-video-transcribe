from __future__ import annotations

from jinja2 import Environment
from jinja2 import PackageLoader

from ..utils import format_timestamp

env = Environment(loader=PackageLoader("pf_video_transcribe"))
env.filters["format_timestamp"] = format_timestamp

get_template = env.get_template
