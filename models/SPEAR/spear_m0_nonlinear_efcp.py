"""SPEAR-M0 nonlinear EFCP candidate for pushover validation.

Source basis: Stratan & Fajfar (2003), Seismic Assessment of the SPEAR Test Structure.
This file is kept separate from the frozen modal model.

PUBLISHED:
- PLAN geometry, 3.0 m analytical storey heights, rigid diaphragms and floor masses.
- Expected materials fc=37.5 MPa, fy=352 MPa; unconfined concrete; steel hardening.
- EFCP columns: distributed-plasticity fibre elements, M-M-N interaction.
- Beams: one-component end moment-rotation behaviour; Table 4-4 My/theta_y/theta_u.
- Shear/torsion elastic; no P-Delta in reference analysis.
- Modal translational load pattern for pushover.

RECONSTRUCTED (explicitly, not calibration):
- Steel02 hardening ratio b=0.005 because the report states strain hardening but does not
  tabulate the tangent hardening modulus.
- Concrete02 tension parameters are set to zero-strength surrogate values; monotonic
  compression follows fc=37.5 MPa and eps_u=0.0037 with residual 0.2fc.
- Beam monotonic Hysteretic envelope uses a small pre-yield point at 0.25 theta_y,
  0.40 My, passes exactly through published (theta_y,My), and uses 1.05 My at theta_u.
  For monotonic pushover the cyclic rule/pinching is immaterial.
- Gravity floor weight is initially distributed equally to the nine column joints.
  This is a diagnostic gravity distribution pending exact tributary-line-load reproduction.

Units: N, m, kg, s.
"""
import math, csv, sys
from pathlib import Path
import openseespy.opensees as ops

