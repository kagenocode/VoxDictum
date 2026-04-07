"""
sub_gen package
=========================
Automatically generates SRT subtitles from video files.

Modules:
    - audio       : Extract audio from video
    - transcriber : Speech recognition with Whisper
    - srt_writer  : Generate SRT files
"""

from sub_gen.audio import extract_audio
from sub_gen.transcriber import transcribe_audio
from sub_gen.srt_writer import write_srt

__all__ = ["extract_audio", "transcribe_audio", "write_srt"]
