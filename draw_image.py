"""Seeded HDR plasma / refractive glass still life. No external image assets."""
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates, distance_transform_edt
from PIL import Image, ImageDraw

S = 1024
rng = np.random.default_rng(62017)
y, x = np.mgrid[:S, :S].astype(np.float64)

def noise(scale, u=x, v=y):
    grid = rng.random((int(S / scale)+5, int(S / scale)+5))
    return map_coordinates(grid, [v/scale+1, u/scale+1], order=3, mode='reflect')

def fbm(u, v):
    return sum(w*noise(s,u,v) for s,w in [(100,.38),(43,.26),(18,.18),(7,.11),(2.5,.07)])

def sample(a, u, v):
    return np.stack([map_coordinates(a[:,:,c], [v,u], order=1, mode='nearest') for c in range(3)],-1)

def add(field, color):
    global hdr
    hdr += field[:,:,None]*np.array(color)

# Defocused indigo studio, distant wall, and tactile walnut tabletop.
wall = fbm(x,y)
hdr = np.zeros((S,S,3)) + [0.009, .017, .045]
hdr += wall[:,:,None]*np.array([.012,.018,.035])
horizon = 807
floor = np.clip((y-horizon)/24,0,1)
wood = noise(18, x*.36 + 12*np.sin(y/150), y*5) + .16*noise(3,x,y*3)
wood += .13*np.sin(y*.9+noise(65)*14)+.08*noise(1.4)
lightpool = np.exp(-((x-518)/260)**2-((y-859)/95)**2)
desk = np.stack([.035+.025*wood,.022+.015*wood,.019+.012*wood],-1)
desk += lightpool[:,:,None]*[.58,.24,.055]
hdr = hdr*(1-floor[:,:,None])+desk*floor[:,:,None]
# Soft contact shadow under the jar.
hdr *= (1-.77*np.exp(-((x-514)/114)**2-((y-934)/18)**2))[:,:,None]
add(np.exp(-((x-514)/320)**2-((y-566)/350)**2),[.20,.058,.009])

# Photosphere: spherical coordinates, domain-warped convection, emissive granules.
cx, cy, radius = 511, 392, 271
dx,dy=(x-cx)/radius,(y-cy)/radius
r=np.hypot(dx,dy)
theta=np.arctan2(dy,dx)
z=np.sqrt(np.clip(1-r*r,0,1))
u=x+42*(noise(75)-.5)+24*z
v=y+44*(noise(67)-.5)-32*z
conv=fbm(u,v)
fine=noise(3.1,u,v)
# Many irregular flame fingers, with turbulent soft volume boundaries.
angular = np.zeros_like(r)
for k in range(58):
    angle=rng.uniform(-np.pi,np.pi)
    delta=np.arctan2(np.sin(theta-angle),np.cos(theta-angle))
    bend=.85*(r-1)*np.sin(angle*5)
    angular += rng.uniform(.025,.14)*np.exp(-((delta-bend)/rng.uniform(.035,.085))**2)
warp=fbm(x+45*noise(43),y+45*noise(39))
edge=1+angular+.055*(warp-.5)
corona=np.exp(-np.maximum(r-1,0)*14)*(r>.98)
flames=np.exp(-((r-1.015)/(edge-.95))**2*2)*(r>.98)
filaments=np.clip((warp-.36)*2.3,0,1)**2
emission=(corona*.32+flames*2.8)*( .25+filaments)
add(emission,[3.7,.77,.055])
# Volumetric column rises out of the broken mouth and feeds the sphere.
columnwidth=17+np.clip((780-y),0,180)*.20
column=np.exp(-((x-512-10*np.sin(y/33))/columnwidth)**2*2)*np.exp(-((y-700)/102)**4)
add(column*(.5+2*fbm(x,y)),[3.4,1.55,.25])
mask=np.clip((1.003+.017*(warp-.5)-r)*90,0,1)
granules=np.clip((conv-.25)*1.7,0,1)
lanes=np.clip((conv-.38)*5,0,1)
intensity=(.35+2.4*granules+1.3*lanes+.65*fine)*(.40+.60*z**.45)
core=np.exp(-((dx+.22)/.55)**2-((dy+.20)/.50)**2)
solar=np.stack([intensity*1.35+core*2.2,intensity**1.6*.31+core*1.5,intensity**2*.022+core*.68],-1)
hdr=hdr*(1-mask[:,:,None])+solar*mask[:,:,None]

# Tiny broken cylindrical preserving jar: normal-map refraction and Fresnel reflection.
background=hdr.copy()
center=513; top=778; bottom=932; half=67
q=(x-center)/half
topedge=top+4*np.sin(x*.15)+3*np.sin(x*.37)
body=(np.abs(q)<1)&(y>topedge)&(y<bottom-7+7*np.sqrt(np.clip(1-q*q,0,1)))
nx=np.clip(q,-.999,.999)
nz=np.sqrt(np.clip(1-nx*nx,.001,1))
# Air/glass index 1.52: stronger offsets through curved outer walls.
refx=x-18*nx/(nz+.22)
refy=y+3*np.sin((y-top)/150*np.pi)+2*nx*nx
refracted=sample(background,refx,refy)
fresnel=.04+.96*(1-nz)**5
reflection=np.stack([.06+.3*nz,.12+.20*nz,.22+.16*nz],-1)
glass=refracted*np.array([.82,.91,.94])+fresnel[:,:,None]*reflection
    # Glass thickness attenuates light most strongly at grazing angles.
