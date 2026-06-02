from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import math
from PIL import Image, ImageDraw


Color = Tuple[int, int, int, int]


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

    arc_color: Color = (50, 50, 50, 255)

    show_endcaps: bool = True
    endcap_color: Color = (50, 50, 50, 255)

    offset_x: int = 0
    offset_y: int = 0

    supersample: int = 4  # replaces "smoothing_factor"


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

        cx = (w / 2) + cfg.offset_x * scale
        cy = (h / 2) + cfg.offset_y * scale

        bbox = (
            cx - diameter / 2,
            cy - diameter / 2,
            cx + diameter / 2,
            cy + diameter / 2,
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
    def polar_point(center, radius, angle_deg):
        angle_rad = math.radians(ArcRenderer.to_pil_angle(angle_deg))
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        return x, y

    def render(self, cfg: ArcConfig) -> Image.Image:
        scale = cfg.supersample

        canvas_size = (cfg.canvas_size[0] * scale, cfg.canvas_size[1] * scale)
        img = Image.new("RGBA", canvas_size, cfg.background)
        draw = ImageDraw.Draw(img)

        geom = ArcGeometryBuilder.build(cfg, scale)

        start = self.to_pil_angle(cfg.start_angle)
        end = self.to_pil_angle(cfg.end_angle)

        thickness = cfg.arc_thickness * scale

        draw.arc(
            geom.bbox,
            start=start,
            end=end,
            fill=cfg.arc_color,
            width=thickness,
        )

        if cfg.show_endcaps:
            for angle in (cfg.start_angle, cfg.end_angle):
                x, y = self.polar_point(geom.center, geom.radius, angle)

                r = thickness / 2
                draw.ellipse(
                    [x - r, y - r, x + r, y + r],
                    fill=cfg.endcap_color,
                )

        # downscale for smoothing
        if scale != 1:
            img = img.resize(cfg.canvas_size, Image.Resampling.LANCZOS)

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
        arc_color=(80, 200, 10, 255),
        show_endcaps=True,
        endcap_color=(80, 200, 10, 255),
        supersample=4,
    )

    ArcGenerator(cfg).save("test/test.png")


if __name__ == "__main__":
    main()