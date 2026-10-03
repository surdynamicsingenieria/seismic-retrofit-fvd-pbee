"""SPEAR-M0 EFCP STRATAN-FAJFAR variant: source-traceable modal reconstruction.

This variant preserves spear_m0_efcp.py and changes only the analytical storey
elevations to 2.75 + 3.00 + 3.00 m, as reported in the Stratan/Fajfar EFCP
idealisation. It is a diagnostic source variant, not a calibrated model.

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
Z_LEVELS=[0.0,2.75,5.75,8.75]

def rect_props(b,h):
    A=b*h
    Iy=b*h**3/12.0
    Iz=h*b**3/12.0
    # Saint-Venant approximation, adequate here only for elastic diagnostic.
    aa=max(b,h); bb=min(b,h)
    J=aa*bb**3*(1/3-0.21*(bb/aa)*(1-bb**4/(12*aa**4)))
    return A,Iy,Iz,J

def build_spear_m0_efcp_stratan_fajfar():
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    # Expected concrete strength used by the pre-test best-estimate model: 37.5 MPa.
    # For this modal diagnostic use EC2 secant modulus from fcm=fc+8 MPa.
    fc=37.5e6
    fcm=fc+8.0e6
    E=22.0e9*(fcm/10.0e6)**0.3
    nu=0.20; G=E/(2*(1+nu))
    # transformations: column local x vertical; beam local x horizontal
    ops.geomTransf("Linear",1,1,0,0)
    ops.geomTransf("Linear",2,0,0,1)
    # Geometric rigid-end offsets for beams are represented with member-specific
    # transformations below because C6 is rectangular and beams are skewed.

    names=list(PLAN)
    idx={n:i+1 for i,n in enumerate(names)}
    def ntag(level,name): return level*100+idx[name]

    # base + three elevated levels
    for lev in range(4):
        z=Z_LEVELS[lev]
        for name,(x,y) in PLAN.items():
            ops.node(ntag(lev,name),x,y,z)
            if lev==0: ops.fix(ntag(lev,name),1,1,1,1,1,1)

    # Columns: C6 = 0.25 x 0.75 with strong bending direction Y.
    # Local section orientation is explicitly represented through Iy/Iz assignment.
    tag=1
    for lev in range(1,4):
        for name in names:
            # Modal tangent section: gross RC section with explicit longitudinal steel.
            # Force-based distributed-plasticity element, 5-point Lobatto, matching EFCP formulation.
            if name=="C6":
                b,h,nbar=0.75,0.25,10
            else:
                b,h,nbar=0.25,0.25,4
            A,Iy,Iz,J=rect_props(b,h)
            sec=5000+tag
            ops.section("Elastic",sec,E,A,Iz,Iy,G,J)
            integ=6000+tag
            ops.beamIntegration("Lobatto",integ,sec,5)
            ops.element("forceBeamColumn",tag,ntag(lev-1,name),ntag(lev,name),1,integ)
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
            if (a=="C6" or b=="C6"):
                xa,ya=PLAN[a]; xb,yb=PLAN[b]
                L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
                da=col_half_extent(a,ux,uy) if a=="C6" else 0.0
                db=col_half_extent(b,ux,uy) if b=="C6" else 0.0
                transf=2000+tag
                ops.geomTransf("Linear",transf,0,0,1,"-jntOffset",ux*da,uy*da,0,-ux*db,-uy*db,0)
            elif False:
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
        ops.node(master,mx,my,Z_LEVELS[lev])
        ops.fix(master,0,0,1,1,1,0)
        ops.mass(master,MASSES[lev-1],MASSES[lev-1],0,0,0,POLAR[lev-1])
        ops.rigidDiaphragm(3,master,*[ntag(lev,n) for n in names])
    return True

def run_modal_efcp_stratan_fajfar(n_modes=6):
    build_spear_m0_efcp_stratan_fajfar()
    vals=ops.eigen("-fullGenLapack",n_modes)
    return [2*math.pi/math.sqrt(v) for v in vals]

if __name__=="__main__":
    ps=run_modal_efcp_stratan_fajfar()
    print("EFCP STRATAN-FAJFAR / H1=2.75 m / FORCE-BASED 5-LOBATTO")
    targets=(0.559,0.476,0.385,0.195,0.159,0.130)
    for i,t in enumerate(ps,1):
        e=100*(t-targets[i-1])/targets[i-1]
        print(f"EFCP_SF Mode {i}: T={t:.6f} s; target={targets[i-1]:.3f} s; error={e:+.2f}%")
    print("STATUS: STRATAN-FAJFAR HEIGHT VARIANT; SOURCE-BASED DIAGNOSTIC, NOT YET PUSHOVER MODEL")
    ops.wipe()
