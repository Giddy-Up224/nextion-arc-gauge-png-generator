from PIL import Image, ImageDraw
import math

#################################################################
##################      USER SETTINGS          ##################
#################################################################
DISPLAY_SIZE     = 200
MARGIN           = 20
SCALE            = 4
ARC_THICKNESS    = 15
ARC_START_ANGLE  = 270
ARC_STOP_ANGLE   = 90
ARC_COLOR        = (0, 0, 255) # Red, Green, Blue
ARC_BG_COLOR     = (0, 100, 100) # Red, Green, Blue
TICK_STEP        = 2 # Step size. Example: 5 will produce 20 pngs, 2 will produce 50 pngs


#################################################################
##############      INTERNAL SETTINGS          ##################
#################################################################
SIZE = DISPLAY_SIZE * SCALE
CENTER = SIZE // 2
RADIUS = (SIZE // 2) - MARGIN
INTERNAL_THICKNESS = ARC_THICKNESS * SCALE

BG_COLOR = (0, 0, 0, 0)
EMPTY_COLOR = ARC_BG_COLOR


#################################################################
##################   ANGLE HANDLING (FIXED)   ##################
#################################################################


def user_to_pil(angle):
    return (90 - angle) % 360


# Work entirely in USER space (clockwise)
ANGLE_RANGE = (ARC_START_ANGLE - ARC_STOP_ANGLE) % 360


def polar_to_cartesian(center, radius, angle_user):
    angle_math = (90 - angle_user) % 360
    angle_rad = math.radians(angle_math)

    x = center + radius * math.cos(angle_rad)
    y = center + radius * math.sin(angle_rad)
    return (x, y)


#################################################################
##################        DRAW FUNCTION        ##################
#################################################################


def draw_arc(percent):
    img = Image.new("RGBA", (SIZE, SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    bbox = [CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS]

    # Compute angles in USER space
    fill_user = (ARC_START_ANGLE - (percent / 100.0) * ANGLE_RANGE) % 360

    # Convert ONLY when drawing
    start_pil = user_to_pil(ARC_START_ANGLE)
    stop_pil = user_to_pil(ARC_STOP_ANGLE)
    fill_pil = user_to_pil(fill_user)

    # Background arc
    draw.arc(bbox, start_pil, stop_pil, fill=EMPTY_COLOR, width=INTERNAL_THICKNESS)

    # Filled arc
    draw.arc(bbox, start_pil, fill_pil, fill=ARC_COLOR, width=INTERNAL_THICKNESS)

    # Caps
    track_radius = RADIUS - (INTERNAL_THICKNESS / 2)

    start_xy = polar_to_cartesian(CENTER, track_radius, ARC_START_ANGLE)
    end_xy = polar_to_cartesian(CENTER, track_radius, fill_user)
    gray_end_xy = polar_to_cartesian(CENTER, track_radius, ARC_STOP_ANGLE)

    cap_radius = INTERNAL_THICKNESS // 2

    # Gray end cap
    draw.ellipse(
        [
            gray_end_xy[0] - cap_radius,
            gray_end_xy[1] - cap_radius,
            gray_end_xy[0] + cap_radius,
            gray_end_xy[1] + cap_radius,
        ],
        fill=EMPTY_COLOR,
    )

    # Colored caps
    for xy in [start_xy, end_xy]:
        draw.ellipse(
            [
                xy[0] - cap_radius,
                xy[1] - cap_radius,
                xy[0] + cap_radius,
                xy[1] + cap_radius,
            ],
            fill=ARC_COLOR,
        )

    # Downscale
    return img.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.LANCZOS)


#################################################################
##################      IMAGE GENERATION       ##################
#################################################################

for i in range(0, 101, TICK_STEP):
    img = draw_arc(i)
    img.save(f"out/soc_{i:03d}.png")

print("Done.")
