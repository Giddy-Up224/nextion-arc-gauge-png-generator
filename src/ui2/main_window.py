from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from time import perf_counter
from typing import Optional

from PIL.ImageQt import ImageQt
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QIcon, QPainter, QPixmap, QTransform
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from arc.arc2 import ArcConfig, ArcGenerator


class PreviewRenderSignals(QObject):
    finished = Signal(int, object, float, object)


class PreviewRenderWorker(QRunnable):
    def __init__(self, request_id: int, cfg: ArcConfig) -> None:
        super().__init__()
        self.request_id = request_id
        self.cfg = cfg
        self.signals = PreviewRenderSignals()

    def run(self) -> None:
        try:
            t0 = perf_counter()
            image = ArcGenerator(self.cfg).generate()
            elapsed_ms = (perf_counter() - t0) * 1000.0
            self.signals.finished.emit(self.request_id, image, elapsed_ms, None)
        except Exception as exc:
            self.signals.finished.emit(self.request_id, None, 0.0, exc)


class SequenceExportSignals(QObject):
    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(str)


class SequenceExportWorker(QRunnable):
    def __init__(
        self,
        base_cfg: ArcConfig,
        out_dir: Path,
        count: int,
        step: float,
        prefix: str,
    ) -> None:
        super().__init__()
        self.base_cfg = base_cfg
        self.out_dir = out_dir
        self.count = count
        self.step = step
        self.prefix = prefix
        self.signals = SequenceExportSignals()

    def run(self) -> None:
        try:
            for idx in range(self.count):
                value = max(0.0, min(1.0, self.base_cfg.gauge_value + (idx * self.step)))
                cfg = replace(self.base_cfg, gauge_value=value)
                filename = f"{self.prefix}_{idx:04d}.png"
                ArcGenerator(cfg).save(str(self.out_dir / filename))
                self.signals.progress.emit(idx + 1, self.count)

            self.signals.finished.emit(
                f"Exported {self.count} images to {self.out_dir} ({self.prefix}_0000.png ... )"
            )
        except Exception as exc:
            self.signals.error.emit(str(exc))


class SaveImageSignals(QObject):
    finished = Signal(str)
    error = Signal(str)


class SaveImageWorker(QRunnable):
    def __init__(self, cfg: ArcConfig, out_path: Path) -> None:
        super().__init__()
        self.cfg = cfg
        self.out_path = out_path
        self.signals = SaveImageSignals()

    def run(self) -> None:
        try:
            ArcGenerator(self.cfg).save(str(self.out_path))
            self.signals.finished.emit(f"Saved {self.out_path}")
        except Exception as exc:
            self.signals.error.emit(str(exc))


class ColorButton(QPushButton):
    def __init__(self, color: tuple[int, int, int, int], title: str) -> None:
        super().__init__(title)
        self._rgba = color
        self.setFixedHeight(28)
        self.clicked.connect(self._open_picker)
        self._refresh_style()

    def value(self) -> tuple[int, int, int, int]:
        return self._rgba

    def set_value(self, color: tuple[int, int, int, int]) -> None:
        self._rgba = color
        self._refresh_style()

    def _refresh_style(self) -> None:
        r, g, b, a = self._rgba
        self.setText(f"RGBA({r}, {g}, {b}, {a})")
        swatch = QPixmap(18, 18)
        swatch.fill(QColor(r, g, b, a))
        self.setIcon(QIcon(swatch))
        self.setIconSize(swatch.size())

    def _open_picker(self) -> None:
        r, g, b, a = self._rgba
        dialog = QColorDialog(QColor(r, g, b, a), self)
        dialog.setWindowTitle("Choose Color")
        dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        if dialog.exec():
            picked = dialog.currentColor()
            if picked.isValid():
                self.set_value((picked.red(), picked.green(), picked.blue(), picked.alpha()))


