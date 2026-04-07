"""
Video Altyazı Oluşturucu — CLI Giriş Noktası
==============================================
Kullanım:
    python main.py --input video.mp4
    python main.py --input video.mp4 --model large-v3-turbo --language tr
    python main.py --input video.mp4 --model large-v3 --device cpu --output altyazi.srt
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from subtitle_generator import extract_audio, transcribe_audio, write_srt


def parse_args() -> argparse.Namespace:
    """Komut satırı argümanlarını ayrıştırır."""
    parser = argparse.ArgumentParser(
        description="🎬 Video Altyazı Oluşturucu — Whisper ile otomatik altyazı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py --input video.mp4
  python main.py --input video.mp4 --model large-v3 --language en
  python main.py --input video.mp4 --model large-v3-turbo --device cpu
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Video dosyasının yolu (mp4, mkv, avi, vb.)",
    )
    parser.add_argument(
        "--model", "-m",
        default="large-v3-turbo",
        choices=["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"],
        help="Whisper model boyutu (varsayılan: large-v3-turbo)",
    )
    parser.add_argument(
        "--language", "-l",
        default="tr",
        help="Ses dili kodu, ör: tr, en, de (varsayılan: tr)",
    )
    parser.add_argument(
        "--device", "-d",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Hesaplama cihazı (varsayılan: auto — GPU varsa kullanır)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Çıktı SRT dosyasının yolu (varsayılan: <video_adı>.srt)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Girdi dosyası kontrolü ──
    if not os.path.isfile(args.input):
        print(f"❌ Dosya bulunamadı: {args.input}")
        sys.exit(1)

    # ── Çıktı dosya adını belirle ──
    output_path = args.output or f"{Path(args.input).stem}.srt"

    # ── Başlık ──
    print("=" * 50)
    print("🎬 Video Altyazı Oluşturucu")
    print("=" * 50)
    print(f"   Video  : {args.input}")
    print(f"   Model  : {args.model}")
    print(f"   Dil    : {args.language}")
    print(f"   Cihaz  : {args.device}")
    print(f"   Çıktı  : {output_path}")
    print("=" * 50)

    # ── Geçici ses dosyası ──
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name

    try:
        # 1️⃣  Video → Ses
        extract_audio(args.input, audio_path)

        # 2️⃣  Ses → Metin (segment'ler)
        segments = transcribe_audio(
            audio_path,
            model_size=args.model,
            device=args.device,
            language=args.language,
        )

        # 3️⃣  Segment'ler → SRT
        if segments:
            write_srt(segments, output_path)
        else:
            print("⚠️  Hiç konuşma tespit edilemedi!")

    finally:
        # Geçici dosyayı temizle
        if os.path.exists(audio_path):
            os.unlink(audio_path)
            print("🧹 Geçici dosyalar temizlendi.")

    print("\n🎉 İşlem tamamlandı!")


if __name__ == "__main__":
    main()
