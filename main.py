"""
VoxDictum — CLI Entry Point
===============================
Usage:
    python main.py --input video.mp4
    python main.py --input video.mp4 --model large-v3-turbo --language tr
    python main.py --input video.mp4 --model large-v3 --device cpu --output subtitle.srt
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from sub_gen import extract_audio, transcribe_audio, write_srt


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="🏛️ VoxDictum — Automatic subtitles with Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input video.mp4
  python main.py --input video.mp4 --model large-v3 --language en
  python main.py --input video.mp4 --model large-v3-turbo --device cpu
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the video file (mp4, mkv, avi, etc.)",
    )
    parser.add_argument(
        "--model", "-m",
        default="large-v3-turbo",
        choices=["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"],
        help="Whisper model size (default: large-v3-turbo)",
    )
    parser.add_argument(
        "--language", "-l",
        default="tr",
        help="Audio language code, e.g.: tr, en, de (default: tr)",
    )
    parser.add_argument(
        "--device", "-d",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Compute device (default: auto — uses GPU if available)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output SRT file path (default: <video_name>.srt)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Input file check ──
    if not os.path.isfile(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    # ── Determine output file name ──
    output_path = args.output or f"{Path(args.input).stem}.srt"

    # ── Header ──
    print("=" * 50)
    print("🏛️ VoxDictum")
    print("=" * 50)
    print(f"   Video    : {args.input}")
    print(f"   Model    : {args.model}")
    print(f"   Language : {args.language}")
    print(f"   Device   : {args.device}")
    print(f"   Output   : {output_path}")
    print("=" * 50)

    # ── Temporary audio file ──
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name

    try:
        # 1️⃣  Video → Audio
        extract_audio(args.input, audio_path)

        # 2️⃣  Audio → Text (segments)
        segments = transcribe_audio(
            audio_path,
            model_size=args.model,
            device=args.device,
            language=args.language,
        )

        # 3️⃣  Segments → SRT
        if segments:
            write_srt(segments, output_path)
        else:
            print("⚠️  No speech detected!")

    finally:
        # Clean up temporary file
        if os.path.exists(audio_path):
            os.unlink(audio_path)
            print("🧹 Temporary files cleaned up.")

    print("\n🎉 Process complete!")


if __name__ == "__main__":
    main()
