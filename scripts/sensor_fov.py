"""Horizontal field of view of the LiDARs and RaDARs of the AV-24 and EAV-25 (Section 2.2),
overlaid on the top view of the car. Run from the repository root.
The angular extent of each sector follows the datasheets; the radii are not to scale.
The top views are embedded at full resolution (interpolation='none' in a vector backend)."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Patch
from PIL import Image
plt.rcParams.update({'font.family':'serif','font.serif':['cmr10','DejaVu Serif'],'mathtext.fontset':'cm',
    'axes.formatter.use_mathtext':True,'font.size':9,'savefig.bbox':'tight'})
COL={'LiDAR':'#1F5FD1','RaDAR':'#E0302F'}
RAD=6.0                                  # sector radius [m], schematic

def limits(sensors,extent):
    """Plot limits relative to the center of the car image."""
    cx,cy=(extent[0]+extent[1])/2,(extent[2]+extent[3])/2
    xs=[X+RAD*np.cos(np.radians(a))-cx for X,Y,f,h in sensors for a in np.linspace(f-h,f+h,90)]
    ys=[Y+RAD*np.sin(np.radians(a))-cy for X,Y,f,h in sensors for a in np.linspace(f-h,f+h,90)]
    return min(xs),max(xs),min(ys),max(ys)

def draw(kind,sensors,img,extent,lim,out):
    """sensors: (X [m], Y [m], facing [deg], half FoV [deg]); X forward, Y left.
    All the figures share the same limits (relative to the car center) and size."""
    cx,cy=(extent[0]+extent[1])/2,(extent[2]+extent[3])/2
    fig=plt.figure(figsize=(6.1,3.9)); ax=fig.add_axes([0,.08,1,.92])
    for X,Y,f,h in sensors:
        ax.add_patch(Wedge((X,Y),RAD,f-h,f+h,fc=COL[kind],alpha=.18,ec='none',zorder=1))
        ax.add_patch(Wedge((X,Y),RAD,f-h,f+h,fc='none',ec=COL[kind],lw=.8,zorder=2))
    ax.imshow(img,extent=extent,zorder=3,interpolation='none')
    for X,Y,f,h in sensors:
        ax.plot(X,Y,'o',ms=4.5,mfc=COL[kind],mec='white',mew=.7,zorder=4)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(cx+lim[0]-.2,cx+lim[1]+.2); ax.set_ylim(cy+lim[2]-.2,cy+lim[3]+.2)
    fig.legend(handles=[Patch(fc=COL[kind],alpha=.35,ec=COL[kind],label=f'{kind} horizontal FoV')],
               loc='lower center',bbox_to_anchor=(.5,0),frameon=False,fontsize=9)
    fig.savefig(out,dpi=300,bbox_inches=None); plt.close(fig)

# sensors and images
AV_IMG=Image.open('figures/ch2/src/av24_top_hr.png')
AV_EXT=(-0.866,4.278,-0.989,0.982)                         # origin at the rear axle
AV_L=[(2.222,0.005,0,60),(1.564,0.149,112.5,60),(1.574,-0.153,-112.5,60)]
AV_R=[(1.789,0,0,50),(-0.498,0,180,45)]
EAV_IMG=Image.open('figures/ch2/src/eav24_top_hr.png'); W,H=EAV_IMG.size
X0,Y0,SC=2197,533,0.508                                    # origin at the front axle
EAV_EXT=((0-X0)/SC/1e3,(W-X0)/SC/1e3,(Y0-H)/SC/1e3,(Y0-0)/SC/1e3)
EAV_L=[(-0.992,0,0,60),(-1.652,0.190,120,60),(-1.652,-0.190,-120,60)]
EAV_R=[(-1.246,0,0,45),(-1.360,0.234,90,45),(-1.360,-0.234,-90,45),(-4.204,0,180,45)]

L=[limits(s,e) for s,e in [(AV_L,AV_EXT),(AV_R,AV_EXT),(EAV_L,EAV_EXT),(EAV_R,EAV_EXT)]]
m=max(max(abs(l[0]),abs(l[1])) for l in L); n=max(max(abs(l[2]),abs(l[3])) for l in L)
LIM=(-m,m,-n,n)
draw('LiDAR',AV_L,AV_IMG,AV_EXT,LIM,'figures/ch2/av24_lidar_fov.pdf')
draw('RaDAR',AV_R,AV_IMG,AV_EXT,LIM,'figures/ch2/av24_radar_fov.pdf')
draw('LiDAR',EAV_L,EAV_IMG,EAV_EXT,LIM,'figures/ch2/eav24_lidar_fov.pdf')
draw('RaDAR',EAV_R,EAV_IMG,EAV_EXT,LIM,'figures/ch2/eav24_radar_fov.pdf')
print('ok',LIM)