class ArcPreviewView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item = self._scene.addPixmap(QPixmap())
        self._pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self._zoom = 1.0
        self._fit_mode = True
        self._fit_in_progress = False
        self._canvas_size = (0, 0)

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        checker = QPixmap(32, 32)
        checker.fill(QColor("#2B2D31"))
        painter = QPainter(checker)
        painter.fillRect(0, 0, 16, 16, QColor("#3A3C41"))
        painter.fillRect(16, 16, 16, 16, QColor("#3A3C41"))
        painter.end()
        self._checker_brush = QBrush(checker)

    def drawBackground(self, painter: QPainter, rect) -> None:  # type: ignore[override]
        painter.fillRect(rect, QColor("#202124"))
        if self._canvas_size[0] > 0 and self._canvas_size[1] > 0:
            painter.fillRect(0, 0, self._canvas_size[0], self._canvas_size[1], self._checker_brush)

    def set_pixmap(self, pixmap: QPixmap, canvas_size: tuple[int, int] | None = None) -> None:
        if canvas_size is None:
            canvas_w = pixmap.width()
            canvas_h = pixmap.height()
        else:
            canvas_w = max(1, int(canvas_size[0]))
            canvas_h = max(1, int(canvas_size[1]))

        self._canvas_size = (canvas_w, canvas_h)
        self._pixmap_item.setPixmap(pixmap)

        pix_w = max(1, pixmap.width())
        pix_h = max(1, pixmap.height())
        self._pixmap_item.setPos(0, 0)
        self._pixmap_item.setTransformOriginPoint(0, 0)
        self._pixmap_item.setTransform(
            QTransform.fromScale(canvas_w / pix_w, canvas_h / pix_h)
        )

        self._scene.setSceneRect(0, 0, canvas_w, canvas_h)
        if self._fit_mode:
            self.fit_to_window()
        else:
            self._apply_zoom()

    def fit_to_window(self) -> None:
        if self._fit_in_progress:
            return

        self._fit_mode = True
        self._zoom = 1.0
        if not self._pixmap_item.pixmap().isNull():
            self._fit_in_progress = True
            try:
                self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
            finally:
                self._fit_in_progress = False

    def reset_zoom(self) -> None:
        self._fit_mode = False
        self._zoom = 1.0
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._apply_zoom()

    def zoom_in(self) -> None:
        self._fit_mode = False
        self._zoom = min(32.0, self._zoom * 1.2)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._apply_zoom()

    def zoom_out(self) -> None:
        self._fit_mode = False
        self._zoom = max(0.05, self._zoom / 1.2)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        self.resetTransform()
        self.scale(self._zoom, self._zoom)

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._fit_mode and not self._fit_in_progress:
            self.fit_to_window()


class ArcPreviewWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Arc Gauge Previewer")
        self.setWindowIcon(QIcon("img/R.png"))
        self.resize(1260, 760)

        self._latest_pixmap: Optional[QPixmap] = None
        self._thread_pool = QThreadPool.globalInstance()
        self._render_request_id = 0
        self._render_in_flight = False
        self._pending_render = False
        self._export_in_progress = False
        self._save_in_progress = False
        self._render_meta: dict[int, str] = {}
        self._render_canvas: dict[int, tuple[int, int]] = {}

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(60)
        self._debounce.timeout.connect(self.render_preview)

        self._build_ui()
        self.render_preview()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        controls = self._build_controls_panel()
        controls.setMaximumWidth(420)
        layout.addWidget(controls)

        right = QVBoxLayout()
        right.setSpacing(10)

        toolbar = QHBoxLayout()
        self.fit_btn = QPushButton("Fit")
        self.fit_btn.clicked.connect(self._fit_preview)
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.clicked.connect(self.preview.zoom_in)
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.clicked.connect(self.preview.zoom_out)
        self.zoom_reset_btn = QPushButton("100%")
        self.zoom_reset_btn.clicked.connect(self.preview.reset_zoom)
        toolbar.addWidget(self.fit_btn)
        toolbar.addWidget(self.zoom_in_btn)
        toolbar.addWidget(self.zoom_out_btn)
        toolbar.addWidget(self.zoom_reset_btn)
        toolbar.addStretch(1)

        right.addLayout(toolbar)
        right.addWidget(self.preview, stretch=1)
        right.addWidget(self.status_label)

        right_host = QWidget()
        right_host.setLayout(right)
        layout.addWidget(right_host, stretch=1)

    def _build_controls_panel(self) -> QWidget:
        host = QWidget()
        panel = QVBoxLayout(host)
        panel.setSpacing(10)

        cfg_box = QGroupBox("Arc")
        form = QFormLayout(cfg_box)

        self.canvas_w = QSpinBox()
        self.canvas_w.setRange(16, 4096)
        self.canvas_w.setValue(200)

        self.canvas_h = QSpinBox()
        self.canvas_h.setRange(16, 4096)
        self.canvas_h.setValue(200)

        size_row = QWidget()
        size_layout = QHBoxLayout(size_row)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.addWidget(self.canvas_w)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.canvas_h)

        self.arc_diameter = QSpinBox()
        self.arc_diameter.setRange(1, 4096)
        self.arc_diameter.setValue(180)

        self.arc_thickness = QSpinBox()
        self.arc_thickness.setRange(1, 1024)
        self.arc_thickness.setValue(10)

        self.start_angle = QDoubleSpinBox()
        self.start_angle.setRange(-5000, 5000)
        self.start_angle.setDecimals(2)
        self.start_angle.setSingleStep(1)
        self.start_angle.setValue(235.0)

        self.end_angle = QDoubleSpinBox()
        self.end_angle.setRange(-5000, 5000)
        self.end_angle.setDecimals(2)
        self.end_angle.setSingleStep(1)
        self.end_angle.setValue(125.0)

        self.gauge_value = QDoubleSpinBox()
        self.gauge_value.setRange(0.0, 100.0)
        self.gauge_value.setDecimals(2)
        self.gauge_value.setSingleStep(1.0)
        self.gauge_value.setValue(75.0)

        self.offset_x = QSpinBox()
        self.offset_x.setRange(-2048, 2048)
        self.offset_x.setValue(0)

        self.offset_y = QSpinBox()
        self.offset_y.setRange(-2048, 2048)
        self.offset_y.setValue(0)

        self.supersample = QSpinBox()
        self.supersample.setRange(1, 8)
        self.supersample.setValue(6)

        self.show_endcaps = QCheckBox("Enabled")
        self.show_endcaps.setChecked(True)
        self.match_endcap_color = QCheckBox("Match Gauge Arc")
        self.match_endcap_color.setChecked(False)

        self.arc_color = ColorButton((80, 200, 10, 255), "Arc Color")
        self.track_color = ColorButton((70, 70, 70, 220), "Track Color")
        self.endcap_color = ColorButton((80, 200, 10, 255), "Endcap Color")
        self.background_color = ColorButton((0, 0, 0, 0), "Background")

        form.addRow("Canvas", size_row)
        form.addRow("Diameter", self.arc_diameter)
        form.addRow("Thickness", self.arc_thickness)
        form.addRow("Start Angle", self.start_angle)
        form.addRow("End Angle", self.end_angle)
        form.addRow("Gauge Value %", self.gauge_value)
        form.addRow("Offset X", self.offset_x)
        form.addRow("Offset Y", self.offset_y)
        form.addRow("Supersample", self.supersample)
        form.addRow("Show Endcaps", self.show_endcaps)
        form.addRow("Endcaps Follow Arc", self.match_endcap_color)
        form.addRow("Gauge Arc", self.arc_color)
        form.addRow("Track Arc", self.track_color)
        form.addRow("Endcap Color", self.endcap_color)
        form.addRow("Background", self.background_color)

        self.match_endcap_color.toggled.connect(self._on_match_endcap_toggled)
        self.arc_color.clicked.connect(self._sync_endcap_if_linked)

        out_box = QGroupBox("Output")
        out_grid = QGridLayout(out_box)

        self.output_dir = QLineEdit("out")
        self.browse_dir_btn = QPushButton("Browse")
        self.browse_dir_btn.clicked.connect(self._choose_output_dir)

        self.file_name = QLineEdit("arc_preview.png")
        self.save_btn = QPushButton("Save PNG")
        self.save_btn.clicked.connect(self._save_current_png)

        out_grid.addWidget(QLabel("Folder"), 0, 0)
        out_grid.addWidget(self.output_dir, 0, 1)
        out_grid.addWidget(self.browse_dir_btn, 0, 2)
        out_grid.addWidget(QLabel("File Name"), 1, 0)
        out_grid.addWidget(self.file_name, 1, 1, 1, 2)
        out_grid.addWidget(self.save_btn, 2, 1, 1, 2)

        seq_box = QGroupBox("Sequence")
        seq_grid = QGridLayout(seq_box)

        self.sequence_count = QSpinBox()
        self.sequence_count.setRange(1, 5000)
        self.sequence_count.setValue(10)

        self.sequence_step = QDoubleSpinBox()
        self.sequence_step.setRange(0.01, 100.0)
        self.sequence_step.setDecimals(2)
        self.sequence_step.setValue(1.0)

        self.sequence_prefix = QLineEdit("arc")
        self.export_sequence_btn = QPushButton("Export Gauge Value Sweep")
        self.export_sequence_btn.clicked.connect(self._export_sequence)

        seq_grid.addWidget(QLabel("Count"), 0, 0)
        seq_grid.addWidget(self.sequence_count, 0, 1)
        seq_grid.addWidget(QLabel("Step (% points)"), 1, 0)
        seq_grid.addWidget(self.sequence_step, 1, 1)
        seq_grid.addWidget(QLabel("File Prefix"), 2, 0)
        seq_grid.addWidget(self.sequence_prefix, 2, 1)
        seq_grid.addWidget(self.export_sequence_btn, 3, 0, 1, 2)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #BFC3C9;")

        self.preview = ArcPreviewView()

        panel.addWidget(cfg_box)
        panel.addWidget(out_box)
        panel.addWidget(seq_box)
        panel.addStretch(1)

        widgets = [
            self.canvas_w,
            self.canvas_h,
            self.arc_diameter,
            self.arc_thickness,
            self.start_angle,
            self.end_angle,
            self.gauge_value,
            self.offset_x,
            self.offset_y,
            self.supersample,
            self.show_endcaps,
            self.match_endcap_color,
            self.arc_color,
            self.track_color,
            self.endcap_color,
            self.background_color,
        ]

        for w in widgets:
            if isinstance(w, (QSpinBox, QDoubleSpinBox)):
                w.valueChanged.connect(self._schedule_render)
            elif isinstance(w, QCheckBox):
                w.toggled.connect(self._schedule_render)
            elif isinstance(w, ColorButton):
                w.clicked.connect(self._schedule_render)

        return host

    def _schedule_render(self) -> None:
        if not self._export_in_progress and not self._save_in_progress:
            self._debounce.start()

    def _build_config(self) -> ArcConfig:
        resolved_endcap_color = (
            self.arc_color.value()
            if self.match_endcap_color.isChecked()
            else self.endcap_color.value()
        )

        return ArcConfig(
            canvas_size=(self.canvas_w.value(), self.canvas_h.value()),
            background=self.background_color.value(),
            arc_diameter=self.arc_diameter.value(),
            arc_thickness=self.arc_thickness.value(),
            start_angle=self.start_angle.value(),
            end_angle=self.end_angle.value(),
            gauge_value=self.gauge_value.value() / 100.0,
            arc_color=self.arc_color.value(),
            track_color=self.track_color.value(),
            show_endcaps=self.show_endcaps.isChecked(),
            endcap_color=resolved_endcap_color,
            offset_x=self.offset_x.value(),
            offset_y=self.offset_y.value(),
            supersample=self.supersample.value(),
        )

    def _on_match_endcap_toggled(self, checked: bool) -> None:
        self.endcap_color.setEnabled(not checked)
        self._sync_endcap_if_linked()
        self._schedule_render()

    def _sync_endcap_if_linked(self) -> None:
        if self.match_endcap_color.isChecked():
            self.endcap_color.set_value(self.arc_color.value())

    def _build_preview_config(self, full_cfg: ArcConfig) -> ArcConfig:
        return full_cfg

    def render_preview(self) -> None:
        if self._export_in_progress:
            return

        if self._render_in_flight:
            self._pending_render = True
            return

        try:
            full_cfg = self._build_config()
            preview_cfg = self._build_preview_config(full_cfg)
        except Exception as exc:
            self.status_label.setText(f"Render error: {exc}")
            self.status_label.setStyleSheet("color: #F28B82;")
            return

        self._render_request_id += 1
        worker = PreviewRenderWorker(self._render_request_id, preview_cfg)
        worker.signals.finished.connect(self._on_render_finished)
        self._render_meta[self._render_request_id] = (
            f"Preview {preview_cfg.canvas_size[0]}x{preview_cfg.canvas_size[1]}"
            f" from {full_cfg.canvas_size[0]}x{full_cfg.canvas_size[1]}"
        )
        self._render_canvas[self._render_request_id] = full_cfg.canvas_size
        self._render_in_flight = True
        self.status_label.setText("Rendering preview...")
        self.status_label.setStyleSheet("color: #BFC3C9;")
        self._thread_pool.start(worker)

    def _on_render_finished(
        self,
        request_id: int,
        image,
        elapsed_ms: float,
        error,
    ) -> None:
        self._render_in_flight = False
        meta = self._render_meta.pop(request_id, "Preview")
        canvas_size = self._render_canvas.pop(request_id, (image.width, image.height) if image is not None else (0, 0))

        if request_id != self._render_request_id:
            if self._pending_render:
                self._pending_render = False
                self.render_preview()
            return

        if error is not None:
            self.status_label.setText(f"Render error: {error}")
            self.status_label.setStyleSheet("color: #F28B82;")
        else:
            qimage = ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
            self._latest_pixmap = pixmap
            self.preview.set_pixmap(pixmap, canvas_size)

            self.status_label.setText(f"{meta} | {elapsed_ms:.1f} ms")
            self.status_label.setStyleSheet("color: #BFC3C9;")

        if self._pending_render:
            self._pending_render = False
            self.render_preview()

    def _fit_preview(self) -> None:
        self.preview.fit_to_window()

    def _resolve_output_dir(self) -> Path:
        out = Path(self.output_dir.text().strip() or "out")
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _choose_output_dir(self) -> None:
        initial = str(self._resolve_output_dir())
        selected = QFileDialog.getExistingDirectory(self, "Choose Output Folder", initial)
        if selected:
            self.output_dir.setText(selected)

    def _save_current_png(self) -> None:
        if self._save_in_progress or self._export_in_progress:
            return

        try:
            cfg = self._build_config()
            out_dir = self._resolve_output_dir()
            name = self.file_name.text().strip() or "arc_preview.png"
            if not name.lower().endswith(".png"):
                name += ".png"

            out_path = out_dir / name
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return

        self._save_in_progress = True
        self.save_btn.setEnabled(False)
        self.status_label.setText("Saving PNG...")
        self.status_label.setStyleSheet("color: #BFC3C9;")

        worker = SaveImageWorker(cfg, out_path)
        worker.signals.finished.connect(self._on_save_finished)
        worker.signals.error.connect(self._on_save_error)
        self._thread_pool.start(worker)

    def _export_sequence(self) -> None:
        if self._export_in_progress:
            return

        try:
            base_cfg = self._build_config()
            out_dir = self._resolve_output_dir()
            count = self.sequence_count.value()
            step = self.sequence_step.value() / 100.0
            prefix = self.sequence_prefix.text().strip() or "arc"
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
            return

        self._export_in_progress = True
        self.export_sequence_btn.setEnabled(False)
        self.status_label.setText(f"Exporting 0/{count}...")
        self.status_label.setStyleSheet("color: #BFC3C9;")

        worker = SequenceExportWorker(base_cfg, out_dir, count, step, prefix)
        worker.signals.progress.connect(self._on_export_progress)
        worker.signals.finished.connect(self._on_export_finished)
        worker.signals.error.connect(self._on_export_error)
        self._thread_pool.start(worker)

    def _on_export_progress(self, done: int, total: int) -> None:
        self.status_label.setText(f"Exporting {done}/{total}...")
        self.status_label.setStyleSheet("color: #BFC3C9;")

    def _on_export_finished(self, message: str) -> None:
        self._export_in_progress = False
        self.export_sequence_btn.setEnabled(True)
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #81C995;")
        self._schedule_render()

    def _on_export_error(self, message: str) -> None:
        self._export_in_progress = False
        self.export_sequence_btn.setEnabled(True)
        QMessageBox.critical(self, "Export Failed", message)
        self._schedule_render()

    def _on_save_finished(self, message: str) -> None:
        self._save_in_progress = False
        self.save_btn.setEnabled(True)
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #81C995;")

    def _on_save_error(self, message: str) -> None:
        self._save_in_progress = False
        self.save_btn.setEnabled(True)
        QMessageBox.critical(self, "Save Failed", message)
