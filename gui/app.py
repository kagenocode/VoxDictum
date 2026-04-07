"""
app.py — Ana GUI Penceresi
===========================
customtkinter ile modern masaüstü arayüzü.
"""

from __future__ import annotations

import os
import queue

import customtkinter as ctk

from gui.workers import DownloadWorker, SubtitleWorker


class App(ctk.CTk):
    """Video Altyazı Oluşturucu — Masaüstü Uygulaması."""

    MODELS = ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"]
    DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")

    def __init__(self) -> None:
        super().__init__()

        # ── Pencere ayarları ──
        self.title("🎬 Video Altyazı Oluşturucu")
        self.geometry("800x520")
        self.minsize(650, 450)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Durum değişkenleri
        self._video_path: str | None = None
        self._msg_queue: queue.Queue[str] = queue.Queue()
        self._busy = False

        # ── Arayüz ──
        self._build_ui()

        # Kuyruktan gelen mesajları kontrol et
        self._poll_queue()

    # ─────────────────────────── UI ───────────────────────────

    def _build_ui(self) -> None:
        # Ana çerçeve
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        pad = {"padx": 16, "pady": (10, 0)}

        # ── Başlık ──
        title_lbl = ctk.CTkLabel(
            self,
            text="🎬 Video Altyazı Oluşturucu",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title_lbl.grid(row=0, column=0, **pad, sticky="w")

        # ── URL Alanı ──
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=1, column=0, **pad, sticky="ew")
        url_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(url_frame, text="YouTube URL:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=36,
            font=ctk.CTkFont(size=13),
        )
        self.url_entry.grid(row=0, column=1, sticky="ew")

        # ── Ayarlar satırı ──
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.grid(row=2, column=0, **pad, sticky="ew")

        ctk.CTkLabel(settings_frame, text="Model:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(0, 4)
        )
        self.model_menu = ctk.CTkOptionMenu(
            settings_frame, values=self.MODELS, width=160
        )
        self.model_menu.set("large-v3-turbo")
        self.model_menu.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(settings_frame, text="Dil:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(0, 4)
        )
        self.lang_entry = ctk.CTkEntry(settings_frame, width=60, height=32)
        self.lang_entry.insert(0, "tr")
        self.lang_entry.pack(side="left", padx=(0, 16))

        # ── Butonlar ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, **pad, sticky="ew")

        self.download_btn = ctk.CTkButton(
            btn_frame,
            text="⬇️  Videoyu İndir",
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_download,
        )
        self.download_btn.pack(side="left", padx=(0, 12))

        self.subtitle_btn = ctk.CTkButton(
            btn_frame,
            text="📝  Altyazı Oluştur",
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_subtitle,
        )
        self.subtitle_btn.pack(side="left")

        # ── Log / Durum alanı ──
        self.log_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Menlo", size=12),
            state="disabled",
            wrap="word",
        )
        self.log_box.grid(row=4, column=0, padx=16, pady=(10, 16), sticky="nsew")

    # ─────────────────────── Mesaj kuyruğu ───────────────────────

    def _poll_queue(self) -> None:
        """Arka plan thread'lerinden gelen log mesajlarını GUI'ye yazar."""
        while not self._msg_queue.empty():
            msg = self._msg_queue.get_nowait()
            self._append_log(msg)
        self.after(100, self._poll_queue)

    def _log(self, msg: str) -> None:
        """Thread-safe log fonksiyonu."""
        self._msg_queue.put(msg)

    def _append_log(self, msg: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ─────────────────────── Buton eylemleri ───────────────────────

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.download_btn.configure(state=state)
        self.subtitle_btn.configure(state=state)

    def _on_download(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            self._append_log("⚠️  Lütfen bir YouTube URL'si girin.")
            return
        if self._busy:
            return

        self._set_busy(True)
        self._append_log(f"🔗 URL: {url}")

        def done(path: str | None, error: str | None) -> None:
            if path:
                self._video_path = path
            self.after(0, lambda: self._set_busy(False))

        worker = DownloadWorker(
            url=url,
            output_dir=self.DOWNLOADS_DIR,
            log_callback=self._log,
            done_callback=done,
        )
        worker.start()

    def _on_subtitle(self) -> None:
        if not self._video_path:
            self._append_log("⚠️  Önce bir video indirin.")
            return
        if self._busy:
            return

        self._set_busy(True)
        model = self.model_menu.get()
        lang = self.lang_entry.get().strip() or "tr"

        self._append_log(f"📝 Altyazı oluşturuluyor... (model: {model}, dil: {lang})")

        def done(path: str | None, error: str | None) -> None:
            self.after(0, lambda: self._set_busy(False))

        worker = SubtitleWorker(
            video_path=self._video_path,
            model_size=model,
            language=lang,
            log_callback=self._log,
            done_callback=done,
        )
        worker.start()