PLAN={
 "C8":(0.0,0.0), "C6":(3.0,0.0), "C7":(9.0,0.0),
 "C9":(0.0,5.0), "C3":(3.0,5.0), "C4":(9.7,4.0),
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
Z=[0.0,3.0,6.0,9.0]
GACC=9.81

# Table 4-4: theta_y+,- ; theta_u+,- ; My+,- [N m].
BH={
"B1":{"i":(0.0010,0.0022,0.021,0.022,24.7e3,82.1e3),
      "j":(0.0010,0.0024,0.021,0.014,24.7e3,151.5e3)},
"B2":{"i":(0.0014,0.0041,0.029,0.017,25.3e3,187.0e3),
      "j":(0.0014,0.0041,0.029,0.018,25.3e3,171.7e3)},
"B3":{"i":(0.0008,0.0023,0.021,0.018,25.6e3,120.1e3),
      "j":(0.0008,0.0023,0.021,0.018,25.6e3,120.1e3)},
"B4":{"i":(0.0014,0.0056,0.039,0.016,63.0e3,310.5e3),
      "j":(0.0042,0.0045,0.036,0.041,248.2e3,152.7e3)},
"B5":{"i":(0.0010,0.0022,0.021,0.022,24.7e3,82.1e3),
      "j":(0.0010,0.0022,0.021,0.022,24.7e3,82.1e3)},
"B6":{"i":(0.0016,0.0047,0.033,0.025,25.7e3,142.3e3),
      "j":(0.0016,0.0047,0.033,0.025,25.7e3,142.3e3)},
"B7":{"i":(0.0010,0.0059,0.038,0.014,27.3e3,336.6e3),
      "j":(0.0016,0.0054,0.039,0.020,25.6e3,214.1e3)},
"B8":{"i":(0.0011,0.0030,0.025,0.025,25.4e3,105.0e3),
      "j":(0.0011,0.0030,0.025,0.025,25.4e3,105.0e3)},
"B9":{"i":(0.0038,0.0050,0.040,0.027,101.2e3,212.1e3),
      "j":(0.0012,0.0048,0.039,0.024,44.9e3,183.1e3)},
"B10":{"i":(0.0021,0.0030,0.026,0.023,37.3e3,115.6e3),
       "j":(0.0011,0.0036,0.025,0.013,25.3e3,209.4e3)},
"B11":{"i":(0.0015,0.0044,0.031,0.021,25.5e3,159.5e3),
       "j":(0.0018,0.0039,0.031,0.034,24.7e3,74.4e3)},
"B12":{"i":(0.0016,0.0036,0.029,0.032,24.7e3,74.4e3),
       "j":(0.0014,0.0040,0.029,0.020,25.3e3,159.2e3)},
}

def rect_props(b,h):
    A=b*h
    Iy=b*h**3/12.0
    Iz=h*b**3/12.0
    aa=max(b,h); bb=min(b,h)
    J=aa*bb**3*(1/3-0.21*(bb/aa)*(1-bb**4/(12*aa**4)))
    return A,Iy,Iz,J

def c6_half_extent(ux,uy):
    # Published orientation: 0.25 m global X x 0.75 m global Y.
    return 1.0/(abs(ux)/0.125 + abs(uy)/0.375)

def build_column_section(sec, c6=False):
    fc=37.5e6
    fy=352e6
    Es=200e9
    # Published unconfined concrete; residual at eps_u is 0.2fc.
    conc=100
    steel=101
    # Materials are created once by caller.
    if c6:
        by,bz=0.75,0.25  # local y ~= global Y; local z ~= global X
        ny,nz=18,6
    else:
        by,bz=0.25,0.25
        ny,nz=8,8
    A,Iy,Iz,J=rect_props(by,bz)
    G=34.5e9/(2*(1+0.20))
    ops.section("Fiber",sec,"-GJ",G*J)
    ops.patch("rect",conc,ny,nz,-by/2,-bz/2,by/2,bz/2)
    db=0.012
    Ab=math.pi*db*db/4
    cover=0.025
    yy=by/2-cover
    zz=bz/2-cover
    if not c6:
        for y in (-yy,yy):
            for z in (-zz,zz):
                ops.fiber(y,z,Ab,steel)
    else:
        pts=[(-yy,-zz),(-yy,zz),(yy,-zz),(yy,zz),
             (-yy/3,-zz),(yy/3,-zz),(-yy/3,zz),(yy/3,zz),
             (0,-zz),(0,zz)]
        # Keep exactly 10 bars; duplicate middle-face positions avoided below.
        pts=[(-yy,-zz),(-yy,zz),(yy,-zz),(yy,zz),
             (-yy/3,-zz),(yy/3,-zz),(-yy/3,zz),(yy/3,zz),
             (0,-zz),(0,zz)]
        for y,z in pts:
            ops.fiber(y,z,Ab,steel)
    return A,Iy,Iz,J

def make_hysteretic(mat, data):
    typ,tyn,tup,tun,Myp,Myn=data
    # RECONSTRUCTED pre-yield/cracking point; published yield/ultimate points exact.
    p1=(0.40*Myp,0.25*typ)
    p2=(Myp,typ)
    p3=(1.05*Myp,tup)
    n1=(-0.40*Myn,-0.25*tyn)
    n2=(-Myn,-tyn)
    n3=(-1.05*Myn,-tun)
    ops.uniaxialMaterial("Hysteretic",mat,
        p1[0],p1[1],p2[0],p2[1],p3[0],p3[1],
        n1[0],n1[1],n2[0],n2[1],n3[0],n3[1],
        1.0,1.0,0.0,0.0,0.0)

def build_model():
    ops.wipe()
    ops.model("basic","-ndm",3,"-ndf",6)

    fc=37.5e6
    fy=352e6
    Es=200e9
    # Concrete compression: peak strain reconstructed as 0.002; published eps_u=0.0037 at 0.2fc.
    ops.uniaxialMaterial("Concrete01",100,-fc,-0.002,-0.2*fc,-0.0037)
    ops.uniaxialMaterial("Steel02",101,fy,Es,0.005,18.0,0.925,0.15)
    # Near-rigid spring materials for zeroLength beam hinges.
    ops.uniaxialMaterial("Elastic",110,1.0e12)
    ops.uniaxialMaterial("Elastic",111,1.0e12)

    names=list(PLAN)
    idx={n:i+1 for i,n in enumerate(names)}
    def ntag(lev,name): return lev*100+idx[name]

    for lev in range(4):
        for name,(x,y) in PLAN.items():
            ops.node(ntag(lev,name),x,y,Z[lev])
            if lev==0:
                ops.fix(ntag(lev,name),1,1,1,1,1,1)

    # masters + rigid diaphragms
    masters=[]
    for lev in range(1,4):
        mx,my=CM[lev-1]
        m=900+lev
        masters.append(m)
        ops.node(m,mx,my,Z[lev])
        ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,MASSES[lev-1],MASSES[lev-1],0,0,0,POLAR[lev-1])
        ops.rigidDiaphragm(3,m,*[ntag(lev,n) for n in names])

    # Column local x = global Z. vecxz global X -> local y ~= global Y, local z ~= global X.
    ops.geomTransf("Linear",1,1,0,0)
    sec_sq=201; sec_c6=202
    build_column_section(sec_sq,False)
    build_column_section(sec_c6,True)
    ops.beamIntegration("Lobatto",301,sec_sq,5)
    ops.beamIntegration("Lobatto",302,sec_c6,5)

    etag=1
    col_tags=[]
    for lev in range(1,4):
        for name in names:
            integ=302 if name=="C6" else 301
            ops.element("forceBeamColumn",etag,ntag(lev-1,name),ntag(lev,name),1,integ)
            col_tags.append(etag); etag+=1

    # Beam elastic interior properties as published 250x500 web; hinges carry nonlinear flexure.
    E=22.0e9*((37.5e6+8e6)/10e6)**0.3
    nu=0.20; G=E/(2*(1+nu))
    Ab,Iyb,Izb,Jb=rect_props(0.25,0.50)
    beam_tags=[]; hinge_tags=[]; auxnode=10000; mate=1000; trans=1000

    for lev in range(1,4):
        for bname,a,b in BEAMS:
            xa,ya=PLAN[a]; xb,yb=PLAN[b]
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            # Main or rigid-face nodes at each end.
            ends=[]
            for end,name,sgn in (("i",a,+1),("j",b,-1)):
                main=ntag(lev,name)
                if name=="C6":
                    d=c6_half_extent(ux,uy)
                    x=PLAN[name][0] + sgn*ux*d
                    y=PLAN[name][1] + sgn*uy*d
                    face=auxnode; auxnode+=1
                    ops.node(face,x,y,Z[lev])
                    ops.rigidLink("beam",main,face)
                else:
                    face=main
                    x,y=PLAN[name]
                dup=auxnode; auxnode+=1
                ops.node(dup,x,y,Z[lev])
                hm=mate; mate+=1
                make_hysteretic(hm,BH[bname][end])
                # local x along beam, local y vertical; bending hinge is local z (dir 6).
                ops.element("zeroLength",etag,face,dup,
                    "-mat",110,110,110,111,111,hm,
                    "-dir",1,2,3,4,5,6,
                    "-orient",ux,uy,0.0,0.0,0.0,1.0)
                hinge_tags.append(etag); etag+=1
                ends.append(dup)

            trans+=1
            ops.geomTransf("Linear",trans,0,0,1)
            ops.element("elasticBeamColumn",etag,ends[0],ends[1],
                        Ab,E,G,Jb,Iyb,Izb,trans)
            beam_tags.append(etag); etag+=1

    # Gravity: diagnostic distribution of seismic floor weights to column joints.
    ops.timeSeries("Linear",1)
    ops.pattern("Plain",1,1)
    for lev in range(1,4):
        W=MASSES[lev-1]*GACC
        q=W/len(names)
        for n in names:
            ops.load(ntag(lev,n),0,0,-q,0,0,0)

    return {"masters":masters,"bases":[ntag(0,n) for n in names],
            "columns":col_tags,"beams":beam_tags,"hinges":hinge_tags}

