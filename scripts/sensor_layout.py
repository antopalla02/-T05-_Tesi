"""Figures for Section 2.3: top view of the AV-24 and EAV-24 with the position of the
LiDARs, RaDARs and cameras. Run from the repository root.

EAV-24: positions from the sensor coordinates provided by the manufacturer (X, Y in mm,
origin at the front axle, X forward, Y to the left), mapped on the render with the front
axle position and the image scale.
AV-24: positions from the sensor coordinates of the vehicle (X, Y in mm, origin at the
rear axle), mapped on the render in the same way.
"""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from PIL import Image
plt.rcParams.update({'font.family':'serif','font.serif':['cmr10','DejaVu Serif'],'mathtext.fontset':'cm',
    'axes.formatter.use_mathtext':True,'font.size':9,'savefig.bbox':'tight'})

COL={'LiDAR':'#1F5FD1','RaDAR':'#E0302F','Camera':'#F28C1A'}
SIZE={'LiDAR':(88,54),'RaDAR':(78,34),'Camera':(42,28)}   # (length, depth) in px

def box(ax,x,y,kind,facing,k=1.0):
    """Rectangle centred in (x, y); 'facing' is the pointing direction in deg
    (0 = forward, positive towards the left side of the car)."""
    L,D=SIZE[kind]; L*=k; D*=k; a=np.radians(facing)
    d=np.array([np.cos(a),-np.sin(a)]); n=np.array([-d[1],d[0]])   # image y axis points down
    c=np.array([x,y]); P=[c+s*D/2*d+t*L/2*n for s,t in [(1,1),(1,-1),(-1,-1),(-1,1)]]
    ax.add_patch(Polygon(P,closed=True,fc=COL[kind],ec='white',lw=1.0,zorder=3))
    ax.add_patch(Polygon(P,closed=True,fc='none',ec='black',lw=0.4,zorder=4))

def legend(fig):
    h=[Patch(fc=c,ec='black',lw=0.4,label=k) for k,c in COL.items()]
    fig.legend(handles=h,loc='lower center',bbox_to_anchor=(.5,-.02),ncol=3,frameon=False,fontsize=9,handlelength=1.4)

# ---------------- EAV-24 ----------------
X0,Y0,SC=2197,533,0.508            # front axle [px], car axis [px], scale [px/mm]
EAV=[  # name, kind, X [mm], Y [mm], facing [deg]
    ('Front RaDAR','RaDAR',-1246,0,0),('Lateral RaDAR LH','RaDAR',-1360,234,90),
    ('Lateral RaDAR RH','RaDAR',-1360,-234,-90),('Rear RaDAR','RaDAR',-4204,0,180),
    ('Front LiDAR','LiDAR',-992,0,0),('Lateral LiDAR LH','LiDAR',-1652,190,120),
    ('Lateral LiDAR RH','LiDAR',-1652,-190,-120),
    ('Front camera LH','Camera',-999,160,0),('Front camera RH','Camera',-999,-160,0),
    ('Lateral camera LH','Camera',-1467,245,90),('Lateral camera RH','Camera',-1467,-245,-90),
    ('Rear camera LH','Camera',-1784,120,150),('Rear camera RH','Camera',-1784,-120,-150),
    ('Rear camera','Camera',-4179,0,180)]
OFFSET={'Rear RaDAR':(22,-45),'Rear camera':(22,45)}   # rear RaDAR and camera overlap in top view
img=Image.open('figures/ch2/src/eav24_top.png')
fig,ax=plt.subplots(figsize=(6.1,2.5))
ax.imshow(img,extent=(0,img.width,img.height,0))
for name,kind,X,Y,f in EAV:
    dx,dy=OFFSET.get(name,(0,0))
    box(ax,X0+SC*X+dx,Y0-SC*Y+dy,kind,f)
ax.set_xlim(0,img.width); ax.set_ylim(img.height,0); ax.axis('off'); legend(fig)
fig.savefig('figures/ch2/eav24_sensor_layout.pdf',dpi=300); plt.close(fig)

# ---------------- AV-24 ----------------
X0A,Y0A,SCA=845,1042,0.63          # rear axle [px], car axis [px], scale [px/mm] (original image)
AV=[  # name, kind, X [mm], Y [mm], facing [deg]  (sensor coordinates, origin at the rear axle)
    ('Front LiDAR','LiDAR',2222,5,0),('Left LiDAR','LiDAR',1564,149,112.5),
    ('Right LiDAR','LiDAR',1574,-153,-112.5),('Rear LiDAR','LiDAR',-429,-45,180),
    ('Front RaDAR','RaDAR',1789,0,0),('Rear RaDAR','RaDAR',-498,0,180),
    ('Front left camera','Camera',2232,180,0),('Front right camera','Camera',2232,-180,0),
    ('Left side camera','Camera',2020,172,100),('Right side camera','Camera',2020,-172,-100),
    ('Front roll hoop camera','Camera',1365,0,0),('Rear roll hoop camera','Camera',1215,0,180)]
OFFSET_AV={'Rear RaDAR':(0,62),'Rear LiDAR':(0,-45)}   # rear LiDAR and RaDAR overlap in top view
img=Image.open('figures/ch2/src/av24_top.png'); x0,y0,x1,y1=260,390,3580,1700   # crop of the original image
fig,ax=plt.subplots(figsize=(6.1,2.5))
ax.imshow(img,extent=(x0,x1,y1,y0))
for name,kind,X,Y,f in AV:
    dx,dy=OFFSET_AV.get(name,(0,0))
    box(ax,X0A+SCA*X+dx,Y0A-SCA*Y+dy,kind,f,k=1.2)
ax.set_xlim(x0,x1); ax.set_ylim(y1,y0); ax.axis('off'); legend(fig)
fig.savefig('figures/ch2/av24_sensor_layout.pdf',dpi=300); plt.close(fig)
print('ok')
