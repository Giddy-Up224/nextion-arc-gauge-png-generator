from PIL import Image, ImageDraw
import math

canvas_width = 200
canvas_height = 200
canvas_size = (canvas_width, canvas_height)
canvas_color = (0, 0, 0, 0)

img = Image.new('RGBA', canvas_size, canvas_color)
draw = ImageDraw.Draw(img)


arc_color = (100, 100, 200)

arc_diam = 190
left   = ((canvas_width - arc_diam) / 2)
top    = ((canvas_height - arc_diam) / 2)
right  = canvas_width - left
bottom = canvas_height - top
# coords = [left, top, right, bottom]
coords = [left, top, right, bottom]

def clock_to_pil_rotation(angle):
    return (angle - 90) % 360

start = clock_to_pil_rotation(0)
stop = clock_to_pil_rotation(270)

draw.arc(coords, start, stop, arc_color, 5)

img.save('test/test.png')