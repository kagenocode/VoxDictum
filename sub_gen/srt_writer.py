"""
srt_writer.py — SRT File Generation Module
=============================================
Converts transcription segments into standard SRT subtitle format.

SRT Format:
    1
    00:00:01,500 --> 00:00:04,200
    Hello world.

    2
    00:00:05,000 --> 00:00:08,300
    This is a subtitle example.
"""

from __future__ import annotations


def _format_timestamp(seconds: float) -> str:
    """
    Converts seconds to SRT timestamp format.

    Args:
        seconds: Time value (in seconds).

    Returns:
        String in "HH:MM:SS,mmm" format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: list[dict], output_path: str) -> None:
    """
    Creates an SRT subtitle file from a segment list.

    Args:
        segments:    List of dictionaries each containing {"start", "end", "text"}.
        output_path: Path to the output .srt file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_ts = _format_timestamp(seg["start"])
            end_ts = _format_timestamp(seg["end"])
            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{seg['text']}\n")
            f.write("\n")

    print(f"💾 Subtitle file saved: {output_path}")
