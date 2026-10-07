"""Jeong-Elnashai MAE 04-03 SPEAR M0 diagnostic modal model.
No Stratan-Fajfar hinge data. No modal calibration.
"""
import json
import math
from pathlib import Path
import openseespy.opensees as ops
from geometry_source import JOINTS as PLAN, BEAMS, BEFF_MM, STORY_CENTERLINES, SLAB_THICKNESS

OUT = Path("results/SPEAR/jeong_elnashai")
OUT.mkdir(parents=True, exist_ok=True)
Z = list(STORY_CENTERLINES)
G = 9.807
GAMMA_RC = 24.518

def rect(sec, mat, b, h):
    ops.section("Fiber", sec, "-GJ", 1.0e8)
    ops.patch("rect", mat, 12, 12, -b/2, -h/2, b/2, h/2)

def polygon_area(poly):
    return 0.5 * abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1] - poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))))

def build():
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    fc = 25.0e6
    Es = 206.0e9
    fy12 = 458.67e6
    Ec = 4700.0 * math.sqrt(25.0) * 1.0e6
    ops.uniaxialMaterial("Concrete02", 1, -fc, -0.002, -0.2*fc, -0.006, 0.1, 0.0, 0.0)
    ops.uniaxialMaterial("Steel02", 2, fy12, Es, 0.0032, 18.0, 0.925, 0.15)
    names = list(PLAN)
    ix = {n:i+1 for i,n in enumerate(names)}
    def nt(k,n): return 100*k + ix[n]
    for k,z in enumerate(Z):
        for n,(x,y) in PLAN.items():
            ops.node(nt(k,n), x, y, z)
            if k == 0: ops.fix(nt(k,n), 1,1,1,1,1,1)
        # Physical beam-axis connection points at C6: B5/B6 are 0.50 m apart,
        # symmetric about the C6 centroid. Rigid-total arms are modeled as
        # explicit very-stiff elastic elements, avoiding chained MP constraints.
        ops.node(8000+k*10+5, PLAN["C6"][0], PLAN["C6"][1]-0.25, z)
        ops.node(8000+k*10+6, PLAN["C6"][0], PLAN["C6"][1]+0.25, z)
        if k == 0:
            ops.fix(8000+k*10+5,1,1,1,1,1,1); ops.fix(8000+k*10+6,1,1,1,1,1,1)

    # Explicit rigid arms C6 -> B5/B6 connection axes (L=0.25 m).\n    # Large but finite section stiffness approximates a rigid joint arm without MP chaining.\n    Er=Ec*1.0e4; Gr=Er/(2*1.2); Ar=1.0; Ir=1.0; Jr=1.0\n    for k in range(1,4):\n        trr=6000+k\n        ops.geomTransf("Linear",trr,0,0,1)\n        ops.element("elasticBeamColumn",60000+k*10+5,nt(k,"C6"),8000+k*10+5,Ar,Er,Gr,Jr,Ir,Ir,trr)\n        ops.element("elasticBeamColumn",60000+k*10+6,nt(k,"C6"),8000+k*10+6,Ar,Er,Gr,Jr,Ir,Ir,trr)\n        rect(101,1,0.25,0.25)
    rect(102,1,0.75,0.25)
    ops.beamIntegration("Lobatto",201,101,5)
    ops.beamIntegration("Lobatto",202,102,5)
    # Fig. 2.4 / Table 2.8: rigid joint zones at column ends.
    # First-storey deformable height is 2.75 m: no footing offset, 0.25 m top offset.
    et=1
    for k in range(1,4):
        for n in names:
            trc=5000+k*100+ix[n]
            bot=0.0 if k==1 else 0.25
            top=0.25
            ops.geomTransf("PDelta",trc,1,0,0,"-jntOffset",0,0,bot,0,0,-top)
            ops.element("dispBeamColumn",et,nt(k-1,n),nt(k,n),trc,202 if n=="C6" else 201)
            et += 1
    for k in range(1,4):
        for j,(bn,a,b) in enumerate(BEAMS):
            beff = BEFF_MM[bn]/1000.0
            A = 0.25*0.50 + (beff-0.25)*SLAB_THICKNESS
            Af=beff*SLAB_THICKNESS; Aw=0.25*(0.50-SLAB_THICKNESS)
            zf=0.50-SLAB_THICKNESS/2; zw=(0.50-SLAB_THICKNESS)/2
            zbar=(Af*zf+Aw*zw)/(Af+Aw)
            I=beff*SLAB_THICKNESS**3/12+Af*(zf-zbar)**2+0.25*(0.50-SLAB_THICKNESS)**3/12+Aw*(zw-zbar)**2
            Iz=0.50*0.25**3/12; J=0.25*0.50**3/3
            # Beam deformable length starts at column faces. All column dimensions
            # normal to these beam axes are 0.25 m, including C6 in its x direction.
            xa,ya=PLAN[a]; xb,yb=PLAN[b]
            ni,nj=nt(k,a),nt(k,b)
            if bn=="B5" and b=="C6": xb,yb=PLAN["C6"][0],PLAN["C6"][1]-0.25; nj=8000+k*10+5
            if bn=="B6" and a=="C6": xa,ya=PLAN["C6"][0],PLAN["C6"][1]+0.25; ni=8000+k*10+6
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            # Source geometry: C6 is 0.75 m in global Y. B10 approaches C6 along Y,
            # therefore its C6-end rigid offset is 0.375 m; regular column faces are 0.125 m.
            off_i=0.125
            off_j=0.375 if (bn=="B10" and b=="C6") else 0.125
            oi=(off_i*ux,off_i*uy,0.0)
            oj=(-off_j*ux,-off_j*uy,0.0)
            tr=7000+k*100+j
            ops.geomTransf("Linear",tr,0,0,1,"-jntOffset",*oi,*oj)
            ops.element("elasticBeamColumn",10000+k*100+j,ni,nj,A,Ec,Ec/(2*1.2),J,I,Iz,tr)
    poly=[PLAN[x] for x in ("C8","C7","C4","C2","C5")]
    area=polygon_area(poly)
    beamW=sum(math.hypot(PLAN[b][0]-PLAN[a][0],PLAN[b][1]-PLAN[a][1])*0.25*(0.50-SLAB_THICKNESS)*GAMMA_RC for _,a,b in BEAMS)
    colW=(8*0.25*0.25+0.75*0.25)*3.0*GAMMA_RC
    W=area*SLAB_THICKNESS*GAMMA_RC + area*(0.5+0.6) + beamW + colW
    floor_mass_t={1:65.5,2:65.5,3:64.1}
    floor_cm={1:(4.53,5.29),2:(4.53,5.29),3:(4.57,5.33)}
    floor_Jm_tm2={1:1254.0,2:1254.0,3:1196.0}
    for k in range(1,4):
        mf_t=floor_mass_t[k]
        mf=1000.0*mf_t
        cx,cy=floor_cm[k]
        Jm=1000.0*floor_Jm_tm2[k]
        m=900+k
        ops.node(m,cx,cy,Z[k])
        ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,mf,mf,0,0,0,Jm)
        ops.rigidDiaphragm(3,m,*([nt(k,n) for n in names]+[8000+k*10+5,8000+k*10+6]))
    print("PHYSICAL_MASS_DIAGNOSTIC",json.dumps({"source":"published SPEAR mass properties","floor_mass_t":floor_mass_t,"floor_cm":floor_cm,"floor_Jm_tm2":floor_Jm_tm2}))

def modal():
    build()
    vals=ops.eigen("-fullGenLapack",4)
    T=[2*math.pi/math.sqrt(v) for v in vals]
    target=[0.51,0.46,0.40,0.18]
    err=[100*(a-b)/b for a,b in zip(T,target)]
    out={"status":"audit_c6_explicit_rigid_elements_pm0p25","periods_s":T,"targets_s":target,"errors_pct":err,"pending":["C6 rigid arms/eccentricity","member reinforcement","Fig 2.6 exact tributary nodal masses","full nonlinear T-beam fibres"]}
    (OUT/"modal_baseline.json").write_text(json.dumps(out,indent=2))
    print("JEONG_ELNASHAI_MODAL",json.dumps(out))
    ops.wipe()

if __name__ == "__main__":
    modal()
