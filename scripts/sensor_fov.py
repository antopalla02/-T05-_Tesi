"""Figures for Section 2.3: horizontal field of view of the LiDARs and RaDARs of the
AV-24 and EAV-24, overlaid on the top view of the car. Run from the repository root.
The angular extent of each sector follows the datasheets (RaDAR FoV at 150 m, the
largest range of interest in the datasets); the radii are not to scale."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Patch
from PIL import Image
plt.rcParams.update({'font.family':'serif','font.serif':['cmr10','DejaVu Serif'],'mathtext.fontset':'cm',
    'axes.formatter.use_mathtext':True,'font.size':9,'savefig.bbox':'tight'})
COL={'LiDAR':'#1F5FD1','RaDAR':'#E0302F'}
R={'LiDAR':3.6,'RaDAR':5.0}          # sector radius [m], schematic

def draw(sensors,img,extent,out):
    """sensors: (kind, X [m], Y [m], facing [deg], half FoV [deg]); X forward, Y left."""
    fig,ax=plt.subplots(figsize=(6.1,3.6))
    for kind in ['RaDAR','LiDAR']:
        for k,X,Y,f,h in sensors:
            if k!=kind: continue
            ax.add_patch(Wedge((X,Y),R[k],f-h,f+h,fc=COL[k],alpha=.16,ec='none',zorder=1))
            ax.add_patch(Wedge((X,Y),R[k],f-h,f+h,fc='none',ec=COL[k],lw=.8,alpha=.9,zorder=2))
    ax.imshow(img,extent=extent,zorder=3)
    for k,X,Y,f,h in sensors: ax.plot(X,Y,'o',ms=3.2,mfc=COL[k],mec='white',mew=.6,zorder=4)
    ax.set_aspect('equal'); ax.axis('off')
    xs=[X+R[k]*np.cos(np.radians(a)) for k,X,Y,f,h in sensors for a in np.linspace(f-h,f+h,50)]
    ax.set_xlim(min(xs)-.2,max(xs)+.2); ax.set_ylim(-R['RaDAR']-.6,R['RaDAR']+.6)
    h=[Patch(fc=COL[k],alpha=.35,ec=COL[k],label=f'{k} horizontal FoV') for k in COL]
    ax.legend(handles=h,loc='upper center',bbox_to_anchor=(.5,.02),ncol=2,frameon=False,fontsize=9)
    fig.savefig(out,dpi=300); plt.close(fig)

# AV-24: coordinates with origin at the rear axle; image mapping as in sensor_layout.py
X0A,Y0A,SCA=845,1042,0.63
img=Image.open('figures/ch2/src/av24_top.png').convert('RGBA')
A=np.array(img); A[(A[:,:,:3]>245).all(2),3]=0; img=Image.fromarray(A)   # white background -> transparent
ext=((260-X0A)/SCA/1e3,(3580-X0A)/SCA/1e3,(Y0A-1700)/SCA/1e3,(Y0A-390)/SCA/1e3)
AV=[('LiDAR',2.222,0.005,0,60),('LiDAR',1.564,0.149,112.5,60),('LiDAR',1.574,-0.153,-112.5,60),
    ('LiDAR',-0.429,-0.045,180,60),
    ('RaDAR',1.789,0,0,50),       # Continental ARS548 RDI, +-50 deg output FoV
    ('RaDAR',-0.498,0,180,45)]    # ZF FRGen21, +-45 deg up to 150 m
draw(AV,img,ext,'figures/ch2/av24_fov.pdf')

# EAV-24: coordinates with origin at the front axle
X0,Y0,SC=2197,533,0.508
img=Image.open('figures/ch2/src/eav24_top.png'); W,H=img.size
ext=((0-X0)/SC/1e3,(W-X0)/SC/1e3,(Y0-H)/SC/1e3,(Y0-0)/SC/1e3)
EAV=[('LiDAR',-0.992,0,0,60),('LiDAR',-1.652,0.190,120,60),('LiDAR',-1.652,-0.190,-120,60),
     ('RaDAR',-1.246,0,0,45),('RaDAR',-1.360,0.234,90,45),('RaDAR',-1.360,-0.234,-90,45),
     ('RaDAR',-4.204,0,180,45)]     # ZF FRGen21, +-45 deg up to 150 m
draw(EAV,img,ext,'figures/ch2/eav24_fov.pdf')
print('ok')
