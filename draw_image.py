"""Draw an original solar hatching poster; no external image inputs."""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math
import random

SIZE = 1024
rng = random.Random(62017)
yy, xx = np.mgrid[0:SIZE, 0:SIZE]

def sheet():
    return Image.new('RGBA', (SIZE, SIZE))

def composite(art, blur=0):
    global canvas
    canvas = Image.alpha_composite(canvas, art.filter(ImageFilter.GaussianBlur(blur)) if blur else art)

def stroke(points, color, width=1, blur=0):
    art = sheet()
    ImageDraw.Draw(art).line(points, fill=color, width=width, joint='curve')
    composite(art, blur)

def curve(a, b, c, d, steps=80):
    result = []
    for k in range(steps+1):
        t = k/steps
        u = 1-t
        result.append((u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],
                       u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1]))
    return result

def haze(x, y, rx, ry, color, strength):
    a = np.exp(-(((xx-x)/rx)**2+((yy-y)/ry)**2)*2)*strength
    data = np.zeros((SIZE,SIZE,4), dtype=np.uint8)
    data[:,:,:3] = color
    data[:,:,3] = a.astype(np.uint8)
    composite(Image.fromarray(data))

# A dark room gives the impossible newborn star all of the visual space.
v = np.maximum(0, 1-np.hypot((xx-560)/950, (yy-420)/950))
bg = np.stack((8+v*9+yy*.004, 13+v*16, 35+v*35), axis=-1).astype(np.uint8)
canvas = Image.fromarray(bg).convert('RGBA')
haze(600,390,470,480,(255,100,19),155)
haze(390,640,410,520,(25,102,190),80)

# Directional rays move diagonally out of the bulb rather than radiating evenly.
art = sheet()
d = ImageDraw.Draw(art)
for angle, reach, width, alpha in [(-48,1000,31,55),(-35,1000,19,48),(-64,920,19,38),(15,850,12,25),(-152,800,12,20)]:
    a = math.radians(angle)
    vx,vy = math.cos(a),math.sin(a)
    px,py = -vy,vx
    d.polygon([(570,590),(570+vx*reach+px*width,590+vy*reach+py*width),
               (570+vx*reach-px*width,590+vy*reach-py*width)],fill=(255,192,83,alpha))
composite(art,8)

# Surviving bulb walls: asymmetric, fractured, and visibly smaller than the sun.
left = curve((444,779),(415,627),(248,603),(265,405))
left += curve((265,405),(258,287),(331,218),(403,198))
right = curve((648,774),(652,664),(739,631),(769,535))
for pts in [left,right]:
    stroke(pts,(47,184,244,110),15,9)
    stroke(pts,(104,220,255,210),4)
stroke(curve((309,377),(288,471),(345,549),(375,568)),(173,237,255,95),2)

# Tapered flame loops bend with the diagonal solar wind.
cx,cy,radius = 606,365,276
for angle,length,width in [(-134,74,14),(-105,68,13),(-79,100,18),(-52,163,24),(-29,130,20),(-8,100,14),(24,80,13),(64,51,11),(162,53,10)]:
    a = math.radians(angle)
    vx,vy = math.cos(a),math.sin(a)
    tx,ty = -vy,vx
    start=(cx+vx*(radius-15),cy+vy*(radius-15))
    tip=(cx+vx*(radius+length)+tx*length*.30,cy+vy*(radius+length)+ty*length*.30)
    end=(cx+vx*(radius+4)+tx*40,cy+vy*(radius+4)+ty*40)
    path=curve(start,(start[0]+vx*length*.50-tx*length*.35,
                     start[1]+vy*length*.50-ty*length*.35),
               (tip[0]-vx*length*.15+tx*length*.35,
                tip[1]-vy*length*.15+ty*length*.35),tip)
    def tongue(scale, color):
        edge1=[]; edge2=[]
        for k,(x,y) in enumerate(path):
            t=k/(len(path)-1)
            before=path[max(0,k-1)]; after=path[min(len(path)-1,k+1)]
            dx=after[0]-before[0]; dy=after[1]-before[1]
            norm=max(.001,math.hypot(dx,dy))
            w=width*scale*(1-t)**.8*(.65+.6*math.sin(t*math.pi))
            edge1.append((x-dy/norm*w,y+dx/norm*w))
            edge2.append((x+dy/norm*w,y-dx/norm*w))
        art=sheet()
        ImageDraw.Draw(art).polygon(edge1+edge2[::-1],fill=color)
        return art
    flame=tongue(1,(255,123,9,255))
    composite(flame,11); composite(flame)
    composite(tongue(.50,(255,197,54,255)))
    composite(tongue(.15,(255,249,185,245)),1)

