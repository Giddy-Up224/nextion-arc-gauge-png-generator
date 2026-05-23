from PIL import Image, ImageDraw
import math

# canvas_width = 200
# canvas_height = 200
# canvas_size = [canvas_width, canvas_height]
# canvas_color = (0, 0, 0, 0)

# img = Image.new('RGBA', canvas_size, canvas_color)
# draw = ImageDraw.Draw(img)


# arc_color = (50, 50, 200)

# arc_diam = 180
# left   = ((canvas_width - arc_diam) / 2)
# top    = ((canvas_height - arc_diam) / 2)
# right  = canvas_width - left
# bottom = canvas_height - top
# # coords = [left, top, right, bottom]
# coords = [left, top, right, bottom]

# def set_rotation_ref(new_ref):
#     return clock_to_pil_rotation()

# start = clock_to_pil_rotation(0)
# stop = clock_to_pil_rotation(270)

# draw.arc(coords, start, stop, arc_color, 5)

# img.save('test/test.png')

def clock_to_pil_rotation(angle):
    return (angle - 90) % 360

class PositionAndSize:
    def __init__(self, canvas_size: list, arc_diameter: int, x_offset=0, y_offset=0):
        self.rotation = 0
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.left_margin = ((canvas_size[0] - arc_diameter) / 2) + self.x_offset
        self.top_margin = ((canvas_size[1] - arc_diameter) / 2) + self.y_offset
        self.right_margin = (canvas_size[0] - self.left_margin) + self.x_offset
        self.bottom_margin = (canvas_size[1] - self.top_margin) + self.y_offset
        self.coords = [
            self.left_margin,
            self.top_margin,
            self.right_margin,
            self.bottom_margin
        ]

    def set_zero_ref_point(self, new_ref: int):
        """
        Sets arc start reference point (0) relative to absolute 0 (12:00)
        Absolute 0 is 12:00 position, absolute 90 is 3:00
        Example: set_zero_ref_point(270) sets the arc's 0 point to 9:00 position
        """
        self.rotation = clock_to_pil_rotation(new_ref)


class ArcGenerator:
    def __init__(self):
        self.canvas_width    = 200
        self.canvas_height   = 200
        self.canvas_size     = [self.canvas_width, self.canvas_height]
        self.canvas_bg_color = (0, 0, 0, 0) # no background color
        self._arc_color      = (50, 50, 50)
        self.arc_diameter    = 180
        self.start_angle     = 0
        self.end_angle       = 125
        self.arc_width       = 10
        
    def _set_arc_start_angle(self, angle: int):
        self.pos_n_size.set_zero_ref_point(angle)

    def arc_color(self, red, green, blue):
        self._arc_color = (red, green, blue)

    def create(self):
        self.canvas     = Image.new('RGBA', self.canvas_size, self.canvas_bg_color)
        self.draw       = ImageDraw.Draw(self.canvas)
        self.pos_n_size = PositionAndSize(self.canvas_size, self.arc_diameter)
        self._end_angle = clock_to_pil_rotation(self.end_angle)
        self._set_arc_start_angle(self.start_angle)
        self.draw.arc(self.pos_n_size.coords, self.start_angle, self._end_angle, self._arc_color, self.arc_width)

    def save(self, filepath: str):
        self.canvas.save(filepath)

def main():
    arc = ArcGenerator()
    arc.create()
    arc.save('test/test.png')

if __name__ == '__main__':
    main()