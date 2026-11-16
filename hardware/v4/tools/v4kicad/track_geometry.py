"""Pure exported straight/three-point arc geometry; no CAD or process access."""
import math
from .safety import require


def require_straight(tracks,operation):
    require(not any(t.get('geometry')=='arc' for t in tracks),
            operation+' is straight-only; no arc-to-chord substitution')


def arc_geometry(track):
    a,m,b=[track[k] for k in ['start','mid','end']]
    # Translate before solving to avoid cancellation at board coordinates.
    u,v=m[0]-a[0],m[1]-a[1];x,y=b[0]-a[0],b[1]-a[1]
    d=2*(u*y-v*x)
    require(abs(d)>1e-16,'Degenerate exported arc; no chord substitution')
    cx=((u*u+v*v)*y-(x*x+y*y)*v)/d
    cy=((x*x+y*y)*u-(u*u+v*v)*x)/d
    center=[a[0]+cx,a[1]+cy];radius=math.hypot(cx,cy)
    angles=[math.atan2(p[1]-center[1],p[0]-center[0]) for p in [a,m,b]]
    sweep=(angles[2]-angles[0])%(2*math.pi)
    if (angles[1]-angles[0])%(2*math.pi)>sweep:sweep-=2*math.pi
    return center,radius,angles[0],sweep


def track_length(track):
    if track.get('geometry')!='arc':return math.dist(track['start'],track['end'])
    _,r,_,sweep=arc_geometry(track)
    calculated=r*abs(sweep)
    native=track.get('native_length_mm',calculated)
    require(abs(native-calculated)<=.0002,'Native/exported arc length disagreement')
    return native


def track_points(track,max_sag=.0001,max_step=.05):
    if track.get('geometry')!='arc':return [track['start'],track['end']]
    center,r,start,sweep=arc_geometry(track)
    max_angle=2*math.acos(max(-1,min(1,1-max_sag/r)))
    count=max(1,math.ceil(abs(sweep)/max_angle),math.ceil(r*abs(sweep)/max_step))
    require(count<=100000,'Unbounded arc approximation refused')
    points=[[center[0]+r*math.cos(start+sweep*k/count),center[1]+r*math.sin(start+sweep*k/count)]
            for k in range(count+1)]
    points[0]=track['start'];points[-1]=track['end']
    return points
