"""
subtitle_generator paketi
=========================
Video dosyalarından otomatik SRT altyazı oluşturur.

Modüller:
    - audio       : Video'dan ses çıkarma
    - transcriber : Whisper ile konuşma tanıma
    - srt_writer  : SRT dosyası oluşturma
"""

from subtitle_generator.audio import extract_audio
from subtitle_generator.transcriber import transcribe_audio
from subtitle_generator.srt_writer import write_srt

__all__ = ["extract_audio", "transcribe_audio", "write_srt"]

