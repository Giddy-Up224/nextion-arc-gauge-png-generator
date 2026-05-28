from PIL import Image, ImageDraw
import math
from dataclasses import dataclass

# Next steps:
# - Add another arc on top for the gauge
# - Allow changing the color of the endcaps independently of the arc color
# - Make the endcaps optional
# - Add rounded ends to the arcs
# - Allow setting colors for both arcs
# - Allow setting arc widths independently
# - Add PySide6 UI
#   - Provide controls for outputting arcs for every n angle
#   - Allow providing a gradient of colors for the arcs
#   - Allow gradually changing the color of the arc based on the value
#     Example: 0 = red, 25 = red/yellow, 50 = yellow, 75 = yellow/green, 100 = green
#   - Use color picker

class PositionAndSize:
    def __init__(self, canvas_size: list, arc_diameter: int, x_offset=0, y_offset=0):
        self.canvas_size = canvas_size
        self.arc_diameter = arc_diameter
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.update()
        

    def update(self):
        width = (self.canvas_size[0] - self.arc_diameter) / 2
        height = (self.canvas_size[1] - self.arc_diameter) / 2
        self.left_margin = width + self.x_offset
        self.top_margin = height + self.y_offset
        self.right_margin = (self.canvas_size[0] - width) + self.x_offset
        self.bottom_margin = (self.canvas_size[1] - height) + self.y_offset
        
        self.coords = [
            self.left_margin,
            self.top_margin,
            self.right_margin,
            self.bottom_margin
        ]

@dataclass
class ArcProperties:
    smoothing_scale:int   = 6
    canvas_width:   int   = 200
    canvas_height:  int   = 200
    canvas_bg_color:tuple = (0, 0, 0, 0)
    _arc_color:     tuple = (50, 50, 50, 255)
    arc_diameter:   int   = 180
    start_angle:    int   = 235
    end_angle:      int   = 125
    arc_thickness:  int   = 10
    vert_offset:    int   = 0
    horiz_offset:   int   = 0
    use_endcaps:    bool  = True
    endcap_color:   tuple = (50, 50, 50, 255)


class ArcGenerator:
    def __init__(self, properties: ArcProperties):
        self.prop = properties
    
    def clock_to_pil_rotation(self, angle):
        return (angle - 90) % 360
    
    def upscale(self, value):
        return value * self.prop.smoothing_scale
    
    def polar_to_cartesian(self, angle_user):
        self.arc_radius = ((self.prop.arc_diameter / 2) - (self.prop.arc_thickness / 2))
        angle_math = self.clock_to_pil_rotation(angle_user)
        angle_rad = math.radians(angle_math)
        self.x_center = (self.prop.canvas_width // 2) + self.prop.horiz_offset
        self.y_center = (self.prop.canvas_height // 2) + self.prop.vert_offset
        x = self.x_center + self.arc_radius * math.cos(angle_rad)
        y = self.y_center + self.arc_radius * math.sin(angle_rad)
        return (x, y)

    def create_canvas(self):
        self._canvas_size        = [self.upscale(self.prop.canvas_width), self.upscale(self.prop.canvas_height)]
        self.canvas              = Image.new('RGBA', self._canvas_size, self.prop.canvas_bg_color)
        self.draw                = ImageDraw.Draw(self.canvas, 'RGBA')
        self.pos_n_size          = PositionAndSize(self._canvas_size, self.upscale(self.prop.arc_diameter))

    def draw_arc(self):
        # TODO: Use center path for arc creation to allow remaining centered
        # when making the top arc wider than the background arc
        self.pos_n_size.x_offset = self.upscale(self.prop.horiz_offset)
        self.pos_n_size.y_offset = self.upscale(self.prop.vert_offset)
        self.pos_n_size.update()
        self._start_angle = self.clock_to_pil_rotation(self.prop.start_angle)
        print(f"Start angle (user): {self.prop.start_angle}, PIL: {self._start_angle}")
        self._end_angle = self.clock_to_pil_rotation(self.prop.end_angle)
        print(f"End angle (user)  : {self.prop.end_angle}, PIL: {self._end_angle}")
        print(f"Arc color:    {self.prop._arc_color}")
        print(f"Endcap color: {self.prop.endcap_color}")
        self.draw.arc(self.pos_n_size.coords, self._start_angle, self._end_angle, self.prop._arc_color, self.upscale(self.prop.arc_thickness))
        # Add endcaps
        if self.prop.use_endcaps:
            start_xy = self.polar_to_cartesian(self.prop.start_angle)
            end_xy = self.polar_to_cartesian(self.prop.end_angle)
            for xy in [start_xy, end_xy]:
                self.draw.ellipse(
                    [
                        self.upscale(xy[0] - (self.prop.arc_thickness / 2)),
                        self.upscale(xy[1] - (self.prop.arc_thickness / 2)),
                        self.upscale(xy[0] + (self.prop.arc_thickness / 2)),
                        self.upscale(xy[1] + (self.prop.arc_thickness / 2))
                    ],
                    self.prop.endcap_color
                )

    def save(self, filepath: str):
        # Downscale
        self.canvas = self.canvas.resize((self.prop.canvas_width, self.prop.canvas_height), Image.LANCZOS) # type: ignore[attr-defined]
        self.canvas.save(filepath)



def main():
    background = ArcProperties()
    arc = ArcGenerator(background)
    arc.create_canvas()
    arc.draw_arc()
    arc.save('test/test.png')

if __name__ == '__main__':
    main()