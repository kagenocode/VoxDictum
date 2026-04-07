"""
app.py — Ana GUI Penceresi (PyQt5)
====================================
PyQt5 ile modern masaüstü arayüzü.
"""


import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit,
)

from gui.workers import DownloadWorker, SubtitleWorker


class App(QMainWindow):
    """VoxDictum — Masaüstü Uygulaması."""

    MODELS = ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"]
    DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")

    def __init__(self) -> None:
        super().__init__()

        self._video_path = None
        self._worker = None  # aktif worker referansı (GC koruması)

        self.setWindowTitle("🏛️ VoxDictum")
        self.setMinimumSize(700, 480)
        self.resize(840, 560)

        self._apply_dark_theme()
        self._build_ui()

    # ─────────────────── Koyu Tema ───────────────────

    def _apply_dark_theme(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 14px;
            }
            QLabel#title {
                color: #89b4fa;
                font-size: 22px;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #89b4fa;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #45475a;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QTextEdit {
                background-color: #181825;
                color: #a6adc8;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 8px;
                font-family: "Menlo", "Courier New", monospace;
                font-size: 12px;
            }
        """)

    # ─────────────────── Arayüz ───────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ── Başlık ──
        title = QLabel("🏛️ VoxDictum")
        title.setObjectName("title")
        layout.addWidget(title)

        # ── URL Satırı ──
        url_row = QHBoxLayout()
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_row.addWidget(url_label)
        url_row.addWidget(self.url_input, stretch=1)
        layout.addLayout(url_row)

        # ── Ayarlar Satırı ──
        settings_row = QHBoxLayout()

        settings_row.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.MODELS)
        self.model_combo.setCurrentText("large-v3-turbo")
        self.model_combo.setFixedWidth(180)
        settings_row.addWidget(self.model_combo)

        settings_row.addSpacing(16)

        settings_row.addWidget(QLabel("Dil:"))
        self.lang_input = QLineEdit("tr")
        self.lang_input.setFixedWidth(60)
        settings_row.addWidget(self.lang_input)

        settings_row.addStretch()
        layout.addLayout(settings_row)

        # ── Butonlar ──
        btn_row = QHBoxLayout()

        self.download_btn = QPushButton("⬇️  Videoyu İndir")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.clicked.connect(self._on_download)
        btn_row.addWidget(self.download_btn)

        self.subtitle_btn = QPushButton("📝  Altyazı Oluştur")
        self.subtitle_btn.setCursor(Qt.PointingHandCursor)
        self.subtitle_btn.clicked.connect(self._on_subtitle)
        btn_row.addWidget(self.subtitle_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ── Log Alanı ──
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, stretch=1)

    # ─────────────────── Log ───────────────────

    def _append_log(self, msg: str) -> None:
        self.log_box.append(msg)

    # ─────────────────── Busy State ───────────────────

    def _set_busy(self, busy: bool) -> None:
        self.download_btn.setDisabled(busy)
        self.subtitle_btn.setDisabled(busy)

    # ─────────────────── Download ───────────────────

    def _on_download(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            self._append_log("⚠️  Lütfen bir YouTube URL'si girin.")
            return

        self._set_busy(True)
        self._append_log(f"🔗 URL: {url}")

        worker = DownloadWorker(url=url, output_dir=self.DOWNLOADS_DIR)
        worker.log.connect(self._append_log)
        worker.finished.connect(self._on_download_done)
        worker.error.connect(self._on_worker_error)
        self._worker = worker
        worker.start()

    def _on_download_done(self, path: str) -> None:
        self._video_path = path
        self._set_busy(False)

    # ─────────────────── Subtitle ───────────────────

    def _on_subtitle(self) -> None:
        if not self._video_path:
            self._append_log("⚠️  Önce bir video indirin.")
            return

        model = self.model_combo.currentText()
        lang = self.lang_input.text().strip() or "tr"

        self._set_busy(True)
        self._append_log(f"📝 Altyazı oluşturuluyor... (model: {model}, dil: {lang})")

        worker = SubtitleWorker(
            video_path=self._video_path,
            model_size=model,
            language=lang,
        )
        worker.log.connect(self._append_log)
        worker.finished.connect(self._on_subtitle_done)
        worker.error.connect(self._on_worker_error)
        self._worker = worker
        worker.start()

    def _on_subtitle_done(self, path: str) -> None:
        self._set_busy(False)

    # ─────────────────── Error ───────────────────

    def _on_worker_error(self, msg: str) -> None:
        self._set_busy(False)


def run() -> None:
    """Uygulamayı başlatır."""
    import sys
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
