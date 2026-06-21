"""
Generate baseball-themed textures for the Baseball Addon.

These are clean, on-theme procedural textures (navy cap, white pinstripe
uniform, wood-grain bat, black cleats) — far better than flat placeholders,
but still intended to be replaced with hand-painted art in Blockbench before
publishing.

  python3 generate_textures.py

Layout notes:
  * Item icons are 16x16 (inventory/hotbar).
  * bat_model.png is 48x32 — wide enough to fit the bat geo's barrel UV box,
    which overflows a 32-wide atlas (see bat.geo.json texture_width: 48).
  * Worn-armor atlases are 64x32. Pinstripes are drawn as full-atlas vertical
    lines so they map to vertical stripes on every box face regardless of the
    exact UV unwrap.
"""
import struct, zlib, os

# ---------------------------------------------------------------------------
# PNG encoder (RGBA, color type 6)
# ---------------------------------------------------------------------------
def write_png(path, w, h, pixels):
    raw = b""
    for y in range(h):
        raw += b"\x00"  # filter type: None
        for x in range(w):
            r, g, b, a = pixels[y * w + x]
            raw += bytes([r, g, b, a])
    compressed = zlib.compress(raw, 9)

    def chunk(name, data):
        return (struct.pack(">I", len(data)) + name + data
                + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">II", w, h) + bytes([8, 6, 0, 0, 0])  # 8-bit RGBA
    blob = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", compressed)
            + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(blob)
    print(f"wrote {path}  ({w}x{h})")


# ---------------------------------------------------------------------------
# Tiny drawing canvas
# ---------------------------------------------------------------------------
TRANSPARENT = (0, 0, 0, 0)

# Baseball palette
WHITE   = (244, 244, 240, 255)   # home-white uniform
CREAM   = (236, 232, 220, 255)
NAVY    = (24, 36, 92, 255)       # cap + pinstripes
NAVY_HI = (40, 56, 120, 255)      # cap highlight
RED     = (190, 44, 44, 255)       # stitching accent
RED_DK  = (150, 28, 28, 255)       # barrel grain shadow
BLACK   = (26, 26, 30, 255)        # cleats / outline
GREY    = (120, 122, 130, 255)
SILVER  = (188, 192, 200, 255)     # metal spikes
WOOD    = (198, 152, 96, 255)      # ash-bat light
WOOD_MID= (172, 126, 74, 255)
WOOD_DK = (138, 98, 54, 255)       # grain
KNOB    = (110, 76, 42, 255)


class Canvas:
    def __init__(self, w, h, fill=TRANSPARENT):
        self.w, self.h = w, h
        self.px = [fill] * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y * self.w + x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def pinstripes(self, base, stripe, step=3, x0=0, y0=0, x1=None, y1=None):
        x1 = self.w - 1 if x1 is None else x1
        y1 = self.h - 1 if y1 is None else y1
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, stripe if x % step == 0 else base)


# ---------------------------------------------------------------------------
# 16x16 item icons
# ---------------------------------------------------------------------------
def icon_bat():
    c = Canvas(16, 16)
    # tapered barrel (top-right) down to thin handle + knob (bottom-left)
    steps = 48
    for i in range(steps + 1):
        t = i / steps
        x = 3 + (12 - 3) * t          # handle -> barrel along the diagonal
        y = 13 - (13 - 3) * t
        r = 0.9 + 1.6 * t             # widen toward the barrel
        c.disc(x, y, r + 0.6, BLACK)  # dark outline first
    for i in range(steps + 1):
        t = i / steps
        x = 3 + (12 - 3) * t
        y = 13 - (13 - 3) * t
        r = 0.9 + 1.6 * t
        col = WOOD_DK if (i % 6 == 0) else (WOOD_MID if t < 0.45 else WOOD)
        c.disc(x, y, r, col)
    c.disc(3, 13, 1.9, BLACK)         # knob outline
    c.disc(3, 13, 1.3, KNOB)          # knob
    return c


def icon_helmet():
    c = Canvas(16, 16)
    # cap dome (upper half disc) + bill to the right + button
    c.disc(7, 9, 5.2, BLACK)
    c.disc(7, 9, 4.4, NAVY)
    c.rect(0, 10, 15, 15, TRANSPARENT)        # clip to upper dome
    c.disc(7, 9, 4.4, NAVY)
    c.rect(0, 10, 15, 15, TRANSPARENT)
    # bill (front of cap points right)
    c.rect(8, 9, 14, 10, BLACK)
    c.rect(8, 9, 13, 9, NAVY)
    # button + highlight
    c.set(7, 3, NAVY_HI)
    c.disc(5, 7, 1.4, NAVY_HI)
    return c


