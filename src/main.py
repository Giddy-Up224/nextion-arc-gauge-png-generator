from PIL import Image, ImageDraw

#################################################################
##################      USER SETTINGS          ##################
#################################################################
DISPLAY_SIZE = 200
MARGIN = 20
SCALE = 4   # supersampling factor for smoothness. Higher numbers = smoother
ARC_THICKNESS = 15
ARC_START_ANGLE = 45
ARC_STOP_ANGLE  = 90







#################################################################
##############      DO NOT TOUCH SETTINGS          ##############
#################################################################
# Image settings
SIZE = DISPLAY_SIZE * SCALE
CENTER = SIZE // 2
# RADIUS = 80 * SCALE
RADIUS = (SIZE // 2) - MARGIN
INTERNAL_THICKNESS = ARC_THICKNESS * SCALE


# --- Angle mapping (clock face to PIL, counterclockwise fill) ---
def clock_to_pil(angle):
    return (90 - angle) % 360

START_ANGLE = clock_to_pil(ARC_STOP_ANGLE)
END_ANGLE = clock_to_pil(ARC_START_ANGLE)
# For clockwise fill, range is (END - START) % 360
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
    img = Image.new("RGBA", (SIZE, SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    bbox = [
        CENTER - RADIUS,
        CENTER - RADIUS,
        CENTER + RADIUS,
        CENTER + RADIUS
    ]



    # Draw full background arc (from START to END, clockwise)
    draw.arc(bbox, START_ANGLE, END_ANGLE, fill=EMPTY_COLOR, width=INTERNAL_THICKNESS)

    # Calculate filled angle for clockwise fill
    fill_angle = (START_ANGLE + (percent / 100.0) * ANGLE_RANGE) % 360

    # Draw filled arc
    color = get_color(percent)
    draw.arc(bbox, START_ANGLE, fill_angle, fill=color, width=INTERNAL_THICKNESS)

    # Draw rounded ends (caps) for the filled arc
    import math
    # Calculate start and end points

    def polar_to_cartesian(center, radius, angle_deg):
        angle_rad = math.radians(angle_deg)
        x = center + radius * math.cos(angle_rad)
        y = center + radius * math.sin(angle_rad)
        return (x, y)


    # Use the midpoint of the arc's thickness for cap centers
    track_radius = RADIUS - (INTERNAL_THICKNESS / 2)
    start_xy = polar_to_cartesian(CENTER, track_radius, START_ANGLE)
    end_xy = polar_to_cartesian(CENTER, track_radius, fill_angle)

    # Add rounded cap to the end of the gray (unfilled) arc FIRST (at END_ANGLE)
    gray_cap_radius = INTERNAL_THICKNESS // 2
    gray_end_xy = polar_to_cartesian(CENTER, track_radius, END_ANGLE)
    bbox_gray_cap = [
        gray_end_xy[0] - gray_cap_radius,
        gray_end_xy[1] - gray_cap_radius,
        gray_end_xy[0] + gray_cap_radius,
        gray_end_xy[1] + gray_cap_radius
    ]
    draw.ellipse(bbox_gray_cap, fill=EMPTY_COLOR)

    # Now draw colored arc caps so they overwrite if needed
    cap_radius = INTERNAL_THICKNESS // 2
    for xy in [start_xy, end_xy]:
        bbox_cap = [
            xy[0] - cap_radius,
            xy[1] - cap_radius,
            xy[0] + cap_radius,
            xy[1] + cap_radius
        ]
        draw.ellipse(bbox_cap, fill=color)


    # Downscale to display size only
    img_display = img.resize((DISPLAY_SIZE, DISPLAY_SIZE), resample=Image.LANCZOS)
    return img_display


# Generate 0–100%, in increments of 5
for i in range(0, 101, 5):
    img_display = draw_arc(i)
    img_display.save(f"out/soc_{i:03d}.png")

print("Done.")