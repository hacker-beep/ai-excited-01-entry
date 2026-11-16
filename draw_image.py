from PIL import Image, ImageDraw, ImageFilter
import math
import random

S = 1024
random.seed(1847)

def layer():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))

def glow(canvas, center, radius, color, blur):
    halo = layer()
    d = ImageDraw.Draw(halo)
    x, y = center
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    canvas.alpha_composite(halo.filter(ImageFilter.GaussianBlur(blur)))

im = Image.new("RGB", (S, S))
p = im.load()
for y in range(S):
    for x in range(S):
        v = max(0, 1-math.hypot((x-520)/900, (y-430)/850))
        p[x, y] = (int(7+10*y/S+12*v), int(13+13*y/S+19*v), int(39+28*y/S+46*v))
im = im.convert("RGBA")

# Broad cool beams aim toward the opening, with a warm halo behind it.
beams = layer()
bd = ImageDraw.Draw(beams)
for angle, alpha in [(-71,25),(-54,23),(-38,17),(-20,13),(8,12)]:
    a = math.radians(angle)
    vx, vy = math.cos(a), math.sin(a)
    px, py = -vy, vx
    cx, cy, reach = 578, 397, 1050
    half = 16 if alpha > 20 else 9
    bd.polygon([(cx+vx*reach+px*half,cy+vy*reach+py*half),
                (cx+vx*reach-px*half,cy+vy*reach-py*half),
                (cx-vx*130-px*half/4,cy-vy*130-py*half/4),
                (cx-vx*130+px*half/4,cy-vy*130+py*half/4)],
               fill=(83,174,255,alpha))
im.alpha_composite(beams.filter(ImageFilter.GaussianBlur(18)))
glow(im,(590,405),310,(255,103,28,75),95)
glow(im,(594,395),220,(255,203,69,80),48)

# Orbit-like arcs imply a much larger space beyond the single subject.
d = ImageDraw.Draw(im)
d.arc((120,70,1000,950),198,322,fill=(60,174,255,90),width=2)
d.arc((65,20,970,925),205,291,fill=(132,211,255,55),width=1)
d.arc((215,118,930,833),18,142,fill=(255,177,78,95),width=2)

# A cyan rim preserves the bulb silhouette around the sun's expanding globe.
glass = layer()
g = ImageDraw.Draw(glass)
left = [(418,786),(398,717),(365,661),(319,601),(282,527),(259,448),
        (262,364),(290,293),(343,232),(421,191),(510,177),(600,191),(666,224),(700,255)]
g.line(left,fill=(104,221,255,180),width=5,joint="curve")
g.line([(700,255),(675,291)],fill=(104,221,255,180),width=4)
g.line([(745,386),(772,445),(755,520),(724,572),(681,626),(646,683),(630,760)],
       fill=(104,221,255,155),width=5,joint="curve")
g.line([(355,349),(323,412),(338,478),(374,539)],fill=(184,245,255,95),width=2)
g.line([(370,594),(409,641),(430,697)],fill=(184,245,255,85),width=2)
im.alpha_composite(glass.filter(ImageFilter.GaussianBlur(5)))
im.alpha_composite(glass)

# The oversized solar disk has a lit spherical core, a drawn limb and a flowing current.
sun = layer()
s = ImageDraw.Draw(sun)
cx, cy = 610, 384
radius = 286
disk = Image.new("RGBA",(radius*2,radius*2),(0,0,0,0))
dp = disk.load()
for yy in range(radius*2):
    for xx in range(radius*2):
        nx, ny = (xx-radius)/radius, (yy-radius)/radius
        distance = math.sqrt(nx*nx+ny*ny)
        if distance <= 1:
            light = max(0,1-math.hypot(nx+.28,ny+.34)/1.45)
            edge = max(0,(distance-.72)/.28)
            dp[xx,yy] = (255, int(236-89*edge+16*light), int(156-113*edge+32*light), 255)
sun.alpha_composite(disk,(cx-radius,cy-radius))
s = ImageDraw.Draw(sun)
s.ellipse((cx-300,cy-300,cx+300,cy+300),outline=(255,151,48,255),width=13)
s.arc((cx-281,cy-281,cx+281,cy+281),205,337,fill=(255,255,223,230),width=7)
s.arc((cx-267,cy-267,cx+267,cy+267),22,153,fill=(220,78,34,220),width=12)
s.arc((cx-227,cy-227,cx+227,cy+227),185,266,fill=(255,255,246,150),width=4)
# A curved solar current cuts across the face and bends back toward the filament.
def bezier(a,b,c,d,count=48):
    points=[]
    for i in range(count+1):
        t=i/count
        q=1-t
        points.append((int(q**3*a[0]+3*q*q*t*b[0]+3*q*t*t*c[0]+t**3*d[0]),
                       int(q**3*a[1]+3*q*q*t*b[1]+3*q*t*t*c[1]+t**3*d[1])))
    return points
current = bezier((380,478),(452,335),(604,503),(829,262))
s.line(current,fill=(239,101,39,210),width=25,joint="curve")
s.line([(x,y-7) for x,y in current],fill=(255,247,183,240),width=5,joint="curve")
s.ellipse((current[0][0]-7,current[0][1]-7,current[0][0]+7,current[0][1]+7),fill=(255,255,239,255))
s.ellipse((current[-1][0]-8,current[-1][1]-8,current[-1][0]+8,current[-1][1]+8),fill=(255,255,239,255))
im.alpha_composite(sun.filter(ImageFilter.GaussianBlur(20)))
im.alpha_composite(sun)

