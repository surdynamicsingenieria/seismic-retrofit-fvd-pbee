"""Independent SPEAR M0 reconstruction following Jeong & Elnashai (2004), MAE 04-03.
First executable baseline. No Stratan-Fajfar hinge data and no calibration.
"""
import math, json
from pathlib import Path
import openseespy.opensees as ops

OUT=Path("results/SPEAR/jeong_elnashai"); OUT.mkdir(parents=True,exist_ok=True)
PLAN={"C8":(0.,0.),"C6":(3.,0.),"C7":(9.,0.),"C9":(0.,5.),"C3":(3.,5.),
      "C4":(9.7,4.),"C5":(0.,10.5),"C1":(3.,10.5),"C2":(8.,10.)}
BEAMS=[("B1","C5","C1"),("B2","C1","C2"),("B3","C9","C3"),("B4","C3","C4"),
       ("B5","C8","C6"),("B6","C6","C7"),("B7","C2","C4"),("B8","C4","C7"),
       ("B9","C1","C3"),("B10","C3","C6"),("B11","C5","C9"),("B12","C9","C8")]
BEFF={"B1":.4425,"B2":.5825,"B3":.635,"B4":1.055,"B5":.4425,"B6":.6525,
      "B7":1.055,"B8":.775,"B9":1.055,"B10":.775,"B11":.6175,"B12":.5825}
Z=[0.,3.,6.,9.]
# Report 04-03 gravity: DL + 0.3LL; finishing=0.5, LL=2.0 kN/m2.
# Use the published plan polygon area only for this first source-locked modal baseline.
FLOOR_AREA=92.5
RHO_RC=2500.0
SLAB=.15
G=9.81

def rect(sec,mat,b,h,nfy=12,nfz=12):
    ops.section("Fiber",sec,"-GJ",1.e8); ops.patch("rect",mat,nfy,nfz,-b/2,-h/2,b/2,h/2)

def build():
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    # Report 04-03 pre-test material values.
    fc=25.e6; Es=206.e9; fy12=458.67e6
    Ec=4700*math.sqrt(25)*1e6
    ops.uniaxialMaterial("Concrete02",1,-fc,-.002,-.2*fc,-.006,.1,0.,0.)
    ops.uniaxialMaterial("Steel02",2,fy12,Es,.0032,18.,.925,.15)
    # Nodes. Physical joint offsets are source-required; explicit offset geometry is next gate.
    names=list(PLAN); ix={n:i+1 for i,n in enumerate(names)}
    def nt(k,n): return 100*k+ix[n]
    for k,z in enumerate(Z):
        for n,(x,y) in PLAN.items():
            ops.node(nt(k,n),x,y,z)
            if k==0: ops.fix(nt(k,n),1,1,1,1,1,1)
    # P-Delta for columns from the outset.
    ops.geomTransf("PDelta",1,1,0,0)
    # Source sections; reinforcement fibres are deliberately pending source transcription.
    rect(101,1,.25,.25); rect(102,1,.75,.25)
    ops.beamIntegration("Lobatto",201,101,5); ops.beamIntegration("Lobatto",202,102,5)
    et=1
    for k in range(1,4):
        for n in names:
            ops.element("dispBeamColumn",et,nt(k-1,n),nt(k,n),1,202 if n=="C6" else 201); et+=1
    # T-beam elastic baseline using source effective flange widths; nonlinear beam fibres follow
    # once member-specific reinforcement is transcribed from the report.
    for k in range(1,4):
        for j,(bn,a,b) in enumerate(BEAMS):
            xa,ya=PLAN[a]; xb,yb=PLAN[b]; L=math.hypot(xb-xa,yb-ya)
            A=.25*.50+(BEFF[bn]-.25)*.15
            # Approximate gross T-section inertia about horizontal centroidal axis.
            Af=BEFF[bn]*.15; Aw=.25*.35
            zf=.425; zw=.175; zbar=(Af*zf+Aw*zw)/(Af+Aw)
            I=BEFF[bn]*.15**3/12+Af*(zf-zbar)**2+.25*.35**3/12+Aw*(zw-zbar)**2
            Iz=.50*.25**3/12; J=.25*.50**3/3
            tr=1000+k*100+j; ops.geomTransf("Linear",tr,0,0,1)
            ops.element("elasticBeamColumn",10000+k*100+j,nt(k,a),nt(k,b),A,Ec,Ec/(2*1.2),J,I,Iz,tr)
    # Rigid diaphragms. Mass includes slab + finishing + 0.3LL; member self-mass to be
    # replaced by exact source nodal mass reconstruction before validation.
    masters=[]
    area_mass=RHO_RC*SLAB+(0.5e3+0.3*2.0e3)/G
    mf=area_mass*FLOOR_AREA
    for k in range(1,4):
        m=900+k; ops.node(m,4.53,5.29,Z[k]); ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,mf,mf,0,0,0,mf*20.0)
        ops.rigidDiaphragm(3,m,*[nt(k,n) for n in names]); masters.append(m)
    return masters

def modal():
    masters=build(); vals=ops.eigen("-fullGenLapack",4)
    T=[2*math.pi/math.sqrt(x) for x in vals]
    target=[.51,.46,.40,.18]
    err=[100*(a-b)/b for a,b in zip(T,target)]
    out={"status":"diagnostic_not_validated","periods_s":T,"targets_s":target,"errors_pct":err,
         "pending":["explicit rigid end offsets","C6 rigid arms/eccentricity","member reinforcement",
                    "exact source nodal masses","full nonlinear T-beam fibres"]}
    (OUT/"modal_baseline.json").write_text(json.dumps(out,indent=2))
    print("JEONG_ELNASHAI_MODAL",json.dumps(out)); ops.wipe()
    return 0

if __name__=="__main__": raise SystemExit(modal())
