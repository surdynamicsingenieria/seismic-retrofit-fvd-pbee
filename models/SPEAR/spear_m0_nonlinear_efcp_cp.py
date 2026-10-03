"""SPEAR-M0 nonlinear EFCP candidate v2: forceBeamColumn + ConcentratedPlasticity beams.

The frozen modal candidate remains unchanged. This nonlinear model uses:
- distributed-plasticity fibre columns (5 Lobatto points);
- force-based beam-columns with OpenSees ConcentratedPlasticity integration;
- elastic beam interior + finite plastic rotations at member ends;
- published Stratan-Fajfar beam My, theta_y, theta_u values;
- source-consistent C6 finite-dimension offsets;
- no P-Delta, consistent with the reference analysis.

The ConcentratedPlasticity integration expects PLASTIC rotation at beam ends. Therefore
published theta_y is not inserted as an elastic zeroLength spring deformation. Elastic
deformation is carried by the elastic beam section; available post-yield rotation is
reconstructed as theta_pu = theta_u - theta_y. This avoids double-counting member
elastic flexibility.

RECONSTRUCTED, NOT CALIBRATED:
- steel hardening ratio b=0.005;
- concrete peak strain eps_c0=0.002;
- beam post-yield strength at theta_u = 1.05 My (ultimate moment not tabulated);
- plastic section uses a numerically near-rigid pre-yield branch;
- gravity is temporarily distributed equally to column joints pending exact tributary load map.
"""
import math,csv,sys
from pathlib import Path
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as src

PLAN=src.PLAN; BEAMS=src.BEAMS; MASSES=src.MASSES; POLAR=src.POLAR; CM=src.CM
Z=src.Z; GACC=src.GACC; BH=src.BH
rect_props=src.rect_props
c6_half_extent=src.c6_half_extent

def build_col_section(sec,c6=False):
    fc=37.5e6; fy=352e6; Es=200e9
    if c6:
        by,bz=0.75,0.25; ny,nz=18,6
    else:
        by,bz=0.25,0.25; ny,nz=8,8
    A,Iy,Iz,J=rect_props(by,bz)
    E=22e9*((fc+8e6)/10e6)**0.3; G=E/(2*1.2)
    ops.section("Fiber",sec,"-GJ",G*J)
    ops.patch("rect",100,ny,nz,-by/2,-bz/2,by/2,bz/2)
    Ab=math.pi*0.012**2/4; cover=0.025; yy=by/2-cover; zz=bz/2-cover
    if c6:
        pts=[(-yy,-zz),(-yy,zz),(yy,-zz),(yy,zz),
             (-yy/3,-zz),(yy/3,-zz),(-yy/3,zz),(yy/3,zz),(0,-zz),(0,zz)]
    else:
        pts=[(-yy,-zz),(-yy,zz),(yy,-zz),(yy,zz)]
    for y,z in pts: ops.fiber(y,z,Ab,101)

def plastic_rot_material(tag,data):
    typ,tyn,tup,tun,Myp,Myn=data
    pup=max(tup-typ,1e-5); pun=max(tun-tyn,1e-5)
    # Almost no plastic deformation before My; then 5% hardening to the published rotation capacity.
    epsp=min(1e-6,0.001*pup)
    epsn=min(1e-6,0.001*pun)
    ops.uniaxialMaterial("Hysteretic",tag,
        0.995*Myp,epsp, Myp,2*epsp, 1.05*Myp,pup,
        -0.995*Myn,-epsn, -Myn,-2*epsn, -1.05*Myn,-pun,
        1.0,1.0,0.0,0.0,0.0)

def build_model():
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=37.5e6
    ops.uniaxialMaterial("Concrete01",100,-fc,-0.002,-0.2*fc,-0.0037)
    ops.uniaxialMaterial("Steel02",101,352e6,200e9,0.005,18.0,0.925,0.15)

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

    # columns
    ops.geomTransf("Linear",1,1,0,0)
    build_col_section(201,False); build_col_section(202,True)
    ops.beamIntegration("Lobatto",301,201,5); ops.beamIntegration("Lobatto",302,202,5)
    etag=1; coltags=[]
    for l in range(1,4):
        for n in names:
            ops.element("forceBeamColumn",etag,nt(l-1,n),nt(l,n),1,302 if n=="C6" else 301)
            coltags.append(etag); etag+=1

    # common elastic beam interior section: published 250x500 web.
    E=22e9*((fc+8e6)/10e6)**0.3; G=E/(2*1.2)
    A,Iy,Iz,J=rect_props(0.25,0.50)
    # Elastic section syntax is E,A,Iz,Iy,G,J.
    ops.section("Elastic",400,E,A,Iz,Iy,G,J)

    beamtags=[]; mat=1000; sec=2000; integ=3000; transf=4000
    for l in range(1,4):
        for bname,a,b in BEAMS:
            xa,ya=PLAN[a]; xb,yb=PLAN[b]
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            di=dj=0.0
            if a=="C6": di=c6_half_extent(ux,uy)
            if b=="C6": dj=c6_half_extent(ux,uy)
            transf+=1
            ops.geomTransf("Linear",transf,0,0,1,
                "-jntOffset",ux*di,uy*di,0,-ux*dj,-uy*dj,0)

            mat+=1; plastic_rot_material(mat,BH[bname]["i"])
            sec+=1; secI=sec; ops.section("Uniaxial",secI,mat,"My")
            mat+=1; plastic_rot_material(mat,BH[bname]["j"])
            sec+=1; secJ=sec; ops.section("Uniaxial",secJ,mat,"My")
            integ+=1
            ops.beamIntegration("ConcentratedPlasticity",integ,secI,secJ,400)
            ops.element("forceBeamColumn",etag,nt(l,a),nt(l,b),transf,integ,
                        "-iter",30,1e-10)
            beamtags.append(etag); etag+=1

    # gravity diagnostic
    ops.timeSeries("Linear",1); ops.pattern("Plain",1,1)
    for l in range(1,4):
        q=MASSES[l-1]*GACC/len(names)
        for n in names: ops.load(nt(l,n),0,0,-q,0,0,0)
    return {"masters":masters,"bases":[nt(0,n) for n in names],
            "columns":coltags,"beams":beamtags}