# Long corona tongues pull the motion toward the upper-right corner.
cor = layer()
c = ImageDraw.Draw(cor)
c.polygon([(738,151),(808,50),(788,176),(875,99),(821,215),(925,176),(832,254)],fill=(255,186,57,255))
c.polygon([(832,263),(963,206),(868,302),(1002,295),(873,346)],fill=(255,119,48,255))
c.polygon([(672,104),(701,4),(714,148)],fill=(255,225,116,255))
c.polygon([(383,178),(308,101),(369,213)],fill=(255,151,48,240))
c.polygon([(879,433),(1008,468),(874,477)],fill=(255,188,67,245))
im.alpha_composite(cor.filter(ImageFilter.GaussianBlur(12)))
im.alpha_composite(cor)

# Sparse shards are sharp, translucent triangles with bright glass edges.
shards = layer()
g = ImageDraw.Draw(shards)
for points, color in [
    ([(302,319),(228,254),(269,374)],(76,194,255,92)),
    ([(279,505),(191,542),(310,555)],(102,221,255,80)),
    ([(742,276),(817,196),(777,329)],(92,206,255,100)),
    ([(765,543),(853,578),(735,591)],(84,198,255,88)),
    ([(388,231),(352,147),(425,204)],(161,233,255,88)),
    ([(708,622),(780,676),(681,657)],(95,205,255,78)),
]:
    g.polygon(points,fill=color,outline=(151,235,255,230))
    g.line([points[0],points[1],points[2]],fill=(224,252,255,195),width=2)
im.alpha_composite(shards.filter(ImageFilter.GaussianBlur(5)))
im.alpha_composite(shards)

# A few birds crossing the bright limb make the scale legible at a glance.
d = ImageDraw.Draw(im)
for x,y,z in [(882,372,1.0),(930,417,.65),(844,326,.58),(785,469,.48)]:
    d.arc((x-12*z,y-5*z,x,y+7*z),190,345,fill=(15,29,61,255),width=max(2,int(3*z)))
    d.arc((x,y-5*z,x+12*z,y+7*z),195,350,fill=(15,29,61,255),width=max(2,int(3*z)))

# The filament spirals out of the metal neck and becomes the sun's seed.
wire = layer()
w = ImageDraw.Draw(wire)
w.line([(478,754),(475,693),(503,650),(550,615),(583,568),(576,514)],
       fill=(255,235,149,255),width=7,joint="curve")
w.line([(604,755),(612,702),(587,660),(555,627),(535,590)],
       fill=(255,135,44,255),width=5,joint="curve")
w.ellipse((563,496,590,523),fill=(255,255,226,245))
im.alpha_composite(wire.filter(ImageFilter.GaussianBlur(12)))
im.alpha_composite(wire)

# Screw threads and contact pin make the tiny ordinary object unmistakable.
base = layer()
b = ImageDraw.Draw(base)
b.polygon([(430,743),(650,743),(632,858),(600,895),(480,895),(447,857)],
          fill=(22,40,75,255),outline=(127,210,255,255))
b.rectangle((438,752,643,774),fill=(60,116,151,255),outline=(189,240,255,255),width=3)
for y, inset in [(787,7),(815,13),(843,20),(867,28)]:
    b.line([(440+inset,y-5),(640-inset,y+5)],fill=(139,194,218,255),width=7)
    b.line([(443+inset,y),(637-inset,y+9)],fill=(12,25,53,255),width=4)
b.polygon([(480,895),(600,895),(579,925),(500,925)],fill=(230,158,64,255),outline=(255,229,158,255))
b.ellipse((500,914,579,934),fill=(255,212,112,255),outline=(255,245,196,255),width=3)
im.alpha_composite(base)

# The tabletop and a folded note ground the impossible event in an ordinary room.
table = layer()
t = ImageDraw.Draw(table)
t.polygon([(0,897),(1024,855),(1024,1024),(0,1024)],fill=(15,25,49,255))
t.line([(0,897),(1024,855)],fill=(105,193,228,235),width=5)
t.line([(0,914),(1024,872)],fill=(39,69,100,255),width=3)
t.polygon([(155,909),(220,904),(232,951),(168,956)],fill=(197,219,220,255),outline=(255,248,202,255))
t.line([(168,922),(209,919)],fill=(64,99,123,255),width=2)
t.line([(169,932),(213,929)],fill=(64,99,123,255),width=2)
t.line([(170,942),(198,940)],fill=(64,99,123,255),width=2)
im.alpha_composite(table)

# Controlled streaks and sparks add speed while leaving the silhouette clean.
motion = layer()
m = ImageDraw.Draw(motion)
for _ in range(34):
    x, y = random.randint(235,970), random.randint(175,790)
    dx = random.randint(18,74)
    m.line([(x,y),(x+dx,y-int(dx*.55))],
           fill=random.choice([(255,204,100,175),(121,216,255,150),(255,124,66,170)]),
           width=random.choice([1,2,3]))
for _ in range(52):
    x, y, r = random.randint(50,990), random.randint(90,850), random.choice([1,2,2,3])
    m.ellipse((x-r,y-r,x+r,y+r),fill=random.choice([(255,220,148,200),(112,209,255,170),(255,146,83,180)]))
im.alpha_composite(motion)

# Soft edge falloff protects the focal contrast.
vignette = Image.new("L",(S,S))
v = vignette.load()
for y in range(S):
    for x in range(S):
        distance = math.hypot((x-512)/725,(y-490)/760)
        v[x,y] = int(max(0,min(100,(distance-.55)*105)))
shade = Image.new("RGBA",(S,S),(3,7,24,0))
shade.putalpha(vignette)
im.alpha_composite(shade)
im.convert("RGB").save("entry.png",format="PNG",optimize=True)
