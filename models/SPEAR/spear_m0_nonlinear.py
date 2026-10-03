"""SPEAR-M0 nonlinear EFCP-oriented OpenSees model.

Frozen modal geometry:
- published Fajfar plan (C4 x=9.70 m)
- C6 strong dimension in global Y
- 3.00 m analytical storey heights
- rigid diaphragms, published masses/CM

Nonlinear formulation:
- columns: forceBeamColumn, fibre sections, 5-point Lobatto
- concrete: unconfined degrading compression (Concrete02 approximation)
- steel: Steel02 with strain hardening
- beams: elastic interior + concentrated end rotational hinges using published
  Table 4-4 yield/ultimate rotations and moments (B1-B12 mapping)
- shear/torsion elastic
- gravity: floor seismic weight distributed equally to frame joints (reconstructed)
- pushover: modal X pattern from first eigenvector, no P-Delta

This is the first executable nonlinear reconstruction. Source-derived and
reconstructed/assumed inputs are identified below; no modal re-calibration.
"""
import math, json
from pathlib import Path
import openseespy.opensees as ops

OUT=Path("results/SPEAR/pushover")
OUT.mkdir(parents=True,exist_ok=True)

PLAN={
 "C8":(0.0,0.0), "C6":(3.0,0.0), "C7":(9.0,0.0),
 "C9":(0.0,5.0), "C3":(3.0,5.0), "C4":(9.7,4.0),
 "C5":(0.0,10.5),"C1":(3.0,10.5),"C2":(8.0,10.0),
}
# Published beam numbering reconstructed from Fig. 4-5.
BEAMS=[
 ("B1","C5","C1"),("B2","C1","C2"),("B3","C9","C3"),("B4","C3","C4"),
 ("B5","C8","C6"),("B6","C6","C7"),("B7","C1","C3"),("B8","C2","C4"),
 ("B9","C5","C9"),("B10","C3","C6"),("B11","C9","C8"),("B12","C4","C7"),
]
MASSES=[65.5e3,65.5e3,64.1e3]
POLAR=[1254e3,1254e3,1196e3]
CM=[(4.53,5.29),(4.53,5.29),(4.57,5.33)]
Z=[0.0,3.0,6.0,9.0]
GACC=9.81

# Published Table 4-4: theta_y(+,-), theta_u(+,-), My(+,-) [N m]
BH={
"B1": (0.0010,0.0024,0.021,0.014,24.7e3,151.5e3),
"B2": (0.0014,0.0041,0.029,0.018,25.3e3,171.7e3),
"B3": (0.0008,0.0023,0.021,0.018,25.6e3,120.1e3),
"B4": (0.0014,0.0045,0.039,0.041,63.0e3,152.7e3),
"B5": (0.0010,0.0022,0.021,0.022,24.7e3,82.1e3),
"B6": (0.0016,0.0047,0.033,0.025,25.7e3,142.3e3),
"B7": (0.0010,0.0054,0.038,0.020,27.3e3,214.1e3),
"B8": (0.0011,0.0030,0.025,0.025,25.4e3,105.0e3),
"B9": (0.0038,0.0048,0.040,0.024,101.2e3,183.1e3),
"B10":(0.0021,0.0036,0.026,0.013,37.3e3,209.4e3),
"B11":(0.0015,0.0039,0.031,0.034,25.5e3,74.4e3),
"B12":(0.0016,0.0040,0.029,0.020,24.7e3,159.2e3),
}

def rect_props(by,bz):
    A=by*bz
    Iy=by*bz**3/12
    Iz=bz*by**3/12
    aa=max(by,bz); bb=min(by,bz)
    J=aa*bb**3*(1/3-0.21*(bb/aa)*(1-bb**4/(12*aa**4)))
    return A,Iy,Iz,J

def make_fiber_section(sec, by, bz, nbar):
    # local y=global Y, local z=global X for vertical columns.
    conc=100; steel=101
    cover=0.031
    ops.section("Fiber",sec,"-GJ",1.0e7)
    ops.patch("rect",conc,12,12,-by/2,-bz/2,by/2,bz/2)
    As=math.pi*(0.012**2)/4
    if nbar==4:
        ys=[-by/2+cover, by/2-cover]
        zs=[-bz/2+cover, bz/2-cover]
        for y in ys:
            for z in zs: ops.fiber(y,z,As,steel)
    else:
        # 10 bars: five along each long face, consistent with 250x750 section.
        for z in (-bz/2+cover,bz/2-cover):
            for k in range(5):
                y=(-by/2+cover)+(by-2*cover)*k/4
                ops.fiber(y,z,As,steel)

