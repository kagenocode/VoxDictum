"""
sub_gen paketi
=========================
Video dosyalarından otomatik SRT altyazı oluşturur.

Modüller:
    - audio       : Video'dan ses çıkarma
    - transcriber : Whisper ile konuşma tanıma
    - srt_writer  : SRT dosyası oluşturma
"""

from sub_gen.audio import extract_audio
from sub_gen.transcriber import transcribe_audio
from sub_gen.srt_writer import write_srt

__all__ = ["extract_audio", "transcribe_audio", "write_srt"]

