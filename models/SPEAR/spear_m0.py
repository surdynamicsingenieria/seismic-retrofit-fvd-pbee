"""SPEAR-M0 v1.0: first source-locked 3D elastic diagnostic model.

Purpose: verify geometry, axes, masses, torsional coupling and obtain a first
modal diagnostic. This is NOT yet the nonlinear EFCP validation model.
Units: N, m, kg, s.

Plan coordinates are reconstructed from published SPEAR plans. Origin C8.
C5-C1-C2 top line; C9-C3-C4 intermediate; C8-C6-C7 bottom.
The right frame offsets reproduce the published 5.5/5.0 m versus 6.0/4.0 m
vertical dimensions and 3/5/6 m horizontal spans.
"""
import csv, math
from pathlib import Path
import openseespy.opensees as ops

EFCP_TARGETS=(0.559,0.476,0.385)
ETCP_REFERENCES=(0.570,0.484,0.392)

# Published/reconstructed column centreline coordinates, origin at C8.
PLAN={
 "C8":(0.0,0.0), "C6":(3.0,0.0), "C7":(9.0,0.0),
 "C9":(0.0,5.0), "C3":(3.0,5.0), "C4":(9.0,4.0),
 "C5":(0.0,10.5),"C1":(3.0,10.5),"C2":(8.0,10.0),
}
BEAMS=[
 ("B1","C5","C1"),("B2","C1","C2"),("B3","C9","C3"),
 ("B4","C3","C4"),("B5","C8","C6"),("B6","C6","C7"),
 ("B7","C4","C7"),("B8","C2","C4"),("B9","C1","C3"),
 ("B10","C3","C6"),("B11","C5","C9"),("B12","C9","C8"),
]
MASSES=[65.5e3,65.5e3,64.1e3]
POLAR=[1254e3,1254e3,1196e3]
CM=[(4.53,5.29),(4.53,5.29),(4.57,5.33)]
H=3.0

def rect_props(b,h):
    A=b*h
    Iy=b*h**3/12.0
    Iz=h*b**3/12.0
    # Saint-Venant approximation, adequate here only for elastic diagnostic.
    aa=max(b,h); bb=min(b,h)
    J=aa*bb**3*(1/3-0.21*(bb/aa)*(1-bb**4/(12*aa**4)))
    return A,Iy,Iz,J

def build_spear_m0_elastic(rigid_offsets=False, efcp_pretest=False, c6_rigid_arms=False):
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    # Expected concrete strength used by the pre-test best-estimate model: 37.5 MPa.
    # For this modal diagnostic use EC2 secant modulus from fcm=fc+8 MPa.
    fc=37.5e6 if efcp_pretest else 25.0e6
    fcm=fc+8.0e6
    E=22.0e9*(fcm/10.0e6)**0.3 if efcp_pretest else 30.0e9
    nu=0.20; G=E/(2*(1+nu))
    # transformations: column local x vertical; beam local x horizontal
    if rigid_offsets:
        # Sensitivity only: joint-end offsets approximate finite joint dimensions.
        # Columns: +/-0.25 m vertically (half of nominal 0.50 m beam depth).
        # Beams: +/-0.125 m along member axes (half of nominal 0.25 m column width).
        # C6-specific larger in-plane offset is intentionally NOT introduced here:
        # this run isolates the generic rigid-joint effect.
        ops.geomTransf("Linear",1,1,0,0,"-jntOffset",0,0,0.25,0,0,-0.25)
    else:
        ops.geomTransf("Linear",1,1,0,0)
    ops.geomTransf("Linear",2,0,0,1)
    # Geometric rigid-end offsets for beams are represented with member-specific
    # transformations below because C6 is rectangular and beams are skewed.

    names=list(PLAN)
    idx={n:i+1 for i,n in enumerate(names)}
    def ntag(level,name): return level*100+idx[name]

    # base + three elevated levels
    for lev in range(4):
        z=lev*H
        for name,(x,y) in PLAN.items():
            ops.node(ntag(lev,name),x,y,z)
            if lev==0: ops.fix(ntag(lev,name),1,1,1,1,1,1)

    # Columns: C6 = 0.25 x 0.75 with strong bending direction Y.
    # Local section orientation is explicitly represented through Iy/Iz assignment.
    tag=1
    for lev in range(1,4):
        for name in names:
            if name=="C6":
                # local y aligned global X by transf 1; local z then global Y
                # choose dimensions so stiffness is larger for global-Y bending.
                A,Iy,Iz,J=rect_props(0.75,0.25)
            else:
                A,Iy,Iz,J=rect_props(0.25,0.25)
            ops.element("elasticBeamColumn",tag,ntag(lev-1,name),ntag(lev,name),
                        A,E,G,J,Iy,Iz,1)
            tag+=1

    # Beams: 0.25 x 0.50 m. With rigid_offsets=True, each end offset is
    # derived from the actual column footprint projected along the beam axis.
    # Square columns: 0.125 m. C6 footprint: 0.75 m in X and 0.25 m in Y
    # (consistent with its strong bending axis in global Y).
    Ab,Iyb,Izb,Jb=rect_props(0.25,0.50)
    def col_half_extent(name, ux, uy):
        if name != "C6":
            return 0.125
        # distance from centre of an axis-aligned 0.75(X) x 0.25(Y)
        # rectangle to its boundary along beam direction u
        return 1.0/(abs(ux)/0.375 + abs(uy)/0.125)

    for lev in range(1,4):
        for _,a,b in BEAMS:
            transf=2
            if c6_rigid_arms and (a=="C6" or b=="C6"):
                xa,ya=PLAN[a]; xb,yb=PLAN[b]
                L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
                da=col_half_extent(a,ux,uy) if a=="C6" else 0.0
                db=col_half_extent(b,ux,uy) if b=="C6" else 0.0
                transf=2000+tag
                ops.geomTransf("Linear",transf,0,0,1,"-jntOffset",ux*da,uy*da,0,-ux*db,-uy*db,0)
            elif rigid_offsets:
                xa,ya=PLAN[a]; xb,yb=PLAN[b]
                L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
                da=col_half_extent(a,ux,uy); db=col_half_extent(b,ux,uy)
                # jntOffset is global XYZ from node to deformable member end.
                transf=1000+tag
                ops.geomTransf("Linear",transf,0,0,1,"-jntOffset",
                              ux*da,uy*da,0,-ux*db,-uy*db,0)
            ops.element("elasticBeamColumn",tag,ntag(lev,a),ntag(lev,b),
                        Ab,E,G,Jb,Iyb,Izb,transf)
            tag+=1

    # Published rigid-diaphragm masses at CM.
    for lev in range(1,4):
        mx,my=CM[lev-1]
        master=900+lev
        ops.node(master,mx,my,lev*H)
        ops.fix(master,0,0,1,1,1,0)
        ops.mass(master,MASSES[lev-1],MASSES[lev-1],0,0,0,POLAR[lev-1])
        ops.rigidDiaphragm(3,master,*[ntag(lev,n) for n in names])
    return True

