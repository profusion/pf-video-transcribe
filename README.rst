ProFUSION Video Transcribe
==========================

Install
-------

Install the project using `Poetry <https://python-poetry.org/docs/#installation>`_:

.. code-block:: console

    $ poetry install --with dev
    Installing dependencies from lock file
    ...
    Installing the current project: pf-video-transcribe

This project uses `Faster Whisper <https://pypi.org/project/faster-whisper/>`_,
a faster implementation of `OpenAI's Whisper <https://openai.com/research/whisper>`_,
which in turn is built on top of `CTranslate2 <https://opennmt.net/CTranslate2/index.html>`_
hardware optimizations, that requires installation of **NVidia CUDA libraries**, see
`their installation instructions <https://opennmt.net/CTranslate2/installation.html>`_.

Run
---

Run the command line tool:

.. code-block:: console

    $ pf-video-transcribe --help

All commands take ``--log=LEVEL`` or ``--log=DOMAIN:LEVEL`` to change the
log level of every package, such as ``pf_video_transcribe.transcribe``,
``faster_whisper`` and so on. If no domain is given, then the provided level
applies to all log domains. This is a global option and should be specified
before the subcommand.

Subcommands are explained in the next sections.

Transcription
=============

Given that the transcription is a heavy process and takes a lot to load the model
and then to process each media file, it's implemented as a batch operation that
generates an intermediate in the `JSON Lines <https://jsonlines.org/>`_
(``".jsonl"``) format, with a ``"header"`` line followed by all the ``"segment"``,
ended by a ``"finished"`` line with success or failure indicator. Each ``segment``
carries the useful information extracted by
`OpenAI Whisper <https://github.com/openai/whisper>`_:

.. code-block:: console

    $ pf-video-transcribe transcribe videos/my-video.mp4 videos/other-video.mp4


This will generate ``videos/my-video.jsonl`` and ``videos/other-video.jsonl``.

Note that the first time it will take a lot to download the model from the internet.
In the next iterations, the local model will be used, but first they will be checked
remotely -- which can also take time. Using the ``--local`` flag will skip that check.

The language is auto-detected from the first 30 seconds of actual sound (silent is
ignored), but if you do know the language, use the ``--language=LANG`` flag.

Audio Speech Recognition (ASR) models work on slices of the media, producing segments
that are smaller than an actual human language sentence/phrase.
The ``--merge-threshold=SECONDS`` will merge sibling segments if:
``next_segment.start - last_segment.end <= merge_threshold``. The default is 1 second.

A more complex example:

.. code-block:: console

    $ pf-video-transcribe \
          --log=DEBUG \
          transcribe \
          --local \
          --language=pt \
          --merge-threshold=5 \
          videos/my-video.mp4 videos/other-video.mp4

With the transcribed ``".jsonl"`` one can convert to more usable formats,
see the next sections.


Convert to HTML
===============

This generates the HTML meant to easy viewing of the result, a ``<video>`` linking
to the transcribed media alongside a ``<track kind="subtitles">`` linking to the
subtitles, the thumbnail to be used by `OpenGraph <https://ogp.me/>`_ ``og:image``
and the actual transcription segments.

Note: both ``.vtt`` (subtitles) and ``.jpeg`` (thumbnail) are auto-generated
if they don't exist or if they are older than the actual input ``.jsonl``.


Convert to VTT
==============

Web Video Text Track is a subtitle specified by the
`W3C <https://w3c.github.io/webvtt/>`_ and used by all web browsers whenever
specified inside the ``<video>`` element.

The conversion takes parameter ``--duration-threshold=SECONDS`` to control the maximum
duration of a single subtitle entry.

.. code-block:: console

    $ pf-video-transcribe vtt videos/*.jsonl


Convert to SRT
==============

SRT or SubRip is a defacto standard subtitle format that most media players will take.
The conversion takes parameter ``--duration-threshold=SECONDS`` to control the maximum
duration of a single subtitle entry.

.. code-block:: console

    $ pf-video-transcribe srt videos/*.jsonl


Create Thumbnail
================

Uses `FFmpeg <https://ffmpeg.org/>`_ to generate a thumbnail from the video or
its transcription. The ``--size=WIDTHxHEIGHT`` allows to override the default
``320x-1`` (-1 is used to calculate that dimension from the other, keeping the
aspect ratio).

.. code-block:: console

    $ pf-video-transcribe thumbnail videos/*.jsonl


Creating Index HTML
===================

Recursively scans the given directories looking for ``.html`` files, which
can be produced by this tool or not. The generated index will take the ``<title>``
and ``<meta property="og:image">`` to gather the actual title or preview.

It's a very simple way to generate a landing page.

.. code-block:: console

    $ pf-video-transcribe index_html videos/


Serving (Development)
=====================

While developing this tool or playing with parameters it's useful to serve
the files from ``http://`` as the ``file://`` will have some issues with
video files (security limitations). By default serves at ``--port=8000``.

.. code-block:: console

    $ pf-video-transcribe serve videos/


Development
-----------

Install the project with development dependencies:

.. code-block:: console

    $ poetry install --with dev
    Installing dependencies from lock file
    ...
    Installing the current project: pf-video-transcribe


Install `pre-commit <https://pre-commit.com/>`_ in your machine, then install the GIT Hooks:

.. code-block:: console

    $ pre-commit install
    pre-commit installed at .git/hooks/pre-commit
    pre-commit installed at .git/hooks/pre-push
    pre-commit installed at .git/hooks/pre-merge-commit


Used tools:

* Code Formatter: `Black <https://black.readthedocs.io/>`_
* Static Type Checker: `MyPy <https://mypy.readthedocs.io/>`_
* Style Enforcement/Linter: `Flake8 <https://flake8.pycqa.org/>`_
