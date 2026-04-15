from PIL import Image, ImageDraw

# Image settings
SIZE = 800  # high-res output size (square)
DISPLAY_SIZE = 200  # final display size (square)
SCALE = 12   # supersampling factor for smoothness
BIG_SIZE = SIZE * SCALE
CENTER = BIG_SIZE // 2
RADIUS = 80 * SCALE
THICKNESS = 10 * SCALE

# Angle mapping
START_ANGLE = 135
END_ANGLE = 45
ANGLE_RANGE = (END_ANGLE - START_ANGLE) % 360

# Colors
BG_COLOR = (0, 0, 0, 0)  # transparent background
EMPTY_COLOR = (80, 80, 80)

def get_color(percent):
    """Example color gradient: red -> yellow -> green"""
    if percent < 50:
        return (255, int(5.1 * percent), 0)  # red → yellow
    else:
        return (int(255 - 5.1 * (percent - 50)), 255, 0)  # yellow → green

def draw_arc(percent):
    # Draw at high resolution for antialiasing
    img = Image.new("RGBA", (BIG_SIZE, BIG_SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    bbox = [
        CENTER - RADIUS,
        CENTER - RADIUS,
        CENTER + RADIUS,
        CENTER + RADIUS
    ]

    # Draw full background arc
    draw.arc(bbox, START_ANGLE, END_ANGLE, fill=EMPTY_COLOR, width=THICKNESS)

    # Calculate filled angle
    fill_angle = START_ANGLE + (percent / 100.0) * ANGLE_RANGE


    # Draw filled arc
    color = get_color(percent)
    draw.arc(bbox, START_ANGLE, fill_angle, fill=color, width=THICKNESS)

    # Draw rounded ends (caps) for the filled arc
    import math
    # Calculate start and end points

    def polar_to_cartesian(center, radius, angle_deg):
        angle_rad = math.radians(angle_deg)
        x = center + radius * math.cos(angle_rad)
        y = center + radius * math.sin(angle_rad)
        return (x, y)

    # Use the midpoint of the arc's thickness for cap centers
    track_radius = RADIUS - (THICKNESS / 2)
    start_xy = polar_to_cartesian(CENTER, track_radius, START_ANGLE)
    end_xy = polar_to_cartesian(CENTER, track_radius, fill_angle)

    cap_radius = THICKNESS // 2
    for xy in [start_xy, end_xy]:
        bbox_cap = [
            xy[0] - cap_radius,
            xy[1] - cap_radius,
            xy[0] + cap_radius,
            xy[1] + cap_radius
        ]
        draw.ellipse(bbox_cap, fill=color)


    # Add rounded cap to the end of the gray (unfilled) arc
    gray_cap_radius = THICKNESS // 2
    # The end of the gray arc is at END_ANGLE
    gray_end_xy = polar_to_cartesian(CENTER, track_radius, END_ANGLE)
    bbox_gray_cap = [
        gray_end_xy[0] - gray_cap_radius,
        gray_end_xy[1] - gray_cap_radius,
        gray_end_xy[0] + gray_cap_radius,
        gray_end_xy[1] + gray_cap_radius
    ]
    draw.ellipse(bbox_gray_cap, fill=EMPTY_COLOR)

    # Downscale to high-res output size
    img_hr = img.resize((SIZE, SIZE), resample=Image.LANCZOS)
    # Downscale to display size
    img_display = img_hr.resize((DISPLAY_SIZE, DISPLAY_SIZE), resample=Image.LANCZOS)
    return img_hr, img_display

# Generate 0–100%
for i in range(101):
    img_hr, img_display = draw_arc(i)
    img_hr.save(f"img/soc_{i:03d}_hr.png")
    img_display.save(f"img/soc_{i:03d}.png")

print("Done.")