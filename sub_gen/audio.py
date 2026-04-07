"""
audio.py — Audio Extraction Module
========================================
Extracts a 16kHz mono WAV audio file from a video using ffmpeg.
This is the input format expected by the Whisper model.
"""

import sys

import ffmpeg


def extract_audio(video_path: str, audio_path: str) -> None:
    """
    Extracts audio from a video file and saves it in WAV format.

    Args:
        video_path: Path to the source video file.
        audio_path: Path to the output audio file (.wav).

    Raises:
        SystemExit: Terminates the program if an ffmpeg error occurs.
    """
    print(f"🎬 Extracting audio: {video_path}")

    try:
        (
            ffmpeg
            .input(video_path)
            .output(
                audio_path,
                ac=1,            # Mono channel
                ar=16000,        # 16kHz sample rate (Whisper standard)
                format="wav",
            )
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error:
        print("❌ ffmpeg error! Possible causes:")
        print("   1. ffmpeg is not installed → brew install ffmpeg")
        print("   2. Video file is corrupted or unsupported")
        print(f"   3. File not found → {video_path}")
        sys.exit(1)

    print(f"✅ Audio extracted: {audio_path}")