# Analytic turbulence: multiple warped scales make a living solar photosphere.
nx=(xx-cx)/radius
ny=(yy-cy)/radius
rr=np.hypot(nx,ny)
theta=np.arctan2(ny,nx)
# Smooth, seeded noise is warped into giant vortices, with smaller convection cells.
noise_rng=np.random.default_rng(62017)
def field(cells):
    coarse=(noise_rng.random((cells,cells))*255).astype(np.uint8)
    return np.asarray(Image.fromarray(coarse).resize((SIZE,SIZE),Image.Resampling.BICUBIC)).astype(float)/255
n1,n2,n3,n4=field(8),field(22),field(57),field(165)
# Several local vortices avoid a synthetic pinwheel singularity at the center.
u=xx.astype(float).copy(); v=yy.astype(float).copy()
for ox,oy,reach,spin in [(480,290,225,2.2),(710,410,190,-1.8),(490,520,150,1.7)]:
    dx=u-ox; dy=v-oy
    turn=spin*np.exp(-(dx*dx+dy*dy)/(reach*reach))
    u=ox+dx*np.cos(turn)-dy*np.sin(turn)
    v=oy+dx*np.sin(turn)+dy*np.cos(turn)
def sample(arr):
    xi=np.clip(u,0,SIZE-2); yi=np.clip(v,0,SIZE-2)
    ix=xi.astype(int); iy=yi.astype(int)
    fx=xi-ix; fy=yi-iy
    return (arr[iy,ix]*(1-fx)*(1-fy)+arr[iy,ix+1]*fx*(1-fy)
            +arr[iy+1,ix]*(1-fx)*fy+arr[iy+1,ix+1]*fx*fy)
a,b,c,d=sample(n1),sample(n2),sample(n3),sample(n4)
texture=.40*a+.30*b+.20*c+.10*d
ridges=(1-np.abs(2*(.58*b+.29*c+.13*d)-1))**9
core=np.exp(-(((nx+.20)/.40)**2+((ny+.17)/.36)**2)*2)
limb=np.clip((rr-.70)/.30,0,1)
light=np.clip(.12+.74*texture+.24*ridges+.54*core-.28*limb,0,1)
surface=np.zeros((SIZE,SIZE,4),dtype=np.uint8)
surface[:,:,0]=255
surface[:,:,1]=np.clip(91+164*light,0,255)
surface[:,:,2]=np.clip(3+245*light**3.0,0,255)
surface[:,:,3]=np.where(rr<=1,255,0)
solar=Image.fromarray(surface)
composite(solar,18)
composite(solar)

# A single broad rising current breaks into tapered subsidiary tongues.
eddies=sheet()
e=ImageDraw.Draw(eddies)
paths=[curve((377,488),(493,307),(646,518),(819,227)),
       curve((428,535),(574,450),(733,551),(842,350)),
       curve((419,248),(457,185),(553,169),(643,231))]
