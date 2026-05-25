from PIL import Image, ImageDraw
import math

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


class ArcGenerator:
    def __init__(self):
        self.smoothing_scale = 6 # for eliminating pixelation
        self.canvas_width    = 200
        self.canvas_height   = 200
        self.transparency         = 0
        self.canvas_bg_color = (0, 0, 0)
        self._arc_color      = (50, 50, 50)
        self.arc_diameter    = 180
        self.start_angle     = 270
        self.end_angle       = 90
        self.arc_thickness   = 10
        self.vert_offset     = 0
        self.horiz_offset    = 0
        self.use_endcaps     = True
        self.endcap_color    = self._arc_color

    def set_arc_color(self, red, green, blue):
        self._arc_color = (red, green, blue)

    
    def clock_to_pil_rotation(self, angle):
        return (angle - 90) % 360
    
    def upscale(self, value):
        return value * self.smoothing_scale
    
    def polar_to_cartesian(self, angle_user):
        self.arc_radius = (self.arc_diameter // 2) - (self.arc_thickness // 2)
        angle_math = self.clock_to_pil_rotation(angle_user)
        angle_rad = math.radians(angle_math)
        self.x_center = (self.canvas_width // 2) + self.horiz_offset
        self.y_center = (self.canvas_height // 2) + self.vert_offset
        x = self.x_center + self.arc_radius * math.cos(angle_rad)
        y = self.y_center + self.arc_radius * math.sin(angle_rad)
        return (x, y)

    def create(self):
        self._canvas_size        = [self.upscale(self.canvas_width), self.upscale(self.canvas_height)]
        self._cvs_color          = (*self.canvas_bg_color, (255 - self.transparency))
        self.canvas              = Image.new('RGBA', self._canvas_size, self._cvs_color)
        self.draw                = ImageDraw.Draw(self.canvas)
        self.pos_n_size          = PositionAndSize(self._canvas_size, self.upscale(self.arc_diameter))
        self.pos_n_size.x_offset = self.upscale(self.horiz_offset)
        self.pos_n_size.y_offset = self.upscale(self.vert_offset)
        self.pos_n_size.update()
        self._start_angle = self.clock_to_pil_rotation(self.start_angle)
        print(f"Start angle (user): {self.start_angle}, PIL: {self._start_angle}")
        self._end_angle = self.clock_to_pil_rotation(self.end_angle)
        print(f"End angle (user)  : {self.end_angle}, PIL: {self._end_angle}")
        self.draw.arc(self.pos_n_size.coords, self._start_angle, self._end_angle, self._arc_color, self.upscale(self.arc_thickness))
        # Add endcap
        if self.use_endcaps:
            start_xy = self.polar_to_cartesian(235)
            end_xy = self.polar_to_cartesian(125)
            for xy in [start_xy, end_xy]:
                self.draw.ellipse(
                    [
                        self.upscale(xy[0] - (self.arc_thickness / 2)),
                        self.upscale(xy[1] - (self.arc_thickness / 2)),
                        self.upscale(xy[0] + (self.arc_thickness / 2)),
                        self.upscale(xy[1] + (self.arc_thickness / 2))
                    ],
                    self.endcap_color
                )
        # Downscale
        self.canvas = self.canvas.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)

    def save(self, filepath: str):
        self.canvas.save(filepath)

def main():
    arc = ArcGenerator()
    arc.canvas_width    = 400
    arc.canvas_height   = 400
    arc.canvas_bg_color = (0, 0, 0)
    # arc.endcap_color    = (255, 201, 78)
    # arc.use_endcaps     = False
    arc.arc_diameter    = 375
    arc.transparency    = 255
    arc.start_angle     = 235
    arc.end_angle       = 125
    arc.arc_thickness   = 10
    arc.vert_offset     = 6
    arc.horiz_offset    = 0
    arc.set_arc_color(255, 201, 78)
    arc.create()
    arc.save('test/test.png')

if __name__ == '__main__':
    main()