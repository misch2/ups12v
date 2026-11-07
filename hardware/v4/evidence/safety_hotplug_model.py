"""Bounded passive state-space screen. No CAD writes, no charger behavioral model.

Vs--Rs,Lc--A--Rf,Lf--B(VAC1)--Ron,Lon--C(VBUS)
             |         |                 |
           Ld,Rd,Cd   C9                Cbus
             |         |                 |
            PGND      PGND              PGND
Small Ca at A regularizes the distributed model (assumed PCB parasitic).
The FET-off model omits the B-C branch. Capacitors use constant Ceff.
"""
from pathlib import Path
import itertools, json
import numpy as np
E = Path(__file__).resolve().parent
VS = 21.
def run(lc, rs, cd, lf, mode, initial=0., cb=20., samples=40001):
    # States: cable current, A, snubber current, snubber C voltage,
    #         feed current, B, [FET current, C]
    on = mode != 'fet_off'
    ca, c9, cd, cb = 1e-9, .1e-6, cd*1e-6, cb*1e-6
    lc, lf, ld, lon = lc*1e-6, lf*1e-9, 20e-9, 20e-9
    rd, rf, ron = 1.9, .02, .02
    n = 8 if on else 6
    a = np.zeros((n,n)); u = np.zeros(n)
    a[0,0]=-rs/lc; a[0,1]=-1/lc; u[0]=VS/lc
    a[1,0]=1/ca; a[1,2]=-1/ca; a[1,4]=-1/ca
    a[2,1]=1/ld; a[2,2]=-rd/ld; a[2,3]=-1/ld
    a[3,2]=1/cd
    a[4,1]=1/lf; a[4,4]=-rf/lf; a[4,5]=-1/lf
    a[5,4]=1/c9
    if on:
        a[5,6]=-1/c9
        a[6,5]=1/lon; a[6,6]=-ron/lon; a[6,7]=-1/lon
        a[7,6]=1/cb
    steady = -np.linalg.solve(a,u)
    x0 = steady * (initial/VS)
    if mode == 'abrupt_fet_enable':
        x0 = steady.copy(); x0[7]=0
    poles, vec = np.linalg.eig(a)
    assert np.max(poles.real)<0
    end=max(200e-6,12/min(-poles.real))
    t=np.linspace(0,end,samples)
    amp=vec*np.linalg.solve(vec,x0-steady)[None,:]
    z=steady[:,None]+np.sum(amp[:,:,None]*np.exp(poles[None,:,None]*t),axis=1)
    assert np.max(np.abs(z.imag))<1e-5
    z=z.real; p=rd*z[2]**2
    er=np.trapezoid(p,t)
    # Energy balance independently checks passive equations and time sampling.
    weights=np.array([lc,ca,ld,cd,lf,c9]+([lon,cb] if on else []))
    stored=lambda x:float(.5*np.sum(weights*x*x))
    losses=rs*z[0]**2+p+rf*z[4]**2+(ron*z[6]**2 if on else 0)
    supplied=np.trapezoid(VS*z[0],t)
    balance=abs(supplied-np.trapezoid(losses,t)-stored(z[:,-1])+stored(x0))
    relative=balance/max(abs(supplied),stored(x0),1e-12)
    assert relative<.005,relative
    return dict(mode=mode,Lc_uH=lc*1e6,Rs_ohm=rs,Cd_uF=cd*1e6,Lfeed_nH=lf*1e9,
                initial_V=initial,Cbus_uF=cb*1e6 if on else None,
                input_peak_V=float(z[1].max()),VAC1_peak_V=float(z[5].max()),
                VAC1_min_V=float(z[5].min()),VBUS_peak_V=float(z[7].max()) if on else None,
                R12_peak_W=float(p.max()),R12_energy_mJ=float(er*1000),
                R12_equal_peak_energy_width_us=float(er/p.max()*1e6),
                energy_residual_fraction=relative,samples=samples)
rows=[]
# Deliberately bounded sensitivity points, not measured or approved cable limits.
for lc,rs in [(.2,.05),(1,.05),(1,.2),(3,.2),(3,.5),(10,.05),(10,.5)]:
    for cd,lf in itertools.product([1.226046,2.2],[50,150]):
        rows.append(run(lc,rs,cd,lf,'fet_off'))
        rows.append(run(lc,rs,cd,lf,'fet_on_reinsert',initial=20))
for mode in ['fet_on_discharged','abrupt_fet_enable']:
    for lc,rs,cb in [(1,.05,10),(1,.2,20),(3,.2,20)]:
        rows.append(run(lc,rs,1.226046,150,mode,cb=cb))
# Independent time-grid refinement of maximum VAC and resistor stresses.
worst=max(rows,key=lambda x:x['VAC1_peak_V'])
refined=run(worst['Lc_uH'],worst['Rs_ohm'],worst['Cd_uF'],worst['Lfeed_nH'],
            worst['mode'],worst['initial_V'],worst['Cbus_uF'] or 20,samples=160001)
assert abs(worst['VAC1_peak_V']-refined['VAC1_peak_V'])<.02
out=dict(description=__doc__,assumptions=dict(Vs_V=VS,Ca_nF=1,C9_uF=.1,Lsnubber_nH=20,
         Rsnubber_ohm=1.9,Rfeed_ohm=.02,Rfet_plus_cap_ESR_ohm=.02,Lfet_nH=20),
         limitations='No nonlinear C(V), source control, FET driver/diode/OVP dynamics, bounce switching or extraction of actual PCB parasitics. Fresh-on discharged is a stress sensitivity, not established reinsertion behavior. No hardware safety proof.',
         cases=rows,refined_worst=refined)
(E/'safety-hotplug-model.json').write_text(json.dumps(out,indent=2)+'\n')
for mode in sorted(set(x['mode'] for x in rows)):
    r=[x for x in rows if x['mode']==mode]
    print(mode,len(r),'VAC range',round(min(x['VAC1_peak_V'] for x in r),3),round(max(x['VAC1_peak_V'] for x in r),3),
          'R max W/mJ',round(max(x['R12_peak_W'] for x in r),2),round(max(x['R12_energy_mJ'] for x in r),4))