def icon_jersey():
    c = Canvas(16, 16)
    body_x0, body_x1 = 4, 11
    # short sleeves
    c.rect(1, 5, 3, 9, BLACK); c.rect(2, 6, 3, 8, WHITE)
    c.rect(12, 5, 14, 9, BLACK); c.rect(12, 6, 13, 8, WHITE)
    # body outline + white fill
    c.rect(body_x0 - 1, 4, body_x1 + 1, 15, BLACK)
    c.rect(body_x0, 5, body_x1, 14, WHITE)
    # thin navy pinstripes down the body (accents on white, not 50% fill)
    for x in range(body_x0, body_x1 + 1):
        if (x - body_x0) % 3 == 1:
            c.rect(x, 5, x, 14, NAVY)
    # collar / placket
    c.rect(6, 4, 9, 5, NAVY)
    c.rect(7, 5, 8, 8, NAVY)
    return c


def icon_pants():
    c = Canvas(16, 16)
    # belt
    c.rect(3, 3, 12, 4, BLACK)
    c.rect(4, 3, 11, 3, NAVY)
    # two legs
    c.rect(4, 4, 7, 15, BLACK); c.rect(8, 4, 11, 15, BLACK)
    c.rect(4, 4, 6, 14, WHITE); c.rect(9, 4, 11, 14, WHITE)
    # one thin pinstripe per leg so the white reads through
    c.rect(5, 5, 5, 14, NAVY)
    c.rect(10, 5, 10, 14, NAVY)
    return c


def icon_cleats():
    c = Canvas(16, 16)
    # boot upper (heel left, toe right)
    c.rect(2, 6, 12, 11, BLACK)
    c.disc(11, 9, 2.6, BLACK)
    # ankle collar + laces
    c.rect(2, 5, 6, 6, BLACK)
    c.set(4, 7, WHITE); c.set(4, 9, WHITE); c.set(4, 11, WHITE)  # laces
    # sole
    c.rect(2, 12, 13, 12, GREY)
    # metal spikes
    for sx in (3, 6, 9, 12):
        c.set(sx, 13, SILVER)
    return c


def icon_baseball():  # not wired to an item; handy spare / future ball
    c = Canvas(16, 16)
    c.disc(8, 8, 7, BLACK)
    c.disc(8, 8, 6, WHITE)
    for y in range(3, 14):
        c.set(4, y, RED); c.set(12, y, RED)
    return c


def pack_icon(size=128):
    """A baseball (white ball, red seams) on navy — pack-list icon for BP & RP."""
    c = Canvas(size, size, NAVY)
    cx = cy = (size - 1) / 2
    r = size * 0.40
    th = size * 0.022                        # seam thickness
    c.disc(cx, cy, r + size * 0.02, BLACK)   # thin dark rim
    c.disc(cx, cy, r, WHITE)
    # Two seams that bulge outward and meet near the top/bottom poles: ( )
    for y in range(size):
        ny = (y - cy) / r
        if abs(ny) >= 0.985:
            continue
        off = 0.60 * r * (1 - ny * ny) ** 0.5
        for x in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                continue
            if abs(abs(x - cx) - off) < th:
                c.set(x, y, RED)
        # stitch ticks every few rows, angled off each seam
        if y % max(2, int(size * 0.05)) == 0:
            for s in (-1, 1):
                bx = cx + s * off
                for t in range(1, int(size * 0.035) + 1):
                    c.set(int(bx + s * t), y - t, RED)
                    c.set(int(bx + s * t), y + t, RED)
    return c


# ---------------------------------------------------------------------------
# 3D bat model texture (48x32) — wood grain across the whole atlas
# ---------------------------------------------------------------------------
def bat_model():
    c = Canvas(48, 32, WOOD)
    grain_cols = {1, 4, 5, 9, 13, 14, 18, 22, 25, 29, 33, 34, 38, 42, 45}
    for x in range(48):
        for y in range(32):
            if x in grain_cols:
                c.set(x, y, WOOD_DK)
            elif (x * 3 + y) % 7 == 0:
                c.set(x, y, WOOD_MID)
    # Paint barrel UV region red: x=[12,35] y=[0,17] (barrel sides+top/bottom)
    # and end cap UV region: x=[12,31] y=[24,29]
    for x in range(12, 36):
        for y in range(0, 18):
            shade = RED_DK if (x in grain_cols or (x * 3 + y) % 7 == 0) else RED
            c.set(x, y, shade)
    for x in range(12, 32):
        for y in range(24, 30):
            c.set(x, y, RED_DK if (x * 3 + y) % 7 == 0 else RED)
    return c


# ---------------------------------------------------------------------------
# Worn-armor atlases (64x32)
# ---------------------------------------------------------------------------
def armor_jersey():
    c = Canvas(64, 32)
    c.pinstripes(WHITE, NAVY, step=3)
    return c


def armor_pants():
    c = Canvas(64, 32)
    c.pinstripes(WHITE, NAVY, step=3)
    return c