def run_modal(n_modes=6, rigid_offsets=False, efcp_pretest=False, c6_rigid_arms=False):
    build_spear_m0_elastic(rigid_offsets=rigid_offsets, efcp_pretest=efcp_pretest, c6_rigid_arms=c6_rigid_arms)
    vals=ops.eigen("-fullGenLapack",n_modes)
    periods=[2*math.pi/math.sqrt(v) for v in vals]
    return periods

def write_results(periods,path="results/modal_results.csv"):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["mode","period_s","efcp_target_s","error_pct","status"])
        for i,t in enumerate(periods,1):
            target=EFCP_TARGETS[i-1] if i<=3 else ""
            err=100*(t-target)/target if i<=3 else ""
            w.writerow([i,f"{t:.8f}",target,f"{err:.3f}" if i<=3 else "","DIAGNOSTIC_NOT_VALIDATED"])

if __name__=="__main__":
    ps=run_modal(rigid_offsets=False); write_results(ps)
    ps_off=run_modal(rigid_offsets=True)
    ps_efcp=run_modal(rigid_offsets=False,efcp_pretest=True)
    ps_c6=run_modal(rigid_offsets=False,efcp_pretest=True,c6_rigid_arms=True)
    print("BASELINE / GENERIC JOINT-OFFSET SENSITIVITY")
    for i,t in enumerate(ps,1):
        if i<=3:
            e=100*(t-EFCP_TARGETS[i-1])/EFCP_TARGETS[i-1]
            print(f"Mode {i}: T={t:.6f} s; EFCP={EFCP_TARGETS[i-1]:.3f} s; error={e:+.2f}%")
        else: print(f"Mode {i}: T={t:.6f} s")
    print("WITH GEOMETRIC RIGID-END OFFSETS (beam depth + actual column footprints):")
    for i,t in enumerate(ps_off,1):
        if i<=3:
            e=100*(t-EFCP_TARGETS[i-1])/EFCP_TARGETS[i-1]
            delta=100*(t-ps[i-1])/ps[i-1]
            print(f"Mode {i}: T={t:.6f} s; EFCP={EFCP_TARGETS[i-1]:.3f} s; error={e:+.2f}%; vs baseline={delta:+.2f}%")
        else:
            delta=100*(t-ps[i-1])/ps[i-1]
            print(f"Mode {i}: T={t:.6f} s; vs baseline={delta:+.2f}%")
    print("EFCP PRE-TEST MATERIAL / CENTRELINE DIAGNOSTIC (no general rigid offsets):")
    for i,t in enumerate(ps_efcp,1):
        if i<=3:
            e=100*(t-EFCP_TARGETS[i-1])/EFCP_TARGETS[i-1]
            print(f"EFCPdiag Mode {i}: T={t:.6f} s; EFCP={EFCP_TARGETS[i-1]:.3f} s; error={e:+.2f}%")
        else:
            print(f"EFCPdiag Mode {i}: T={t:.6f} s")
    print("EFCP DIAGNOSTIC + C6-ONLY RIGID ARMS:")
    for i,t in enumerate(ps_c6,1):
        if i<=3:
            e=100*(t-EFCP_TARGETS[i-1])/EFCP_TARGETS[i-1]
            delta=100*(t-ps_efcp[i-1])/ps_efcp[i-1]
            print(f"C6diag Mode {i}: T={t:.6f} s; EFCP={EFCP_TARGETS[i-1]:.3f} s; error={e:+.2f}%; vs EFCPdiag={delta:+.2f}%")
        else:
            delta=100*(t-ps_efcp[i-1])/ps_efcp[i-1]
            print(f"C6diag Mode {i}: T={t:.6f} s; vs EFCPdiag={delta:+.2f}%")
    print("STATUS: SENSITIVITY ONLY - SPEAR-M0 NOT VALIDATED")
    ops.wipe()

# rerun marker: EFCP-consistent C6 diagnostic; no cross-model beam assumptions
