"""
srt_writer.py — SRT Dosyası Oluşturma Modülü
=============================================
Transkripsiyon segment'lerini standart SRT altyazı formatına çevirir.

SRT Formatı:
    1
    00:00:01,500 --> 00:00:04,200
    Merhaba dünya.

    2
    00:00:05,000 --> 00:00:08,300
    Bu bir altyazı örneğidir.
"""

from __future__ import annotations


def _format_timestamp(seconds: float) -> str:
    """
    Saniyeyi SRT zaman damgası formatına çevirir.

    Args:
        seconds: Zaman değeri (saniye cinsinden).

    Returns:
        "HH:MM:SS,mmm" formatında string.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: list[dict], output_path: str) -> None:
    """
    Segment listesinden SRT altyazı dosyası oluşturur.

    Args:
        segments:    Her biri {"start", "end", "text"} içeren sözlük listesi.
        output_path: Çıktı .srt dosyasının yolu.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_ts = _format_timestamp(seg["start"])
            end_ts = _format_timestamp(seg["end"])
            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{seg['text']}\n")
            f.write("\n")

    print(f"💾 Altyazı dosyası kaydedildi: {output_path}")