def hinge_mat(tag, ty_pos,ty_neg,tu_pos,tu_neg,my_pos,my_neg):
    # Trilinear approximation: cracking point + yield + near-flat post-yield branch.
    # Positive and negative capacities are asymmetric per Table 4-4.
    ops.uniaxialMaterial("Hysteretic",tag,
        0.30*my_pos,0.30*ty_pos, my_pos,ty_pos,1.03*my_pos,tu_pos,
        -0.30*my_neg,-0.30*ty_neg,-my_neg,-ty_neg,-1.03*my_neg,-tu_neg,
        0.2,0.2,0.0,0.0,0.0)

def build():
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=37.5e6; fy=352e6; Es=200e9
    fcm=fc+8e6; Ec=22e9*(fcm/10e6)**0.3; nu=0.20; G=Ec/(2*(1+nu))
    ops.uniaxialMaterial("Concrete02",100,-fc,-0.002,-0.2*fc,-0.0037,0.1,0.0,0.0)
    ops.uniaxialMaterial("Steel02",101,fy,Es,0.005,18.0,0.925,0.15)

    names=list(PLAN); idx={n:i+1 for i,n in enumerate(names)}
    def nt(l,n): return l*100+idx[n]
    for l in range(4):
        for n,(x,y) in PLAN.items():
            ops.node(nt(l,n),x,y,Z[l])
            if l==0: ops.fix(nt(l,n),1,1,1,1,1,1)

    # Column local z is global X; local y therefore global Y.
    ops.geomTransf("Linear",1,1,0,0)
    make_fiber_section(201,0.25,0.25,4)
    make_fiber_section(202,0.75,0.25,10)
    ops.beamIntegration("Lobatto",301,201,5)
    ops.beamIntegration("Lobatto",302,202,5)
    etag=1
    for l in range(1,4):
        for n in names:
            integ=302 if n=="C6" else 301
            ops.element("forceBeamColumn",etag,nt(l-1,n),nt(l,n),1,integ)
            etag+=1

    # Beam elastic interior + zeroLength end hinges.
    Ab,Iyb,Izb,Jb=rect_props(0.25,0.50)
    stiff=1.0e12
    for k in range(1,6):
        ops.uniaxialMaterial("Elastic",800+k,stiff)
    for l in range(1,4):
        for ib,(bn,a,b) in enumerate(BEAMS,1):
            xa,ya=PLAN[a]; xb,yb=PLAN[b]
            dx=xb-xa; dy=yb-ya; L=math.hypot(dx,dy); ux=dx/L; uy=dy/L
            # duplicate nodes at joints for beam element
            ni=10000+l*1000+ib*2; nj=ni+1
            ops.node(ni,xa,ya,Z[l]); ops.node(nj,xb,yb,Z[l])
            hp=BH[bn]
            mi=20000+l*1000+ib*2; mj=mi+1
            hinge_mat(mi,*hp); hinge_mat(mj,*hp)
            # local x along beam; local y = global Z => local z horizontal transverse.
            # Vertical-plane beam flexure is rotation about local z => dir 6.
            si=30000+l*1000+ib*2; sj=si+1
            mats=[801,802,803,804,805,mi]
            ops.element("zeroLength",si,nt(l,a),ni,"-mat",*mats,"-dir",1,2,3,4,5,6,
                        "-orient",ux,uy,0,0,0,1)
            matsj=[801,802,803,804,805,mj]
            ops.element("zeroLength",sj,nj,nt(l,b),"-mat",*matsj,"-dir",1,2,3,4,5,6,
                        "-orient",ux,uy,0,0,0,1)
            tr=40000+l*1000+ib
            ops.geomTransf("Linear",tr,0,0,1)
            ops.element("elasticBeamColumn",50000+l*1000+ib,ni,nj,Ab,Ec,G,Jb,Iyb,Izb,tr)

    # Rigid diaphragms and published masses.
    masters=[]
    for l in range(1,4):
        mx,my=CM[l-1]; m=900+l
        ops.node(m,mx,my,Z[l]); ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,MASSES[l-1],MASSES[l-1],0,0,0,POLAR[l-1])
        ops.rigidDiaphragm(3,m,*[nt(l,n) for n in names])
        masters.append(m)
    return names,idx,nt,masters,Ec

