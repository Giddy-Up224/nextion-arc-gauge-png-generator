from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import math
from PIL import Image, ImageDraw


Color = Tuple[int, int, int, int]

try:
    RESAMPLING_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLING_LANCZOS = Image.LANCZOS  # type: ignore[attr-defined]


# -----------------------------
# Configuration
# -----------------------------

@dataclass(frozen=True)
class ArcConfig:
    canvas_size: Tuple[int, int] = (200, 200)
    background: Color = (0, 0, 0, 0)

    arc_diameter: int = 180
    arc_thickness: int = 10

    start_angle: float = 235
    end_angle: float = 125

    gauge_value: float = 1.0  # 0.0 to 1.0

    arc_color: Color = (50, 50, 50, 255)
    track_color: Color = (35, 35, 35, 200)

    show_endcaps: bool = True
    endcap_color: Color = (50, 50, 50, 255)

    offset_x: int = 0
    offset_y: int = 0

    supersample: int = 6  # replaces "smoothing_factor"

    def __post_init__(self) -> None:
        width, height = self.canvas_size
        if width <= 0 or height <= 0:
            raise ValueError("canvas_size values must be > 0")
        if self.arc_diameter <= 0:
            raise ValueError("arc_diameter must be > 0")
        if self.arc_thickness <= 0:
            raise ValueError("arc_thickness must be > 0")
        if self.arc_thickness > self.arc_diameter:
            raise ValueError("arc_thickness must be <= arc_diameter")
        if self.supersample < 1:
            raise ValueError("supersample must be >= 1")
        if not 0.0 <= self.gauge_value <= 1.0:
            raise ValueError("gauge_value must be between 0.0 and 1.0")

        self._validate_color("background", self.background)
        self._validate_color("arc_color", self.arc_color)
        self._validate_color("track_color", self.track_color)
        self._validate_color("endcap_color", self.endcap_color)

    @staticmethod
    def _validate_color(name: str, color: Color) -> None:
        if len(color) != 4:
            raise ValueError(f"{name} must be an RGBA tuple of 4 integers")
        if not all(0 <= channel <= 255 for channel in color):
            raise ValueError(f"{name} color channels must be between 0 and 255")


# -----------------------------
# Geometry
# -----------------------------

@dataclass
class ArcGeometry:
    bbox: Tuple[float, float, float, float]
    center: Tuple[float, float]
    radius: float


