"""
transcriber.py — Whisper Konuşma Tanıma Modülü
===============================================
faster-whisper kütüphanesi ile ses dosyasını metne çevirir.
Her segment için başlangıç/bitiş zamanı ve metin döndürür.
"""

from __future__ import annotations

from faster_whisper import WhisperModel
from tqdm import tqdm


def _detect_device() -> str:
    """Kullanılabilir en iyi hesaplama cihazını tespit eder."""
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
    Ses dosyasını Whisper modeli ile metne çevirir.

    Args:
        audio_path:  Giriş ses dosyasının yolu (.wav).
        model_size:  Whisper model boyutu
                     (tiny | base | small | medium | large-v3 | large-v3-turbo).
        device:      Hesaplama cihazı (auto | cpu | cuda).
        language:    Ses dili kodu (tr, en, de, …).

    Returns:
        Her biri {"start", "end", "text"} anahtarlarını içeren sözlük listesi.
    """

    # ── Cihaz & hesaplama tipi ──
    if device == "auto":
        device = _detect_device()

    compute_type = "float16" if device == "cuda" else "int8"

    print(f"🤖 Model yükleniyor: {model_size} (cihaz: {device}, hesaplama: {compute_type})")
    print("   İlk çalıştırmada model indirilir (~3 GB), bu biraz zaman alabilir...")

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    # ── Transkripsiyon ──
    print(f"🎙️  Konuşma tanıma başlıyor (dil: {language})...")

    segments_gen, info = model.transcribe(
        audio_path,
        language=language,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

    print(f"📊 Tespit edilen dil: {info.language} "
          f"(olasılık: {info.language_probability:.2%})")
    print(f"⏱️  Toplam süre: {info.duration:.1f} saniye")

    # ── Segment'leri topla (ilerleme çubuğu ile) ──
    segments: list[dict] = []

    with tqdm(
        total=info.duration,
        unit="s",
        desc="📝 İşleniyor",
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

    print(f"✅ {len(segments)} altyazı segmenti oluşturuldu.")
    return segments

