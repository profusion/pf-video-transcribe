from __future__ import annotations

import functools
import logging
from typing import Optional
from typing import Sequence

from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment
from faster_whisper.transcribe import TranscriptionInfo
from faster_whisper.transcribe import Word
from termcolor import colored
from tqdm import tqdm

from ..jsonl.writer import Writer
from ..types import HeaderInfoJson
from ..types import SegmentPayloadJson
from ..types import WordJson
from ..utils import format_color_prob
from ..utils import format_timestamp
from ..utils import needs_generate

_logger = logging.getLogger(__name__.replace(".work", ""))
_dbg = functools.partial(_logger.log, logging.DEBUG)
_inf = functools.partial(_logger.log, logging.INFO)


def _word_tojson(word: Word) -> WordJson:
    return {
        "start": word.start,
        "end": word.end,
        "text": word.word,
        "probability": word.probability,
    }


def _segment_tojson(segment: Segment) -> SegmentPayloadJson:
    return {
        "start": segment.start,
        "end": segment.end,
        "text": segment.text,
        "words": [_word_tojson(w) for w in (segment.words or ())],
    }


def _info_tojson(info: TranscriptionInfo) -> HeaderInfoJson:
    return {
        "duration": info.duration,
        "language": info.language,
        "language_probability": info.language_probability,
        "all_language_probs": info.all_language_probs or [],
    }


def _show_info(method: str, info: TranscriptionInfo, outfile: str) -> None:
    _inf(
        f"{method} language: "
        + colored(info.language, "cyan")
        + format_color_prob(info.language_probability)
        + " duration: "
        + colored(format_timestamp(info.duration), "cyan")
        + " writing to file: "
        + colored(outfile, "cyan")
    )
    if info.all_language_probs:
        _dbg("Other language probabilities:")
        for lang, prob in info.all_language_probs:
            if prob > 0.1:
                _dbg("   " + colored(lang, "cyan") + format_color_prob(prob))


def transcribe(
    model: WhisperModel,
    media_filename: str,
    force: bool,
    language: Optional[str],
    merge_threshold: float,
) -> str:
    jsonl_filename = Writer.create_output_name(media_filename)
    if not force and not needs_generate(media_filename, jsonl_filename):
        _inf(
            "Up to date: "
            + colored(jsonl_filename, "green")
            + f" (from: {media_filename})"
        )
        return jsonl_filename

    _inf(
        colored("transcribe: ", "blue")
        + colored(media_filename, "cyan")
        + ", language="
        + colored(language or "auto", "cyan")
        + ", merge_threshold="
        + colored(str(merge_threshold), "cyan")
        + ": "
        + colored("preprocessing... it may take some time!", "yellow")
    )

    segments, info = model.transcribe(
        media_filename,
        language=language,
        beam_size=5,
        vad_filter=True,
        word_timestamps=True,
        initial_prompt="Please, write with punctuation.",
    )

    info_json = _info_tojson(info)
    with Writer(media_filename, info_json, merge_threshold) as writer:
        _show_info("forced" if language else "detected", info, writer.filename)
        with tqdm(segments, total=info.duration, unit="s") as pbar:
            for segment in pbar:
                pbar.update(segment.end)
                _dbg(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                writer.add(_segment_tojson(segment))

            jsonl_filename = writer.filename
            _inf(
                "Saved: "
                + colored(jsonl_filename, "cyan")
                + f" (from: {media_filename})"
            )
            return jsonl_filename


def transcribe_batch(
    files: Sequence[str],
    force: bool,
    language: str,
    merge_threshold: float,
    local: bool,
    acceleration_device: str,
) -> None:
    model_size = "large-v2"

    download_text = "" if local else " and will download the models from the internet,"

    _dbg(
        "loading model "
        + colored(model_size, "cyan")
        + " on device "
        + colored(acceleration_device, "cyan")
        + colored(download_text + " it may take some time!", "yellow")
    )
    model = WhisperModel(
        model_size,
        device=acceleration_device,
        local_files_only=local,
    )

    for filename in files:
        transcribe(model, filename, force, language, merge_threshold)
