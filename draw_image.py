"""Deterministic scene-linear still-life renderer for a sun breaking from glass."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates, distance_transform_edt

SIZE = 1024
rng = np.random.default_rng(6172026)
y, x = np.mgrid[:SIZE, :SIZE].astype(np.float64)


def field(scale, u=x, v=y):
    grid = rng.random((int(SIZE / scale) + 5, int(SIZE / scale) + 5))
    return map_coordinates(grid, [v / scale + 1, u / scale + 1], order=3, mode='reflect')


def turbulence(u, v):
    return sum(weight * field(scale, u, v) for scale, weight in
               ((128, .32), (58, .25), (26, .19), (11, .13), (4, .075), (1.7, .035)))


def sample(image, u, v):
    return np.stack([map_coordinates(image[:, :, c], [v, u], order=1, mode='nearest')
                     for c in range(3)], axis=-1)


hdr = np.zeros((SIZE, SIZE, 3), dtype=np.float64)
# Indigo studio wall fades into a walnut surface with a broad, warm light pool.
wallgrain = field(33) * .012
hdr[:] = [0.009, .014, .038]
hdr += wallgrain[:, :, None] * [0.6, 1.0, 1.8]
horizon = 808
floor = np.clip((y - horizon) / 19, 0, 1)
woodgrain = field(19, x * .42 + 12 * np.sin(y / 135), y * 4.3)
woodgrain += .18 * field(3.4, x, y * 2.8) + .08 * np.sin(y * .9 + field(66) * 14)
desk = np.stack([.026 + .022 * woodgrain, .016 + .014 * woodgrain,
                 .014 + .011 * woodgrain], axis=-1)
pool = np.exp(-((x - 514) / 282) ** 2 - ((y - 856) / 95) ** 2)
desk += pool[:, :, None] * [0.63, .27, .052]
hdr = hdr * (1 - floor[:, :, None]) + desk * floor[:, :, None]
hdr *= (1 - .68 * np.exp(-((x - 513) / 110) ** 2 - ((y - 934) / 18) ** 2))[:, :, None]

# A turbulent, spherical photosphere: mottled convection below a soft plasma limb.
cx, cy, radius = 512, 390, 274
dx, dy = (x - cx) / radius, (y - cy) / radius
r = np.hypot(dx, dy)
theta = np.arctan2(dy, dx)
depth = np.sqrt(np.clip(1 - r * r, 0, 1))
warp_u = x + 39 * (field(86) - .5) + 25 * depth
warp_v = y + 42 * (field(72) - .5) - 29 * depth
convection = turbulence(warp_u, warp_v)
micro = field(2.4, warp_u, warp_v)
granulation = np.clip((convection - .31) * 2.25, 0, 1)
filament = np.clip((convection - .43) * 5.5, 0, 1)
cellular = .38 + 2.25 * granulation + 1.12 * filament + .48 * micro
cellular *= .45 + .55 * depth ** .55
core = np.exp(-((dx + .19) / .52) ** 2 - ((dy + .21) / .51) ** 2)

# Uneven arcs, fine prominences and turbulent tongues create a volumetric corona.
angular = np.zeros_like(r)
for _ in range(96):
    angle = rng.uniform(-np.pi, np.pi)
    delta = np.arctan2(np.sin(theta - angle), np.cos(theta - angle))
    width = rng.uniform(.025, .082)
    bend = (r - 1) * rng.uniform(-1.3, 1.3) + .011 * np.sin(theta * rng.integers(3, 9))
    angular += rng.uniform(.008, .055) * np.exp(-((delta - bend) / width) ** 2)
edge_noise = turbulence(x + 38 * field(52), y + 35 * field(46))
limb = 1 + angular + .075 * (edge_noise - .5)
outside = np.maximum(r - limb, 0)
corona = np.exp(-outside * 15) * (r > .96)
tongues = np.exp(-((r - limb - .018) / (.025 + .008 * np.clip(edge_noise, 0, 1))) ** 2)
plasma = corona * (.25 + 1.05 * np.clip((edge_noise - .30) * 2, 0, 1)) + tongues * .34
hdr += plasma[:, :, None] * [3.8, 1.13, .12]
disc = np.clip((1.01 - r) * 85, 0, 1)
sun = np.stack([cellular * 1.28 + core * 2.45,
                cellular ** 1.58 * .34 + core * 1.55,
                cellular ** 2 * .022 + core * .56], axis=-1)
hdr = hdr * (1 - disc[:, :, None]) + sun * disc[:, :, None]

# A narrow, turbulent plume connects the burst to the broken bottle mouth.
shaft_noise = turbulence(x * .65, y * 1.35)
shaft_width = 13 + np.clip(790 - y, 0, 170) * .18 + 7 * shaft_noise
shaft_center = 512 + 8 * np.sin(y / 29) + 7 * (shaft_noise - .5)
shaft = np.exp(-((x - shaft_center) / shaft_width) ** 2 * 1.7) * np.exp(-((y - 700) / 112) ** 4)
hdr += shaft[:, :, None] * (.55 + 1.7 * turbulence(x, y))[:, :, None] * [2.9, 1.25, .19]

# Defocused reflected light and a subtle veil around the photosphere.
hdr += np.exp(-((x - cx) / 335) ** 2 - ((y - 520) / 390) ** 2)[:, :, None] * [.13, .045, .008]

# Refractive glass bottle; a warped normal field bends the sampled background.
background = hdr.copy()
center, top, bottom, half = 512, 780, 932, 67
q = (x - center) / half
top_edge = top + 3.2 * np.sin(x * .12) + 1.8 * np.sin(x * .31)
body = (np.abs(q) < 1) & (y > top_edge) & (y < bottom - 8 + 8 * np.sqrt(np.clip(1 - q*q, 0, 1)))
edge_slope = np.clip(q, -.985, .985)
normal_x = edge_slope
normal_y = .035 * np.sin((y - top) / 16) + .018 * np.sin(x / 8)
normal_z = np.sqrt(np.clip(1 - normal_x**2 - normal_y**2, .025, 1))
offset_x = 19 * normal_x / (normal_z + .27) + 4 * normal_y
offset_y = 4.5 * normal_y / (normal_z + .25) + 2.2 * normal_x**2
refracted = sample(background, x - offset_x, y + offset_y)
fresnel = .035 + .965 * (1 - normal_z) ** 5
reflection = np.stack([.055 + .25 * normal_z, .095 + .24 * normal_z,
                       .17 + .29 * normal_z], axis=-1)
glass = refracted * [.78, .87, .93] + fresnel[:, :, None] * reflection
glass += np.stack([.015 + .028 * (1-normal_z), .025 + .05 * (1-normal_z),
                   .035 + .075 * (1-normal_z)], axis=-1)
glass *= (1 - .26 * np.abs(q)**9)[:, :, None]
softbox = np.exp(-((q + .78) / .055)**2) * np.exp(-((y - 852) / 77)**4)
warm_edge = np.exp(-((q - .86) / .038)**2) * np.exp(-((y - 850) / 77)**4)
inner = np.exp(-((q + .48) / .11)**2) * np.exp(-((y - 844) / 63)**4)
glass += (softbox[:, :, None] * [1.8, 1.9, 1.8] +
          warm_edge[:, :, None] * [2.55, 1.42, .53] +
          inner[:, :, None] * [.22, .30, .39])
hdr = np.where(body[:, :, None], glass, hdr)

# Thick bottom heel, shattered rim and refracted caustics.
for ey, ry, strength in ((926, 12, .28), (919, 9, .14), (780, 11, .85),
                         (786, 10, .40), (793, 10, .17), (801, 9, .10)):
    ellipse = np.sqrt(((x - center) / half)**2 + ((y - ey) / ry)**2)
    ring = np.exp(-((ellipse - 1) / .052)**2) * strength
    if ey < 800:
        ring *= .18 + .82 * np.clip(np.sin(x * .12 + y * .19) * 2.8, 0, 1)
    hdr += ring[:, :, None] * ([1.8, 1.22, .62] if ey < 800 else [ .48, .58, .66 ])
caustic_r = np.sqrt(((x - 514) / 106)**2 + ((y - 944) / 22)**2)
caustic = np.exp(-((caustic_r - 1) / .24)**2) * (.42 + .58 * field(11))
hdr += caustic[:, :, None] * [.55, .25, .055]

# Each splinter has a distinct shard mask, beveled thickness, normal and reflected edge.
for _ in range(33):
    angle = rng.uniform(0, 2 * np.pi)
    reach = rng.uniform(100, 305)
    px = 512 + np.cos(angle) * reach
    py = 747 - abs(np.sin(angle)) * rng.uniform(30, 200)
    if 302 < px < 724 and py < 675:
        continue
    length, width = rng.uniform(13, 42), rng.uniform(4, 14)
    rotation = rng.uniform(-3.1, 3.1)
    points = []
    for k in range(7):
        a = 2 * np.pi * k / 7
        lx = np.cos(a) * length * rng.uniform(.66, 1.24)
        ly = np.sin(a) * width * rng.uniform(.65, 1.3)
        points.append((px + lx*np.cos(rotation) - ly*np.sin(rotation),
                       py + lx*np.sin(rotation) + ly*np.cos(rotation)))
    mask_image = Image.new('L', (SIZE, SIZE))
    ImageDraw.Draw(mask_image).polygon(points, fill=255)
    mask = np.asarray(mask_image) > 0
    if not mask.any():
        continue
    distance = distance_transform_edt(mask)
    gy, gx = np.gradient(gaussian_filter(distance, .72))
    thickness = rng.uniform(.72, .94)
    refr = sample(hdr, x + gx * rng.uniform(5, 11) + np.cos(rotation) * 4,
                  y + gy * rng.uniform(5, 11) + np.sin(rotation) * 4)
    refr_color = np.array([.82, .91, .98]) * thickness
    hdr = np.where(mask[:, :, None], refr * refr_color, hdr)
    bevel = mask & (distance > .8) & (distance < rng.uniform(2.6, 4.2))
    glint = np.clip(gx * .48 - gy * .72 + .12, 0, 1) ** 4
    hdr += bevel[:, :, None] * (glint[:, :, None] * [2.65, 2.15, 1.55] + [.045, .055, .072])
    inner_bevel = mask & (distance > 2.0) & (distance < 4.0)
    hdr += inner_bevel[:, :, None] * np.clip(-gx - .4*gy, 0, 1)[:, :, None] * [.40, .25, .11]

# Scene-linear optical bloom rolls off gently into the room; DOF and grain stay restrained.
bright = np.maximum(hdr - .72, 0)
for sigma, amount in ((2.2, .13), (8, .18), (24, .16), (62, .09)):
    hdr += gaussian_filter(bright, (sigma, sigma, 0)) * amount
hdr = gaussian_filter(hdr, (0.42, 0.42, 0))
vignette = np.clip(1 - .30 * ((x - 512)**2 + (y - 476)**2) / 690000, .59, 1)
hdr *= vignette[:, :, None]
# Filmic shoulder retains the hot white-gold core and colored shadows.
a, b, c, d, e = 2.51, .03, 2.43, .59, .14
rgb = np.clip((hdr * (a*hdr + b)) / (hdr * (c*hdr + d) + e), 0, 1) ** (1/2.2)
rgb += rng.normal(0, .00055, (SIZE, SIZE, 1))
image = Image.fromarray(np.uint8(np.clip(rgb, 0, 1) * 255), mode='RGB')
image.save(Path(__file__).with_name('entry.png'), optimize=True)
image.resize((300, 300), Image.Resampling.LANCZOS).save(Path(__file__).with_name('preview.png'))