def periods(n=6):
    vals=ops.eigen("-fullGenLapack",n)
    return [2*math.pi/math.sqrt(v) for v in vals]

def gravity():
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-9,60,0); ops.algorithm("Newton")
    ops.integrator("LoadControl",0.1); ops.analysis("Static")
    ok=ops.analyze(10)
    if ok!=0:
        ops.algorithm("NewtonLineSearch"); ops.test("NormDispIncr",1e-7,120,0)
        ok=ops.analyze(10)
    if ok: raise RuntimeError("gravity failed")
    ops.loadConst("-time",0.0)

def push_x(target=0.20,du=0.001,out=None):
    info=build_model()
    p0=periods(); print("CP_EFCP periods_before_gravity:",",".join(f"{x:.6f}" for x in p0))
    gravity()
    pg=periods(); print("CP_EFCP periods_after_gravity:",",".join(f"{x:.6f}" for x in pg))
    phi=[ops.nodeEigenvector(n,1,1) for n in info["masters"]]
    if phi[-1]<0: phi=[-x for x in phi]
    f=[m*x for m,x in zip(MASSES,phi)]; sf=sum(f); f=[x/sf for x in f]
    print("CP_PUSHX modal_floor_fractions:",",".join(f"{x:.6f}" for x in f))
    ops.timeSeries("Linear",10); ops.pattern("Plain",10,10)
    for n,a in zip(info["masters"],f): ops.load(n,1e6*a,0,0,0,0,0)
    ops.wipeAnalysis(); ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-7,80,0); ops.algorithm("Newton")
    ops.integrator("DisplacementControl",info["masters"][-1],1,du); ops.analysis("Static")
    rows=[]; peak=0.0
    for step in range(1,int(target/du)+10):
        ok=ops.analyze(1)
        if ok:
            solved=False
            for alg in (("NewtonLineSearch",),("KrylovNewton",),("ModifiedNewton","-initial")):
                try:
                    ops.algorithm(*alg); ops.test("NormDispIncr",1e-6,160,0)
                    ops.integrator("DisplacementControl",info["masters"][-1],1,du/2)
                    if ops.analyze(1)==0: solved=True; break
                except: pass
            ops.algorithm("Newton"); ops.test("NormDispIncr",1e-7,80,0)
            ops.integrator("DisplacementControl",info["masters"][-1],1,du)
            if not solved:
                print("CP_PUSHX NONCONVERGENCE",step); break
        roof=ops.nodeDisp(info["masters"][-1],1)
        ops.reactions(); V=-sum(ops.nodeReaction(n,1) for n in info["bases"])
        rows.append((step,roof,V)); peak=max(peak,V)
        if step==1 or step%10==0: print(f"CP_PUSHX step={step}, roof={roof:.6f}, Vbase={V/1e3:.3f} kN")
        if roof>=target-1e-9: break
        if peak>0 and roof>0.08 and V<0.60*peak:
            print("CP_PUSHX stop strength<60%peak"); break
    if out:
        path=Path(out); path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",newline="") as fh:
            w=csv.writer(fh); w.writerow(["step","roof_m","base_shear_N"]); w.writerows(rows)
    if rows:
        pk=max(rows,key=lambda x:x[2])
        print(f"CP_PUSHX SUMMARY steps={len(rows)} roof_end={rows[-1][1]:.6f} "
              f"Vpeak={pk[2]/1e3:.3f}kN roof_peak={pk[1]:.6f}")
    return p0,pg,rows

if __name__=="__main__":
    push_x(out=sys.argv[1] if len(sys.argv)>1 else None)
    ops.wipe()
