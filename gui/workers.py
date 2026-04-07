"""
workers.py — Background Workers (PyQt5)
================================================
Runs YouTube downloading and subtitle generation tasks
with QThread so the GUI doesn't freeze.
"""


import os
import tempfile
from pathlib import Path

import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal

from sub_gen import extract_audio, transcribe_audio, write_srt


class DownloadWorker(QThread):
    """Downloads a YouTube video."""

    log = pyqtSignal(str)
    finished = pyqtSignal(str)       # downloaded file path
    error = pyqtSignal(str)

    def __init__(self, url: str, output_dir: str) -> None:
        super().__init__()
        self.url = url
        self.output_dir = output_dir

    def run(self) -> None:
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            self.log.emit("⬇️  Downloading video...")

            downloaded_file = None

            def progress_hook(d: dict) -> None:
                nonlocal downloaded_file
                if d["status"] == "downloading":
                    pct = d.get("_percent_str", "?%").strip()
                    speed = d.get("_speed_str", "").strip()
                    self.log.emit(f"   {pct}  {speed}")
                elif d["status"] == "finished":
                    downloaded_file = d.get("filename")
                    self.log.emit("✅ Download complete, converting...")

            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                "merge_output_format": "mp4",
                "progress_hooks": [progress_hook],
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                if not downloaded_file:
                    downloaded_file = ydl.prepare_filename(info)

            self.log.emit(f"✅ Video saved: {downloaded_file}")
            self.finished.emit(downloaded_file)

        except Exception as e:
            self.log.emit(f"❌ Download error: {e}")
            self.error.emit(str(e))


class SubtitleWorker(QThread):
    """Generates subtitles from a video file."""

    log = pyqtSignal(str)
    finished = pyqtSignal(str)       # SRT file path
    error = pyqtSignal(str)

    def __init__(self, video_path: str, model_size: str, language: str) -> None:
        super().__init__()
        self.video_path = video_path
        self.model_size = model_size
        self.language = language

    def run(self) -> None:
        audio_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_path = tmp.name

            # 1) Video → Audio
            self.log.emit("🎬 Extracting audio...")
            extract_audio(self.video_path, audio_path)
            self.log.emit("✅ Audio extracted.")

            # 2) Audio → Text
            self.log.emit(f"🤖 Loading model: {self.model_size} ...")
            segments = transcribe_audio(
                audio_path,
                model_size=self.model_size,
                device="auto",
                language=self.language,
            )

            # 3) Segments → SRT
            if segments:
                srt_path = str(Path(self.video_path).with_suffix(".srt"))
                write_srt(segments, srt_path)
                self.log.emit(f"💾 Subtitles saved: {srt_path}")
                self.finished.emit(srt_path)
            else:
                self.log.emit("⚠️  No speech detected!")
                self.error.emit("No speech detected.")

        except Exception as e:
            self.log.emit(f"❌ Subtitle error: {e}")
            self.error.emit(str(e))

        finally:
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)