def armor_helmet():
    c = Canvas(64, 32, NAVY)
    # subtle top highlight band so the cap reads with some depth
    c.rect(0, 0, 63, 2, NAVY_HI)
    return c


def armor_cleats():
    c = Canvas(64, 32, BLACK)
    # grey sole strip + a couple of silver spikes for definition
    c.rect(0, 10, 21, 12, GREY)
    c.rect(0, 26, 21, 31, GREY)
    return c


# ---------------------------------------------------------------------------
# Catcher gear icons and armor textures
# ---------------------------------------------------------------------------
def icon_catcher_mask():
    c = Canvas(16, 16)
    # Navy cap dome (same as helmet but no brim)
    c.disc(7, 8, 5.2, BLACK)
    c.disc(7, 8, 4.4, NAVY)
    c.rect(0, 11, 15, 15, TRANSPARENT)
    c.disc(7, 8, 4.4, NAVY)
    # Iron cage bars across the face
    c.rect(3, 11, 12, 11, GREY)    # top cage bar
    c.rect(3, 15, 12, 15, GREY)    # chin bar
    for bx in (4, 7, 10):
        for by in range(12, 15):
            c.set(bx, by, GREY)
    # Highlight
    c.set(7, 2, NAVY_HI)
    c.disc(5, 6, 1.4, NAVY_HI)
    return c


def icon_catcher_vest():
    c = Canvas(16, 16)
    # Wide padded body outline
    c.rect(2, 4, 13, 15, BLACK)
    c.rect(3, 5, 12, 14, NAVY)
    # Horizontal quilting lines for the padded look
    for y in (8, 11):
        c.rect(3, y, 12, y, NAVY_HI)
    # Collar
    c.rect(5, 4, 10, 5, NAVY_HI)
    c.rect(6, 5, 9, 7, NAVY_HI)
    # Shoulder pads (wider than a jersey)
    c.rect(1, 4, 2, 8, BLACK)
    c.rect(13, 4, 14, 8, BLACK)
    c.rect(1, 4, 2, 7, NAVY)
    c.rect(13, 4, 14, 7, NAVY)
    return c


def armor_catcher_mask():
    # 64x32: cap area is NAVY; cage bar UV regions are iron grey
    c = Canvas(64, 32, NAVY)
    c.rect(0, 0, 63, 2, NAVY_HI)
    # Clear the face area (North face of the head cube: x=[8,15], y=[8,15])
    c.rect(8, 8, 15, 15, TRANSPARENT)
    # Cage UV regions (from geo UV layout)
    c.rect(0, 18, 17, 19, GREY)   # top bar
    c.rect(20, 18, 33, 19, GREY)  # chin bar
    c.rect(0, 22, 3, 28, GREY)    # side rail
    c.rect(6, 22, 9, 26, GREY)    # vertical bars
    return c


def armor_catcher_vest():
    # 64x32: solid navy with quilted horizontal lines on the torso front face
    # Torso front face UV: x=[4,12), y=[4,16) (box [8,12,4] at UV [0,0])
    c = Canvas(64, 32, NAVY)
    c.rect(0, 0, 63, 1, NAVY_HI)
    for y in (7, 10, 13):
        c.rect(4, y, 11, y, NAVY_HI)
    return c


# ---------------------------------------------------------------------------
# Build everything
# ---------------------------------------------------------------------------
jobs = [
    ("Baseball_RP/textures/items/bat.png",     icon_bat()),
    ("Baseball_RP/textures/items/helmet.png",  icon_helmet()),
    ("Baseball_RP/textures/items/jersey.png",  icon_jersey()),
    ("Baseball_RP/textures/items/pants.png",   icon_pants()),
    ("Baseball_RP/textures/items/cleats.png",  icon_cleats()),
    ("Baseball_RP/textures/items/bat_model.png", bat_model()),
    ("Baseball_RP/textures/models/armor/baseball_jersey.png", armor_jersey()),
    ("Baseball_RP/textures/models/armor/baseball_helmet.png", armor_helmet()),
    ("Baseball_RP/textures/models/armor/baseball_pants.png",  armor_pants()),
    ("Baseball_RP/textures/models/armor/baseball_cleats.png", armor_cleats()),
    ("Baseball_RP/textures/items/catcher_mask.png",  icon_catcher_mask()),
    ("Baseball_RP/textures/items/catcher_vest.png",  icon_catcher_vest()),
    ("Baseball_RP/textures/models/armor/baseball_catcher_mask.png", armor_catcher_mask()),
    ("Baseball_RP/textures/models/armor/baseball_catcher_vest.png", armor_catcher_vest()),
    ("Baseball_BP/pack_icon.png", pack_icon(128)),
    ("Baseball_RP/pack_icon.png", pack_icon(128)),
]

for path, canvas in jobs:
    write_png(path, canvas.w, canvas.h, canvas.px)

print("\nDone! Baseball-themed textures generated. Replace with hand-painted "
      "art in Blockbench for a final release.")