def run_gravity():
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr",1e-8,50,0)
    ops.algorithm("Newton")
    ops.integrator("LoadControl",0.1)
    ops.analysis("Static")
    ok=ops.analyze(10)
    if ok!=0:
        ops.algorithm("ModifiedNewton","-initial")
        ok=ops.analyze(10)
    if ok!=0:
        raise RuntimeError("gravity analysis failed")
    ops.loadConst("-time",0.0)

def modal_periods(n=6):
    vals=ops.eigen("-fullGenLapack",n)
    return [2*math.pi/math.sqrt(v) for v in vals]

def pushover_x(target=0.20,du=0.001,csv_path=None):
    info=build_model()
    run_gravity()
    periods=modal_periods(6)
    print("NL_EFCP initial periods:",",".join(f"{x:.6f}" for x in periods))

    masters=info["masters"]
    phi=[ops.nodeEigenvector(n,1,1) for n in masters]
    if phi[-1] < 0: phi=[-x for x in phi]
    modal=[m*p for m,p in zip(MASSES,phi)]
    sm=sum(modal)
    modal=[x/sm for x in modal]
    print("PUSHX modal floor fractions:",",".join(f"{x:.6f}" for x in modal))

    ops.timeSeries("Linear",10)
    ops.pattern("Plain",10,10)
    # 1 MN reference total lateral pattern; load factor scales it.
    for n,f in zip(masters,modal):
        ops.load(n,1.0e6*f,0,0,0,0,0)

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr",1e-7,60,0)
    ops.algorithm("Newton")
    ops.integrator("DisplacementControl",masters[-1],1,du)
    ops.analysis("Static")

    rows=[]
    peak=0.0
    nstep=int(target/du)+5
    for step in range(1,nstep+1):
        ok=ops.analyze(1)
        if ok!=0:
            solved=False
            for alg in (("NewtonLineSearch",),("ModifiedNewton","-initial"),("KrylovNewton",)):
                try:
                    ops.algorithm(*alg)
                    ops.test("NormDispIncr",1e-6,120,0)
                    ops.integrator("DisplacementControl",masters[-1],1,du/2)
                    if ops.analyze(1)==0:
                        solved=True
                        break
                except Exception:
                    pass
            ops.algorithm("Newton")
            ops.test("NormDispIncr",1e-7,60,0)
            ops.integrator("DisplacementControl",masters[-1],1,du)
            if not solved:
                print(f"PUSHX NONCONVERGENCE step={step}")
                break
        roof=ops.nodeDisp(masters[-1],1)
        ops.reactions()
        V=-sum(ops.nodeReaction(n,1) for n in info["bases"])
        peak=max(peak,V)
        rows.append((step,roof,V))
        if step%10==0 or step==1:
            print(f"PUSHX step={step}, roof={roof:.6f}, Vbase={V/1e3:.3f} kN")
        if roof>=target-1e-9:
            break
        if peak>0 and roof>0.08 and V<0.65*peak:
            print("PUSHX stop: strength dropped below 65% of peak")
            break

    if csv_path:
        p=Path(csv_path); p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("w",newline="") as f:
            w=csv.writer(f); w.writerow(["step","roof_m","base_shear_N"]); w.writerows(rows)
    if rows:
        pk=max(rows,key=lambda r:r[2])
        print(f"PUSHX SUMMARY: steps={len(rows)}; roof_end={rows[-1][1]:.6f} m; "
              f"Vpeak={pk[2]/1e3:.3f} kN at roof={pk[1]:.6f} m")
    return periods,rows

if __name__=="__main__":
    out=sys.argv[1] if len(sys.argv)>1 else None
    pushover_x(csv_path=out)
    ops.wipe()
