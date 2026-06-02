from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from ui2.main_window import ArcPreviewWindow
else:
    from .main_window import ArcPreviewWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = ArcPreviewWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
