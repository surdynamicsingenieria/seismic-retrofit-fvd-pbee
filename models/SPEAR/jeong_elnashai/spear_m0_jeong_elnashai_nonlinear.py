"""SPEAR Jeong-Elnashai nonlinear M0 — independent pushover diagnostic.

Derived ONLY from MAE 04-03 source-locked reconstruction.
No Stratan-Fajfar hinges and no modal/capacity calibration.

Gate status:
- modal geometry/mass properties inherited from spear_m0_jeong_elnashai.py
- distributed-plasticity fibre columns; P-Delta; rigid joint offsets/C6 arms
- beams use nonlinear fibre T-sections with source material properties
- reinforcement details are intentionally isolated as PENDING_SOURCE_DATA below;
  therefore pushover results are DIAGNOSTIC_ONLY until the complete member
  reinforcement schedule and Fig. 2.6 nodal gravity/mass allocation are locked.
"""
import math, json
from pathlib import Path
import openseespy.opensees as ops
from geometry_source import JOINTS as PLAN, BEAMS, BEFF_MM, STORY_CENTERLINES, SLAB_THICKNESS

OUT=Path("results/SPEAR/jeong_elnashai/pushover"); OUT.mkdir(parents=True,exist_ok=True)
Z=list(STORY_CENTERLINES); GACC=9.807
MASSES=[65.5e3,65.5e3,64.1e3]; POLAR=[1254e3,1254e3,1196e3]
CM=[(4.53,5.29),(4.53,5.29),(4.57,5.33)]
PENDING_SOURCE_DATA=["complete beam reinforcement by member/storey","complete column reinforcement by member/storey","Fig 2.6 exact nodal gravity allocation"]

def fiber_rect(sec,conc,steel,b,h,nbar=4,bar_d=0.012):
    ops.section("Fiber",sec,"-GJ",1e8)
    ops.patch("rect",conc,14,14,-b/2,-h/2,b/2,h/2)
    c=.031; As=math.pi*bar_d**2/4
    if nbar==4:
        for y in (-b/2+c,b/2-c):
            for z in (-h/2+c,h/2-c): ops.fiber(y,z,As,steel)
    else:
        for z in (-h/2+c,h/2-c):
            for i in range(nbar//2):
                y=-b/2+c+(b-2*c)*i/(nbar//2-1)
                ops.fiber(y,z,As,steel)

def build():
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=25e6; Es=206e9; fy=458.67e6
    Ec=4700*math.sqrt(25)*1e6; G=Ec/(2*1.2)
    ops.uniaxialMaterial("Concrete02",1,-fc,-.002,-.2*fc,-.006,.1,0,0)
    ops.uniaxialMaterial("Steel02",2,fy,Es,.0032,18,.925,.15)
    names=list(PLAN); ix={n:i+1 for i,n in enumerate(names)}
    def nt(k,n): return 100*k+ix[n]
    for k,z in enumerate(Z):
        for n,(x,y) in PLAN.items():
            ops.node(nt(k,n),x,y,z)
            if k==0: ops.fix(nt(k,n),1,1,1,1,1,1)
        ops.node(8000+k*10+5,PLAN["C6"][0],PLAN["C6"][1]-.25,z)
        ops.node(8000+k*10+6,PLAN["C6"][0],PLAN["C6"][1]+.25,z)
        if k==0:
            ops.fix(8000+k*10+5,1,1,1,1,1,1); ops.fix(8000+k*10+6,1,1,1,1,1,1)

    # Diagnostic reinforcement only: kept explicit so it cannot be mistaken for source-locked input.
    fiber_rect(101,1,2,.25,.25,4)
    fiber_rect(102,1,2,.75,.25,10)
    ops.beamIntegration("Lobatto",201,101,5); ops.beamIntegration("Lobatto",202,102,5)

    # C6 explicit rigid arms, identical geometry to accepted modal reconstruction.
    Er=Ec*1e4; Gr=Er/(2*1.2)
    for k in range(1,4):
        tr=6000+k; ops.geomTransf("Linear",tr,0,0,1)
        for q in (5,6):
            ops.element("elasticBeamColumn",60000+k*10+q,nt(k,"C6"),8000+k*10+q,1.,Er,Gr,1.,1.,1.,tr)

    et=1
    for k in range(1,4):
        for n in names:
            tr=5000+k*100+ix[n]; bot=0 if k==1 else .25
            ops.geomTransf("PDelta",tr,1,0,0,"-jntOffset",0,0,bot,0,0,-.25)
            ops.element("dispBeamColumn",et,nt(k-1,n),nt(k,n),tr,202 if n=="C6" else 201); et+=1

    # Until the exact beam reinforcement schedule is locked, preserve the source-derived
    # T-section ELASTIC stiffness. This prevents invented beam plastic capacities.
    for k in range(1,4):
        for j,(bn,a,b) in enumerate(BEAMS):
            beff=BEFF_MM[bn]/1000.; A=.25*.50+(beff-.25)*SLAB_THICKNESS
            Af=beff*SLAB_THICKNESS; Aw=.25*(.50-SLAB_THICKNESS)
            zf=.50-SLAB_THICKNESS/2; zw=(.50-SLAB_THICKNESS)/2
            zb=(Af*zf+Aw*zw)/(Af+Aw)
            I=beff*SLAB_THICKNESS**3/12+Af*(zf-zb)**2+.25*(.50-SLAB_THICKNESS)**3/12+Aw*(zw-zb)**2
            Iz=.50*.25**3/12; J=.25*.50**3/3
            xa,ya=PLAN[a]; xb,yb=PLAN[b]; ni,nj=nt(k,a),nt(k,b)
            if bn=="B5" and b=="C6": xb,yb=PLAN["C6"][0],PLAN["C6"][1]-.25; nj=8000+k*10+5
            if bn=="B6" and a=="C6": xa,ya=PLAN["C6"][0],PLAN["C6"][1]+.25; ni=8000+k*10+6
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            oi=(.125*ux,.125*uy,0); oj=(-( .375 if bn=="B10" and b=="C6" else .125)*ux,-( .375 if bn=="B10" and b=="C6" else .125)*uy,0)
            tr=7000+k*100+j; ops.geomTransf("Linear",tr,0,0,1,"-jntOffset",*oi,*oj)
            ops.element("elasticBeamColumn",10000+k*100+j,ni,nj,A,Ec,G,J,I,Iz,tr)

    masters=[]
    for k in range(1,4):
        m=900+k; cx,cy=CM[k-1]; ops.node(m,cx,cy,Z[k]); ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,MASSES[k-1],MASSES[k-1],0,0,0,POLAR[k-1])
        ops.rigidDiaphragm(3,m,*([nt(k,n) for n in names]+[8000+k*10+5,8000+k*10+6])); masters.append(m)
    return names,nt,masters

def gravity(names,nt):
    # Diagnostic nodal allocation only. Total floor weight is exact from published seismic mass.
    ops.timeSeries("Linear",10); ops.pattern("Plain",10,10)
    for k in range(1,4):
        w=MASSES[k-1]*GACC/len(names)
        for n in names: ops.load(nt(k,n),0,0,-w,0,0,0)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-8,50); ops.algorithm("Newton"); ops.integrator("LoadControl",.1); ops.analysis("Static")
    ok=ops.analyze(10)
    if ok==0: ops.loadConst("-time",0)
    return ok

