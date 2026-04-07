"""
workers.py — Arka Plan İş Parçacıkları
=======================================
YouTube indirme ve altyazı oluşturma işlemlerini
ayrı thread'lerde çalıştırır, böylece GUI donmaz.
"""

from __future__ import annotations

import os
import tempfile
import threading
from pathlib import Path
from typing import Callable

import yt_dlp

from subtitle_generator import extract_audio, transcribe_audio, write_srt


class DownloadWorker(threading.Thread):
    """YouTube videosunu indirir."""

    def __init__(
        self,
        url: str,
        output_dir: str,
        log_callback: Callable[[str], None],
        done_callback: Callable[[str | None, str | None], None],
    ) -> None:
        super().__init__(daemon=True)
        self.url = url
        self.output_dir = output_dir
        self.log = log_callback
        self.done = done_callback

    def run(self) -> None:
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            self.log("⬇️  Video indiriliyor...")
            downloaded_file: str | None = None

            def progress_hook(d: dict) -> None:
                nonlocal downloaded_file
                if d["status"] == "downloading":
                    pct = d.get("_percent_str", "?%").strip()
                    speed = d.get("_speed_str", "").strip()
                    self.log(f"   {pct}  {speed}")
                elif d["status"] == "finished":
                    downloaded_file = d.get("filename")
                    self.log("✅ İndirme tamamlandı, dönüştürülüyor...")

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

            self.log(f"✅ Video kaydedildi: {downloaded_file}")
            self.done(downloaded_file, None)

        except Exception as e:
            self.log(f"❌ İndirme hatası: {e}")
            self.done(None, str(e))


class SubtitleWorker(threading.Thread):
    """Video dosyasından altyazı oluşturur."""

    def __init__(
        self,
        video_path: str,
        model_size: str,
        language: str,
        log_callback: Callable[[str], None],
        done_callback: Callable[[str | None, str | None], None],
    ) -> None:
        super().__init__(daemon=True)
        self.video_path = video_path
        self.model_size = model_size
        self.language = language
        self.log = log_callback
        self.done = done_callback

    def run(self) -> None:
        audio_path: str | None = None
        try:
            # Geçici ses dosyası
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_path = tmp.name

            # 1) Video → Ses
            self.log("🎬 Ses çıkarılıyor...")
            extract_audio(self.video_path, audio_path)
            self.log("✅ Ses çıkarıldı.")

            # 2) Ses → Metin
            self.log(f"🤖 Model yükleniyor: {self.model_size} ...")
            segments = transcribe_audio(
                audio_path,
                model_size=self.model_size,
                device="auto",
                language=self.language,
            )

            # 3) Segment → SRT
            if segments:
                srt_path = str(Path(self.video_path).with_suffix(".srt"))
                write_srt(segments, srt_path)
                self.log(f"💾 Altyazı kaydedildi: {srt_path}")
                self.done(srt_path, None)
            else:
                self.log("⚠️  Hiç konuşma tespit edilemedi!")
                self.done(None, "Konuşma tespit edilemedi.")

        except Exception as e:
            self.log(f"❌ Altyazı hatası: {e}")
            self.done(None, str(e))

        finally:
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)