for j,points in enumerate(paths):
    for k in range(len(points)-1):
        t=k/(len(points)-1)
        width=int((29 if j==0 else 15)*math.sin(math.pi*t)**.6)+1
        e.line(points[k:k+2],fill=(201,66,8,45 if j==0 else 0),width=width)
        shifted=[(x-1,y-6) for x,y in points[k:k+2]]
        e.line(shifted,fill=(255,247,164,70 if j==0 else 0),width=max(1,width//4))
mask=Image.fromarray(np.where(rr<=.965,255,0).astype(np.uint8))
eddies.putalpha(Image.fromarray((np.asarray(eddies.getchannel('A')).astype(float)*np.asarray(mask)/255).astype(np.uint8)))
composite(eddies,3)
haze(551,325,105,92,(255,255,223),140)
# Thin limb highlights keep the sphere readable against its corona.
limb_art=sheet()
e=ImageDraw.Draw(limb_art)
e.arc((cx-radius,cy-radius,cx+radius,cy+radius),185,307,fill=(255,250,194,255),width=5)
e.arc((cx-radius,cy-radius,cx+radius,cy+radius),5,103,fill=(255,136,27,255),width=7)
composite(limb_art)

# The neck ruptures in a sharp elliptical crown, not a random scatter.
ring=sheet()
d=ImageDraw.Draw(ring)
d.arc((365,591,742,723),5,173,fill=(255,159,35,255),width=18)
d.arc((365,591,742,723),12,169,fill=(255,255,211,255),width=6)
for a in range(190,356,18):
    t=math.radians(a)
    x=554+181*math.cos(t)
    y=659+60*math.sin(t)
    d.line([(x,y),(x+math.cos(t)*24,y+math.sin(t)*37)],fill=(219,250,255,230),width=3)
# Alternating bright facets mark an actual fractured glass lip.
for degrees in [17,34,58,83,112,139,165]:
    a=math.radians(degrees)
    x=554+188*math.cos(a); y=657+64*math.sin(a)
    h=10+(degrees%4)*4
    d.polygon([(x-9,y),(x+3,y-h),(x+12,y+3)],fill=(191,245,255,230))
composite(ring,14)
composite(ring)

# Each glass splinter has a coherent outward trajectory and a swept light trail.
shard_specs=[(285,284,-.85,-.85,54),(190,535,-1,.02,48),(355,157,-.4,-1,32),
             (811,214,.65,-.9,53),(863,568,1,-.15,51),(778,714,.8,.5,38),
             (328,702,-.8,.5,33),(932,346,1,-.4,26)]
for x,y,vx,vy,z in shard_specs:
    stroke([(x-vx*105,y-vy*105),(x,y)],(94,207,255,100),7,5)
    stroke([(x-vx*82-8,y-vy*82+8),(x-vx*15-8,y-vy*15+8)],(153,232,255,155),2)
    pts=[(x+vx*z,y+vy*z),(x-vy*z*.42,y+vx*z*.42),(x-vx*z*.40+vy*z*.22,y-vy*z*.40-vx*z*.22)]
    art=sheet(); d=ImageDraw.Draw(art)
    d.polygon(pts,fill=(64,152,202,130),outline=(174,240,255,255))
    d.line([pts[0],pts[1]],fill=(245,255,251,255),width=3)
    composite(art,3); composite(art)

# Filament roots tie the new sun physically to the ordinary metal bulb base.
for pts,w in [(curve((478,786),(453,694),(528,700),(557,625)),6),
              (curve((614,785),(642,699),(583,713),(578,646)),5)]:
    stroke(pts,(255,139,22,255),w*3,10)
    stroke(pts,(255,242,168,255),w)

# A desk with a broad warm spill grounds the scale and reflects the event.
art=sheet(); d=ImageDraw.Draw(art)
d.polygon([(0,902),(1024,860),(1024,1024),(0,1024)],fill=(16,25,43,255))
d.line([(0,902),(1024,860)],fill=(94,145,176,255),width=3)
composite(art)
spill=sheet()
pix=np.zeros((SIZE,SIZE,4),dtype=np.uint8)
fall=np.exp(-(((xx-550)/300)**2+((yy-921)/62)**2)*2)
pix[:,:,:3]=(255,157,52)
pix[:,:,3]=np.where(yy>902-xx*.041,fall*160,0).astype(np.uint8)
composite(Image.fromarray(pix))
for offset in [0,23,57]:
    stroke([(260-offset,944+offset//2),(780+offset,920+offset//2)],(249,176,86,45),2)

# Curved screw threads are lit gold on one side and cool blue on the other.
art=sheet(); d=ImageDraw.Draw(art)
d.ellipse((423,872,660,923),fill=(5,10,23,220))
d.polygon([(430,764),(650,764),(628,871),(594,900),(482,900),(450,869)],fill=(35,48,61,255),outline=(143,191,205,255))
for y,inset in [(775,0),(799,5),(823,10),(847,16),(869,25)]:
    pts=curve((440+inset,y),(494,y+16),(578,y+21),(642-inset,y+4))
composite(art)
for y,inset in [(775,0),(799,5),(823,10),(847,16),(869,25)]:
    pts=curve((440+inset,y),(494,y+16),(578,y+21),(642-inset,y+4))
    stroke(pts,(7,18,33,255),13)
    stroke([(x,y-4) for x,y in pts],(128,174,190,255),7)
    stroke([(x,y-5) for x,y in pts[:44]],(255,214,132,255),4)
art=sheet(); d=ImageDraw.Draw(art)
d.rounded_rectangle((496,895,585,921),radius=10,fill=(179,132,65,255),outline=(255,216,139,255),width=3)
composite(art)

# A sparse flock scatters across the limb, silhouettes rather than decoration.
for x,y,z,tilt in [(818,395,12,-.4),(854,432,9,.3),(799,454,7,-.5),(895,405,6,.2)]:
    pts=[(x-z,y-4),(x-z*.4,y-7+tilt*z),(x,y),(x+z*.4,y-7-tilt*z),(x+z,y-3)]
    stroke(pts,(13,24,41,255),3)
# Fine sparks follow the same diagonal acceleration.
for k in range(43):
    x=rng.randint(240,960); y=rng.randint(80,780)
    if math.hypot(x-cx,y-cy)<radius+22:
        continue
    length=rng.randint(3,22)
    stroke([(x,y),(x+length,y-length*.65)],(255,194,96,rng.randint(90,210)),rng.choice([1,1,2]))
canvas = canvas.filter(ImageFilter.GaussianBlur(.65))
canvas.convert('RGB').save('entry.png',optimize=True)
canvas.convert('RGB').resize((300,300),Image.Resampling.LANCZOS).save('preview.png')
