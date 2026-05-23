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


class PositionAndSize:
    def __init__(self, canvas_size: list, arc_diameter: int, x_offset=0, y_offset=0):
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


class ArcGenerator:
    def __init__(self):
        self.canvas_width    = 200
        self.canvas_height   = 200
        self.canvas_size     = [self.canvas_width, self.canvas_height]
        self.canvas_bg_color = (0, 0, 0, 0) # no background color
        self._arc_color      = (50, 50, 50)
        self.arc_diameter    = 180
        self.start_angle     = 270
        self.end_angle       = 90
        self.arc_width       = 10

    def set_arc_color(self, red, green, blue):
        self._arc_color = (red, green, blue)

    
    def clock_to_pil_rotation(self, angle):
        return (angle - 90) % 360

    def create(self):
        self.canvas     = Image.new('RGBA', self.canvas_size, self.canvas_bg_color)
        self.draw       = ImageDraw.Draw(self.canvas)
        self.pos_n_size = PositionAndSize(self.canvas_size, self.arc_diameter)
        self._start_angle = self.clock_to_pil_rotation(self.start_angle)
        print(f"Start angle (user): {self.start_angle}, PIL: {self._start_angle}")
        self._end_angle = self.clock_to_pil_rotation(self.end_angle)
        print(f"End angle (user): {self.end_angle}, PIL: {self._end_angle}")
        self.draw.arc(self.pos_n_size.coords, self._start_angle, self._end_angle, self._arc_color, self.arc_width)

    def save(self, filepath: str):
        self.canvas.save(filepath)

def main():
    arc = ArcGenerator()
    arc.create()
    arc.save('test/test.png')

if __name__ == '__main__':
    main()