def gravity(names,nt):
    ops.timeSeries("Linear",10); ops.pattern("Plain",10,10)
    for l in range(1,4):
        W=MASSES[l-1]*GACC
        for n in names: ops.load(nt(l,n),0,0,-W/len(names),0,0,0)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-8,30); ops.algorithm("Newton")
    ops.integrator("LoadControl",0.1); ops.analysis("Static")
    ok=ops.analyze(10)
    if ok!=0: return ok
    ops.loadConst("-time",0.0)
    return 0

def modal_x_pattern(masters):
    vals=ops.eigen("-fullGenLapack",3)
    ph=[ops.nodeEigenvector(m,1,1) for m in masters]
    if sum(MASSES[i]*ph[i] for i in range(3))<0: ph=[-x for x in ph]
    f=[MASSES[i]*ph[i] for i in range(3)]
    s=sum(abs(x) for x in f)
    f=[x/s for x in f]
    return vals,ph,f

def run_pushover_x(target=0.20,du=0.0005):
    names,idx,nt,masters,Ec=build()
    gok=gravity(names,nt)
    if gok!=0:
        print("GRAVITY_FAIL",gok); return 2
    vals,phi,forces=modal_x_pattern(masters)
    T=[2*math.pi/math.sqrt(v) for v in vals]
    ops.timeSeries("Linear",20); ops.pattern("Plain",20,20)
    for m,f in zip(masters,forces): ops.load(m,f,0,0,0,0,0)

    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-7,50); ops.algorithm("Newton")
    ops.integrator("DisplacementControl",masters[-1],1,du)
    ops.analysis("Static")

    rows=[(0.0,0.0)]
    nsteps=int(target/du)
    base_nodes=[nt(0,n) for n in names]
    ok=0
    for step in range(1,nsteps+1):
        ok=ops.analyze(1)
        if ok!=0:
            # convergence recovery
            ops.test("NormDispIncr",1e-6,100)
            ops.algorithm("NewtonLineSearch",0.8)
            ok=ops.analyze(1)
            ops.algorithm("Newton"); ops.test("NormDispIncr",1e-7,50)
        if ok!=0:
            print(f"NONCONVERGENCE step={step} roof={ops.nodeDisp(masters[-1],1):.6f}")
            break
        ops.reactions()
        vb=-sum(ops.nodeReaction(n,1) for n in base_nodes)
        u=ops.nodeDisp(masters[-1],1)
        rows.append((u,vb))
        if step%20==0: print(f"PUSHX step={step} u={u:.5f} Vb={vb/1e3:.2f} kN")

    csv=OUT/"pushover_x.csv"
    csv.write_text("roof_disp_m,base_shear_N\n"+"\n".join(f"{u:.8f},{v:.6f}" for u,v in rows)+"\n")
    peak=max(abs(v) for _,v in rows) if rows else 0
    summary={
      "status":"success" if ok==0 and rows[-1][0]>=target-du*1.5 else "partial",
      "target_m":target,"reached_m":rows[-1][0],"peak_base_shear_kN":peak/1e3,
      "modal_periods_s":T,"modal_shape_x":phi,"modal_pattern":forces,
      "gravity":"G+approx seismic floor weight from published masses, equally distributed to 9 joints",
      "beam_hinges":"Table 4-4 B1-B12; trilinear reconstructed with cracking=0.3My and postyield=1.03My",
      "columns":"fiber Concrete02/Steel02, 5 Lobatto; 4x12 regular, 10x12 C6",
      "warning":"B13/B14 topology not represented in frozen modal topology; nonlinear gate remains provisional until reconciled."
    }
    (OUT/"pushover_x_summary.json").write_text(json.dumps(summary,indent=2))
    print("PUSHOVER_X_SUMMARY",json.dumps(summary))
    ops.wipe()
    return 0 if summary["status"]=="success" else 3

if __name__=="__main__":
    raise SystemExit(run_pushover_x())
