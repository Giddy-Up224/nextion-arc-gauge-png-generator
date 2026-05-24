from PIL import Image, ImageDraw
import math


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
        self.canvas_width    = 200
        self.canvas_height   = 200
        self.opacity         = 0
        self.canvas_bg_color = (0, 0, 0)
        self._arc_color      = (50, 50, 50)
        self.arc_diameter    = 180
        self.start_angle     = 270
        self.end_angle       = 90
        self.arc_thickness   = 10
        self.vert_offset     = 0
        self.horiz_offset    = 0

    def set_arc_color(self, red, green, blue):
        self._arc_color = (red, green, blue)

    
    def clock_to_pil_rotation(self, angle):
        return (angle - 90) % 360

    def create(self):
        self.canvas_size     = [self.canvas_width, self.canvas_height]
        self._cvs_color = (*self.canvas_bg_color, (255 - self.opacity))
        self.canvas     = Image.new('RGBA', self.canvas_size, self._cvs_color)
        self.draw       = ImageDraw.Draw(self.canvas)
        self.pos_n_size = PositionAndSize(self.canvas_size, self.arc_diameter)
        self.pos_n_size.x_offset = self.horiz_offset
        self.pos_n_size.y_offset = self.vert_offset
        self.pos_n_size.update()
        self._start_angle = self.clock_to_pil_rotation(self.start_angle)
        print(f"Start angle (user): {self.start_angle}, PIL: {self._start_angle}")
        self._end_angle = self.clock_to_pil_rotation(self.end_angle)
        print(f"End angle (user): {self.end_angle}, PIL: {self._end_angle}")
        self.draw.arc(self.pos_n_size.coords, self._start_angle, self._end_angle, self._arc_color, self.arc_thickness)

    def save(self, filepath: str):
        self.canvas.save(filepath)

def main():
    arc = ArcGenerator()
    arc.canvas_width = 200
    arc.canvas_height = 200
    arc.canvas_bg_color = (255, 255, 255)
    arc.opacity = 255
    arc.start_angle = 235
    arc.end_angle = 125
    arc.vert_offset = 6
    arc.horiz_offset = 0
    arc.set_arc_color(255, 255, 255)
    arc.create()
    arc.save('test/test.png')

if __name__ == '__main__':
    main()