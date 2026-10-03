"""SPEAR-M0 EFCP end-fibre diagnostic.

Source-consistent variant of spear_m0_nonlinear.py:
the primary Stratan-Fajfar report states that fibre cross-sections are located at
the element ends and curvature varies linearly along the member. Therefore this
variant uses two endpoint Lobatto fibre sections rather than five distributed
integration sections. All materials, geometry, masses, gravity and beam laws are
kept unchanged.

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

OUT=Path("results/SPEAR/pushover_efcp_endfibers")
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
# Reconstructed tributary areas [m2] from the published irregular floor polygon,
# Voronoi-partitioned about column centrelines. Sum = 92.5 m2.
TRIB_AREA={
 "C8":3.7500,"C6":11.2500,"C7":7.3292636364,
 "C9":7.8750,"C3":24.8572168831,"C4":13.4856298701,
 "C5":4.0546875,"C1":9.8129367236,"C2":10.0852653868,
}
TRIB_TOTAL=sum(TRIB_AREA.values())

# Published Table 4-4: end-specific theta_y(+,-), theta_u(+,-), My(+,-)
# [rad, rad, rad, rad, N m, N m]
BH_END={
("B1","i"):(0.0010,0.0022,0.021,0.022,24.7e3,82.1e3),
("B1","j"):(0.0010,0.0024,0.021,0.014,24.7e3,151.5e3),
("B2","i"):(0.0014,0.0041,0.029,0.017,25.3e3,187.0e3),
("B2","j"):(0.0014,0.0041,0.029,0.018,25.3e3,171.7e3),
("B3","i"):(0.0008,0.0023,0.021,0.018,25.6e3,120.1e3),
("B3","j"):(0.0008,0.0023,0.021,0.018,25.6e3,120.1e3),
("B4","i"):(0.0014,0.0056,0.039,0.016,63.0e3,310.5e3),
("B4","j"):(0.0042,0.0045,0.036,0.041,248.2e3,152.7e3),
("B5","i"):(0.0010,0.0022,0.021,0.022,24.7e3,82.1e3),
("B5","j"):(0.0010,0.0022,0.021,0.022,24.7e3,82.1e3),
("B6","i"):(0.0016,0.0047,0.033,0.025,25.7e3,142.3e3),
("B6","j"):(0.0016,0.0047,0.033,0.025,25.7e3,142.3e3),
("B7","i"):(0.0010,0.0059,0.038,0.014,27.3e3,336.6e3),
("B7","j"):(0.0016,0.0054,0.039,0.020,25.6e3,214.1e3),
("B8","i"):(0.0011,0.0030,0.025,0.025,25.4e3,105.0e3),
("B8","j"):(0.0011,0.0030,0.025,0.025,25.4e3,105.0e3),
("B9","i"):(0.0038,0.0050,0.040,0.027,101.2e3,212.1e3),
("B9","j"):(0.0012,0.0048,0.039,0.024,44.9e3,183.1e3),
("B10","i"):(0.0021,0.0030,0.026,0.023,37.3e3,115.6e3),
("B10","j"):(0.0011,0.0036,0.025,0.013,25.3e3,209.4e3),
("B11","i"):(0.0015,0.0044,0.031,0.021,25.5e3,159.5e3),
("B11","j"):(0.0018,0.0039,0.031,0.034,24.7e3,74.4e3),
("B12","i"):(0.0016,0.0036,0.029,0.032,24.7e3,74.4e3),
("B12","j"):(0.0014,0.0040,0.029,0.020,25.3e3,159.2e3),
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
    # Plastic-rotation spring decomposition.
    # The elastic beam carries the member rotation up to yield; this zeroLength
    # spring carries only plastic rotation. Published theta_u-theta_y therefore
    # defines the available plastic-rotation capacity.
    k0=1.0e11
    eyp=my_pos/k0; eyn=my_neg/k0
    pup=max(tu_pos-ty_pos,20*eyp)
    pun=max(tu_neg-ty_neg,20*eyn)
    ops.uniaxialMaterial("Hysteretic",tag,
        0.99*my_pos,0.99*eyp, my_pos,eyp,1.03*my_pos,eyp+pup,
        -0.99*my_neg,-0.99*eyn,-my_neg,-eyn,-1.03*my_neg,-eyn-pun,
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
    ops.beamIntegration("Lobatto",301,201,2)
    ops.beamIntegration("Lobatto",302,202,2)
    etag=1
    for l in range(1,4):
        for n in names:
            integ=302 if n=="C6" else 301
            ops.element("dispBeamColumn",etag,nt(l-1,n),nt(l,n),1,integ)
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
            hpi=BH_END[(bn,"i")]; hpj=BH_END[(bn,"j")]
            mi=20000+l*1000+ib*2; mj=mi+1
            hinge_mat(mi,*hpi); hinge_mat(mj,*hpj)
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
            # Elastic member response remains in the beam; the zeroLength spring above
            # represents plastic rotation only.
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
        for n in names:
            ops.load(nt(l,n),0,0,-W*TRIB_AREA[n]/TRIB_TOTAL,0,0,0)
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

def run_pushover_x(target=0.20,du=0.00025):
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
            recovered=False
            # progressively smaller displacement increments and alternate algorithms
            for fac,alg in [(0.5,"NewtonLineSearch"),(0.25,"KrylovNewton"),(0.10,"ModifiedNewton")]:
                ops.integrator("DisplacementControl",masters[-1],1,du*fac)
                ops.test("NormDispIncr",1e-6,120)
                if alg=="NewtonLineSearch": ops.algorithm("NewtonLineSearch",0.8)
                elif alg=="KrylovNewton": ops.algorithm("KrylovNewton")
                else: ops.algorithm("ModifiedNewton","-initial")
                if ops.analyze(1)==0:
                    recovered=True
                    # complete the remaining fraction of the nominal step using small increments
                    rem=du*(1.0-fac); nsub=max(1,round(rem/(du*fac)))
                    ops.integrator("DisplacementControl",masters[-1],1,rem/nsub)
                    for _ in range(nsub):
                        if ops.analyze(1)!=0: break
                    break
            ops.algorithm("Newton"); ops.test("NormDispIncr",1e-7,50)
            ops.integrator("DisplacementControl",masters[-1],1,du)
            ok=0 if recovered else -1
        if ok!=0:
            print(f"NONCONVERGENCE step={step} roof={ops.nodeDisp(masters[-1],1):.6f}")
            break
        ops.reactions()
        vb=-sum(ops.nodeReaction(n,1) for n in base_nodes)
        u=ops.nodeDisp(masters[-1],1)
        rows.append((u,vb))
        if step%20==0:
            print(f"PUSHX step={step} u={u:.5f} Vb={vb/1e3:.2f} kN")
        # Column force audit at representative roof displacements.
        if any(abs(u-x)<du*0.75 for x in (0.02,0.05,0.10,0.15,0.18)):
            audit=[]
            # First-storey tags follow PLAN insertion order.
            for et,n in enumerate(names,1):
                ef=ops.eleForce(et)
                # local end forces: P,Vy,Vz,T,My,Mz at i-end.
                p=ef[0]/1e3; my=ef[4]/1e3; mz=ef[5]/1e3
                audit.append(f"{n}:P={p:.1f},My={my:.1f},Mz={mz:.1f}")
            print(f"COLAUDIT u={u:.5f} " + " | ".join(audit))

    csv=OUT/"pushover_x_efcp_endfibers.csv"
    csv.write_text("roof_disp_m,base_shear_N\n"+"\n".join(f"{u:.8f},{v:.6f}" for u,v in rows)+"\n")
    peak=max(abs(v) for _,v in rows) if rows else 0
    summary={
      "status":"success" if ok==0 and rows[-1][0]>=target-du*1.5 else "partial",
      "target_m":target,"reached_m":rows[-1][0],"peak_base_shear_kN":peak/1e3,
      "modal_periods_s":T,"modal_shape_x":phi,"modal_pattern":forces,
      "gravity":"published floor seismic weights distributed by reconstructed tributary areas (Voronoi on published plan polygon)",
      "beam_hinges":"Table 4-4 end-specific B1-B12; elastic member + concentrated plastic-rotation springs; plastic capacity theta_u-theta_y",
      "columns":"EFCP source-consistent endpoint fibre sections: dispBeamColumn with 2-point Lobatto; Concrete02/Steel02",
      "warning":"B13/B14 topology not represented in frozen modal topology; nonlinear gate remains provisional until reconciled."
    }
    (OUT/"pushover_x_efcp_endfibers_summary.json").write_text(json.dumps(summary,indent=2))
    print("PUSHOVER_X_SUMMARY",json.dumps(summary))
    ops.wipe()
    return 0 if summary["status"]=="success" else 3

if __name__=="__main__":
    raise SystemExit(run_pushover_x())