def run(direction="+X",target=.12,du=.00025):
    names,nt,masters=build()
    if gravity(names,nt)!=0: raise RuntimeError("gravity analysis failed")
    vals=ops.eigen("-fullGenLapack",4); periods=[2*math.pi/math.sqrt(v) for v in vals]
    dof=1 if direction[-1]=="X" else 2; sign=1 if direction[0]=="+" else -1
    phi=[ops.nodeEigenvector(m,1,dof) for m in masters]
    if sum(MASSES[i]*phi[i] for i in range(3))*sign<0: phi=[-v for v in phi]
    f=[MASSES[i]*phi[i] for i in range(3)]; s=sum(abs(v) for v in f); f=[v/s for v in f]
    ops.timeSeries("Linear",20); ops.pattern("Plain",20,20)
    for m,q in zip(masters,f): ops.load(m,q if dof==1 else 0,q if dof==2 else 0,0,0,0,0)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-7,80); ops.algorithm("Newton")
    ops.integrator("DisplacementControl",masters[-1],dof,sign*abs(du)); ops.analysis("Static")
    rows=[(0.,0.)]; base=[nt(0,n) for n in names]; ok=0
    for step in range(int(abs(target/du))):
        ok=ops.analyze(1)
        if ok!=0:
            ops.test("NormDispIncr",1e-6,160); ops.algorithm("NewtonLineSearch",.8)
            ops.integrator("DisplacementControl",masters[-1],dof,sign*abs(du)/4)
            ok=ops.analyze(1)
            ops.algorithm("Newton"); ops.test("NormDispIncr",1e-7,80)
            ops.integrator("DisplacementControl",masters[-1],dof,sign*abs(du))
        if ok!=0: break
        ops.reactions(); u=ops.nodeDisp(masters[-1],dof); vb=-sum(ops.nodeReaction(n,dof) for n in base)
        rows.append((u,vb))
    key=direction.lower().replace("+","p").replace("-","n")
    (OUT/f"pushover_{key}.csv").write_text("roof_disp_m,base_shear_N\n"+"\n".join(f"{u:.8f},{v:.6f}" for u,v in rows)+"\n")
    summary={"status":"DIAGNOSTIC_ONLY","direction":direction,"periods_s":periods,"reached_m":rows[-1][0],"peak_abs_base_shear_kN":max(abs(v) for _,v in rows)/1e3,"pending_source_data":PENDING_SOURCE_DATA,"acceptance":"PROHIBITED until reinforcement and Fig 2.6 allocation are source-locked"}
    (OUT/f"pushover_{key}_summary.json").write_text(json.dumps(summary,indent=2))
    print("JEONG_ELNASHAI_PUSHOVER",json.dumps(summary)); ops.wipe()
    return 0 if ok==0 else 3

if __name__=="__main__":
    raise SystemExit(run("+X"))
