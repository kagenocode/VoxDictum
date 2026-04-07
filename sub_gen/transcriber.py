"""
transcriber.py — Whisper Speech Recognition Module
===============================================
Transcribes audio files to text using the faster-whisper library.
Returns start/end timestamps and text for each segment.
"""

from __future__ import annotations

from faster_whisper import WhisperModel
from tqdm import tqdm


def _detect_device() -> str:
    """Detects the best available compute device."""
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def transcribe_audio(
    audio_path: str,
    model_size: str = "large-v3-turbo",
    device: str = "auto",
    language: str = "tr",
) -> list[dict]:
    """
    Transcribes an audio file to text using the Whisper model.

    Args:
        audio_path:  Path to the input audio file (.wav).
        model_size:  Whisper model size
                     (tiny | base | small | medium | large-v3 | large-v3-turbo).
        device:      Compute device (auto | cpu | cuda).
        language:    Audio language code (tr, en, de, …).

    Returns:
        List of dictionaries each containing {"start", "end", "text"} keys.
    """

    # ── Device & compute type ──
    if device == "auto":
        device = _detect_device()

    compute_type = "float16" if device == "cuda" else "int8"

    print(f"🤖 Loading model: {model_size} (device: {device}, compute: {compute_type})")
    print("   On the first run, the model will be downloaded (~3 GB), this may take a while...")

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    # ── Transcription ──
    print(f"🎙️  Starting speech recognition (language: {language})...")

    segments_gen, info = model.transcribe(
        audio_path,
        language=language,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

    print(f"📊 Detected language: {info.language} "
          f"(probability: {info.language_probability:.2%})")
    print(f"⏱️  Total duration: {info.duration:.1f} seconds")

    # ── Collect segments (with progress bar) ──
    segments: list[dict] = []

    with tqdm(
        total=info.duration,
        unit="s",
        desc="📝 Processing",
        bar_format="{l_bar}{bar}| {n:.1f}/{total:.1f}s",
    ) as pbar:
        last_end = 0.0
        for segment in segments_gen:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            })
            pbar.update(segment.end - last_end)
            last_end = segment.end

    print(f"✅ {len(segments)} subtitle segments generated.")
    return segments
