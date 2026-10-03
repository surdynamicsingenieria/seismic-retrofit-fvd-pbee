"""SPEAR nonlinear intermediate: EFCP fibre columns + frozen elastic beam formulation.

Purpose: isolate column nonlinear response and establish a stable pushover baseline before
adding beam end nonlinearities. This is NOT the final EFCP reproduction.
"""
import math,csv,sys
from pathlib import Path
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as src
import spear_m0_nonlinear_efcp_cp as cp

PLAN=src.PLAN; BEAMS=src.BEAMS; MASSES=src.MASSES; POLAR=src.POLAR; CM=src.CM; Z=src.Z
GACC=src.GACC

def build():
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=37.5e6
    ops.uniaxialMaterial("Concrete01",100,-fc,-0.002,-0.2*fc,-0.0037)
    ops.uniaxialMaterial("Steel02",101,352e6,200e9,0.005,18,0.925,0.15)
    names=list(PLAN); idx={n:i+1 for i,n in enumerate(names)}
    def nt(l,n): return l*100+idx[n]
    for l in range(4):
        for n,(x,y) in PLAN.items():
            ops.node(nt(l,n),x,y,Z[l])
            if l==0: ops.fix(nt(l,n),1,1,1,1,1,1)
    masters=[]
    for l in range(1,4):
        mx,my=CM[l-1]; m=900+l; masters.append(m)
        ops.node(m,mx,my,Z[l]); ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,MASSES[l-1],MASSES[l-1],0,0,0,POLAR[l-1])
        ops.rigidDiaphragm(3,m,*[nt(l,n) for n in names])

    ops.geomTransf("Linear",1,1,0,0)
    cp.build_col_section(201,False); cp.build_col_section(202,True)
    ops.beamIntegration("Lobatto",301,201,5); ops.beamIntegration("Lobatto",302,202,5)
    tag=1; cols=[]
    for l in range(1,4):
        for n in names:
            ops.element("forceBeamColumn",tag,nt(l-1,n),nt(l,n),1,302 if n=="C6" else 301,
                        "-iter",30,1e-10)
            cols.append(tag); tag+=1

    E=22e9*((fc+8e6)/10e6)**0.3; G=E/(2*1.2); A,Iy,Iz,J=src.rect_props(0.25,0.50)
    tr=1000; beams=[]
    for l in range(1,4):
        for bname,a,b in BEAMS:
            xa,ya=PLAN[a]; xb,yb=PLAN[b]
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            di=src.c6_half_extent(ux,uy) if a=="C6" else 0
            dj=src.c6_half_extent(ux,uy) if b=="C6" else 0
            tr+=1
            ops.geomTransf("Linear",tr,0,0,1,"-jntOffset",ux*di,uy*di,0,-ux*dj,-uy*dj,0)
            ops.element("elasticBeamColumn",tag,nt(l,a),nt(l,b),A,E,G,J,Iy,Iz,tr)
            beams.append(tag); tag+=1

    ops.timeSeries("Linear",1); ops.pattern("Plain",1,1)
    for l in range(1,4):
        q=MASSES[l-1]*GACC/len(names)
        for n in names: ops.load(nt(l,n),0,0,-q,0,0,0)
    return {"masters":masters,"bases":[nt(0,n) for n in names],"columns":cols,"beams":beams}

def periods(n=6):
    vals=ops.eigen("-fullGenLapack",n); return [2*math.pi/math.sqrt(v) for v in vals]

def gravity():
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-9,80,0); ops.algorithm("Newton")
    ops.integrator("LoadControl",0.05); ops.analysis("Static")
    ok=ops.analyze(20)
    if ok:
        ops.algorithm("NewtonLineSearch"); ops.test("NormDispIncr",1e-7,200,0)
        ok=ops.analyze(20)
    if ok: raise RuntimeError("gravity failed")
    ops.loadConst("-time",0)

def push(target=0.20,du=0.001,out=None):
    info=build()
    p0=periods(); print("COLNL periods_before_gravity:",",".join(f"{x:.6f}" for x in p0))
    gravity(); pg=periods(); print("COLNL periods_after_gravity:",",".join(f"{x:.6f}" for x in pg))
    phi=[ops.nodeEigenvector(n,1,1) for n in info["masters"]]
    if phi[-1]<0: phi=[-x for x in phi]
    f=[m*x for m,x in zip(MASSES,phi)]; s=sum(f); f=[x/s for x in f]
    print("COLNL_PUSHX modal_floor_fractions:",",".join(f"{x:.6f}" for x in f))
    ops.timeSeries("Linear",10); ops.pattern("Plain",10,10)
    for n,a in zip(info["masters"],f): ops.load(n,1e6*a,0,0,0,0,0)
    ops.wipeAnalysis(); ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-7,100,0); ops.algorithm("Newton")
    ops.integrator("DisplacementControl",info["masters"][-1],1,du); ops.analysis("Static")
    rows=[]; peak=0
    for step in range(1,int(target/du)+10):
        ok=ops.analyze(1)
        if ok:
            solved=False
            for alg in (("NewtonLineSearch",),("KrylovNewton",),("ModifiedNewton","-initial")):
                try:
                    ops.algorithm(*alg); ops.test("NormDispIncr",1e-6,200,0)
                    ops.integrator("DisplacementControl",info["masters"][-1],1,du/2)
                    if ops.analyze(1)==0: solved=True; break
                except: pass
            ops.algorithm("Newton"); ops.test("NormDispIncr",1e-7,100,0)
            ops.integrator("DisplacementControl",info["masters"][-1],1,du)
            if not solved:
                print("COLNL_PUSHX NONCONVERGENCE",step); break
        roof=ops.nodeDisp(info["masters"][-1],1); ops.reactions()
        V=-sum(ops.nodeReaction(n,1) for n in info["bases"])
        rows.append((step,roof,V)); peak=max(peak,V)
        if step==1 or step%10==0: print(f"COLNL_PUSHX step={step}, roof={roof:.6f}, Vbase={V/1e3:.3f} kN")
        if roof>=target-1e-9: break
        if peak>0 and roof>0.08 and V<0.6*peak:
            print("COLNL_PUSHX stop strength<60%peak"); break
    if out:
        p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("w",newline="") as fh:
            w=csv.writer(fh); w.writerow(["step","roof_m","base_shear_N"]); w.writerows(rows)
    if rows:
        pk=max(rows,key=lambda x:x[2])
        print(f"COLNL_PUSHX SUMMARY steps={len(rows)} roof_end={rows[-1][1]:.6f} "
              f"Vpeak={pk[2]/1e3:.3f}kN roof_peak={pk[1]:.6f}")
    return rows

if __name__=="__main__":
    push(out=sys.argv[1] if len(sys.argv)>1 else None); ops.wipe()