glass *= (1-.38*np.abs(q)**8)[:,:,None]
# Interior warm reflections and narrow softbox / sun streaks.
left=np.exp(-((q+.79)/.035)**2)*np.exp(-((y-854)/71)**4)
right=np.exp(-((q-.88)/.023)**2)*np.exp(-((y-855)/72)**4)
back=np.exp(-((q+.51)/.08)**2)*np.exp(-((y-847)/60)**4)
glass+=(left[:,:,None]*[1.5,1.65,1.55]+right[:,:,None]*[2.4,1.22,.35]+back[:,:,None]*[.22,.28,.33])
hdr=np.where(body[:,:,None],glass,hdr)
# Thick elliptical base and fractured bright lip with reflected underside.
for ey, ry, strength in [(925,12,.27),(918,10,.14),(779,13,1.0),(785,12,.32),(794,12,.12),(801,12,.09)]:
    er=np.sqrt(((x-center)/half)**2+((y-ey)/ry)**2)
    ring=np.exp(-((er-1)/.065)**2)*strength
    if ey<800:
        ring *= .22+.78*np.clip(np.sin(x*.13+y*.17)*3,0,1)
    add(ring,[1.8,1.04,.36] if ey<800 else [.55,.64,.65])
# Bright caustic on the table, optically stretched behind the base.
caustic=np.exp(-((np.sqrt(((x-514)/94)**2+((y-944)/19)**2)-1)/.12)**2)
add(caustic*.14,[1.7,.85,.20])

# Irregular curved glass fragments, each refracting its own background region.
for i in range(24):
    a=rng.uniform(0,2*np.pi)
    reach=rng.uniform(100,300)
    px=512+np.cos(a)*reach
    py=742-abs(np.sin(a))*rng.uniform(35,190)
    if 300<px<735 and py<675: continue
    length=rng.uniform(12,38); width=rng.uniform(5,16)
    angle=rng.uniform(-3,3)
    pts=[]
    for k in range(6):
        t=2*np.pi*k/6
        lx=np.cos(t)*length*rng.uniform(.7,1.2)
        ly=np.sin(t)*width*rng.uniform(.65,1.2)
        pts.append((px+lx*np.cos(angle)-ly*np.sin(angle),py+lx*np.sin(angle)+ly*np.cos(angle)))
    im=Image.new('L',(S,S)); ImageDraw.Draw(im).polygon(pts,fill=255)
    m=np.array(im)>0
    dist=distance_transform_edt(m)
    gy,gx=np.gradient(gaussian_filter(dist,1))
    refr=sample(hdr,x+gx*8+np.cos(angle)*5,y+gy*8+np.sin(angle)*4)
    reflected=(.07+.2*np.maximum(0,gx*.7-gy))[:,:,None]*np.array([.5,.72,1.0])
    hdr=np.where(m[:,:,None],refr*.86+reflected,hdr)
    edge=m&(dist<1.6)
    spec=np.clip(gx*.5-gy*.8,0,1)**5
    hdr+=edge[:,:,None]*(spec[:,:,None]*[4,2.8,1.3]+[.025,.035,.05])
    # Inner bevel catches a separate warm reflection, giving the shard thickness.
    bevel=m&(dist>1.6)&(dist<3.0)
    hdr+=bevel[:,:,None]*np.maximum(0,-gx-gy)[:,:,None]*[.34,.17,.04]

# Sensor response: multiscale lens bloom in scene-linear light, then filmic exposure.
bright=np.maximum(hdr-.9,0)
for sigma, weight in [(2,.15),(9,.20),(29,.20),(75,.12)]:
    hdr+=gaussian_filter(bright,(sigma,sigma,0))*weight
vignette=np.clip(1-.35*((x-512)**2+(y-480)**2)/650000,.55,1)
hdr*=vignette[:,:,None]
# ACES-like shoulder preserves white-hot emission and rich photographic shadows.
a,b,c,d,e=2.51,.03,2.43,.59,.14
rgb=np.clip((hdr*(a*hdr+b))/(hdr*(c*hdr+d)+e),0,1)**(1/2.2)
rgb+=rng.normal(0,.00065,(S,S,1))
img=Image.fromarray(np.uint8(np.clip(rgb,0,1)*255))
# RGB output preserves smooth optical gradients without palette banding.
img.save(Path(__file__).with_name('entry.png'),optimize=True)
img.convert('RGB').resize((300,300),Image.Resampling.LANCZOS).save(Path(__file__).with_name('preview.png'))
