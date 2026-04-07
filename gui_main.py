"""
GUI Giriş Noktası
==================
Masaüstü uygulamasını başlatır.

Kullanım:
    python gui_main.py
"""

from gui.app import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