class ArcGeometryBuilder:
    @staticmethod
    def build(cfg: ArcConfig, scale: int) -> ArcGeometry:
        w, h = cfg.canvas_size
        w *= scale
        h *= scale

        diameter = cfg.arc_diameter * scale
        thickness = cfg.arc_thickness * scale

        radius = (diameter / 2) - (thickness / 2)

        # Match legacy behavior: center snaps to integer pixel coordinates.
        cx = (w // 2) + cfg.offset_x * scale
        cy = (h // 2) + cfg.offset_y * scale

        bbox = (
            int(round(cx - diameter / 2)),
            int(round(cy - diameter / 2)),
            int(round(cx + diameter / 2)),
            int(round(cy + diameter / 2)),
        )

        return ArcGeometry(bbox=bbox, center=(cx, cy), radius=radius)


# -----------------------------
# Renderer
# -----------------------------

class ArcRenderer:
    @staticmethod
    def to_pil_angle(clock_angle: float) -> float:
        # convert "clock style" to PIL arc system
        return (clock_angle - 90) % 360

    @staticmethod
    def polar_point(
        center: Tuple[float, float], radius: float, angle_deg: float
    ) -> Tuple[float, float]:
        angle_rad = math.radians(ArcRenderer.to_pil_angle(angle_deg))
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        return x, y

    @staticmethod
    def from_pil_angle(pil_angle: float) -> float:
        return (pil_angle + 90) % 360

    @staticmethod
    def draw_round_cap(
        draw: ImageDraw.ImageDraw,
        center: Tuple[float, float],
        thickness: float,
        color: Color,
        scale: int,
    ) -> None:
        # Strict legacy cap math from arc.py:
        # upscale(xy +/- thickness/2) with unscaled center coordinates.
        r = thickness / 2.0
        x, y = center
        draw.ellipse(
            [
                scale * (x - r),
                scale * (y - r),
                scale * (x + r),
                scale * (y + r),
            ],
            fill=color,
        )

    @staticmethod
    def legacy_arc_coords(cfg: ArcConfig, scale: int) -> Tuple[float, float, float, float]:
        canvas_w = cfg.canvas_size[0]
        canvas_h = cfg.canvas_size[1]
        diameter = cfg.arc_diameter

        width = ((canvas_w * scale) - (diameter * scale)) / 2
        height = ((canvas_h * scale) - (diameter * scale)) / 2

        left = width + (cfg.offset_x * scale)
        top = height + (cfg.offset_y * scale)
        right = ((canvas_w * scale) - width) + (cfg.offset_x * scale)
        bottom = ((canvas_h * scale) - height) + (cfg.offset_y * scale)
        return (left, top, right, bottom)

    @staticmethod
    def legacy_cap_center(cfg: ArcConfig, angle_clock: float) -> Tuple[float, float]:
        arc_radius = (cfg.arc_diameter / 2) - (cfg.arc_thickness / 2)
        angle_rad = math.radians(ArcRenderer.to_pil_angle(angle_clock))
        # Use true center (not integer-truncated) to avoid endpoint drift,
        # especially visible on the right endcap.
        x_center = (cfg.canvas_size[0] / 2) + cfg.offset_x
        y_center = (cfg.canvas_size[1] / 2) + cfg.offset_y
        x = x_center + arc_radius * math.cos(angle_rad)
        y = y_center + arc_radius * math.sin(angle_rad)
        return (x, y)

    def draw_legacy_arc_layer(
        self,
        draw: ImageDraw.ImageDraw,
        cfg: ArcConfig,
        scale: int,
        start_clock: float,
        end_clock: float,
        arc_color: Color,
        endcap_color: Color,
    ) -> None:
        start = self.to_pil_angle(start_clock)
        end = self.to_pil_angle(end_clock)
        thickness = cfg.arc_thickness * scale

        draw.arc(
            self.legacy_arc_coords(cfg, scale),
            start,
            end,
            arc_color,
            thickness,
        )

        if cfg.show_endcaps:
            for angle in (start_clock, end_clock):
                center = self.legacy_cap_center(cfg, angle)
                self.draw_round_cap(draw, center, cfg.arc_thickness, endcap_color, scale)

    def render(self, cfg: ArcConfig) -> Image.Image:
        scale = cfg.supersample

        canvas_size = (cfg.canvas_size[0] * scale, cfg.canvas_size[1] * scale)
        track_hr = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        gauge_hr = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        track_draw = ImageDraw.Draw(track_hr, "RGBA")
        gauge_draw = ImageDraw.Draw(gauge_hr, "RGBA")

        start = self.to_pil_angle(cfg.start_angle)
        end = self.to_pil_angle(cfg.end_angle)
        full_span = (end - start) % 360
        gauge_end_clock = self.from_pil_angle((start + (full_span * cfg.gauge_value)) % 360)

        # Layer 1: background track arc (full range)
        self.draw_legacy_arc_layer(
            track_draw,
            cfg,
            scale,
            cfg.start_angle,
            cfg.end_angle,
            cfg.track_color,
            cfg.track_color,
        )

        # Layer 2: foreground gauge arc (value range)
        self.draw_legacy_arc_layer(
            gauge_draw,
            cfg,
            scale,
            cfg.start_angle,
            gauge_end_clock,
            cfg.arc_color,
            cfg.endcap_color,
        )

        if scale != 1:
            track_img = track_hr.resize(cfg.canvas_size, RESAMPLING_LANCZOS)
            gauge_img = gauge_hr.resize(cfg.canvas_size, RESAMPLING_LANCZOS)
        else:
            track_img = track_hr
            gauge_img = gauge_hr

        img = Image.new("RGBA", cfg.canvas_size, cfg.background)
        img.alpha_composite(track_img)
        img.alpha_composite(gauge_img)

        return img


# -----------------------------
# Public API
# -----------------------------

class ArcGenerator:
    def __init__(self, config: ArcConfig):
        self.config = config
        self.renderer = ArcRenderer()

    def generate(self) -> Image.Image:
        return self.renderer.render(self.config)

    def save(self, path: str) -> None:
        img = self.generate()
        img.save(path)


# -----------------------------
# Example usage
# -----------------------------

def main():
    cfg = ArcConfig(
        canvas_size=(200, 200),
        arc_diameter=180,
        arc_thickness=10,
        start_angle=235,
        end_angle=125,
        gauge_value=0.72,
        arc_color=(80, 200, 10, 255),
        track_color=(70, 70, 70, 220),
        show_endcaps=True,
        endcap_color=(80, 200, 10, 255),
        supersample=6,
        offset_x=0,
        offset_y=10
    )

    ArcGenerator(cfg).save("test/test.png")


if __name__ == "__main__":
    main()