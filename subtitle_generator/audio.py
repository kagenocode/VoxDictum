"""
audio.py — Video'dan Ses Çıkarma Modülü
========================================
ffmpeg kullanarak video dosyasından 16kHz mono WAV ses dosyası çıkarır.
Bu format Whisper modelinin beklediği giriş formatıdır.
"""

import sys

import ffmpeg


def extract_audio(video_path: str, audio_path: str) -> None:
    """
    Video dosyasından ses çıkarır ve WAV formatında kaydeder.

    Args:
        video_path: Kaynak video dosyasının yolu.
        audio_path: Çıktı ses dosyasının yolu (.wav).

    Raises:
        SystemExit: ffmpeg hatası oluşursa program sonlanır.
    """
    print(f"🎬 Ses çıkarılıyor: {video_path}")

    try:
        (
            ffmpeg
            .input(video_path)
            .output(
                audio_path,
                ac=1,            # Mono kanal
                ar=16000,        # 16kHz örnekleme hızı (Whisper standardı)
                format="wav",
            )
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error:
        print("❌ ffmpeg hatası! Olası sebepler:")
        print("   1. ffmpeg kurulu değil → brew install ffmpeg")
        print("   2. Video dosyası bozuk veya desteklenmiyor")
        print(f"   3. Dosya bulunamadı → {video_path}")
        sys.exit(1)

    print(f"✅ Ses çıkarıldı: {audio_path}")

