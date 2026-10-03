"""Unit-consistency diagnostic for OpenSees ConcentratedPlasticity.

Rebuilds the same SPEAR fibre-column/elastic-beam tangent model in N-mm-s units.
Mass unit is N*s^2/mm = kg/1000, so floor masses are 65.5, 65.5, 64.1.
Compares direct elastic beams with ConcentratedPlasticity beams whose end bending
sections are effectively rigid. No structural parameter is calibrated.
"""
import math
import openseespy.opensees as ops

S=1000.0
PLAN={
 "C8":(0,0),"C6":(3000,0),"C7":(9000,0),
 "C9":(0,5000),"C3":(3000,5000),"C4":(9700,4000),
 "C5":(0,10500),"C1":(3000,10500),"C2":(8000,10000),
}
BEAMS=[
 ("B1","C5","C1"),("B2","C1","C2"),("B3","C9","C3"),("B4","C3","C4"),
 ("B5","C8","C6"),("B6","C6","C7"),("B7","C4","C7"),("B8","C2","C4"),
 ("B9","C1","C3"),("B10","C3","C6"),("B11","C5","C9"),("B12","C9","C8"),
]
M=[65.5,65.5,64.1]
Jmass=[1.254e9,1.254e9,1.196e9]
CM=[(4530,5290),(4530,5290),(4570,5330)]
Z=[0,3000,6000,9000]

def rect(b,h):
    A=b*h; Iy=b*h**3/12; Iz=h*b**3/12
    aa=max(b,h); bb=min(b,h)
    J=aa*bb**3*(1/3-0.21*(bb/aa)*(1-bb**4/(12*aa**4)))
    return A,Iy,Iz,J

def c6ext(ux,uy):
    return 1/(abs(ux)/125+abs(uy)/375)

def colsec(tag,c6=False):
    fc=37.5; fy=352.; Es=200000.
    if c6: by,bz=750,250; ny,nz=18,6
    else: by,bz=250,250; ny,nz=8,8
    A,Iy,Iz,J=rect(by,bz)
    E=22e3*((37.5+8)/10)**0.3; G=E/(2*1.2)
    ops.section("Fiber",tag,"-GJ",G*J)
    ops.patch("rect",100,ny,nz,-by/2,-bz/2,by/2,bz/2)
    Ab=math.pi*12**2/4; cover=25; yy=by/2-cover; zz=bz/2-cover
    pts=[(-yy,-zz),(-yy,zz),(yy,-zz),(yy,zz)]
    if c6:
        pts += [(-yy/3,-zz),(yy/3,-zz),(-yy/3,zz),(yy/3,zz),(0,-zz),(0,zz)]
    for y,z in pts: ops.fiber(y,z,Ab,101)

def build(mode,K=1e15):
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    ops.uniaxialMaterial("Concrete01",100,-37.5,-0.002,-7.5,-0.0037)
    ops.uniaxialMaterial("Steel02",101,352.,200000.,0.005,18.,0.925,0.15)
    names=list(PLAN); idx={n:i+1 for i,n in enumerate(names)}
    def nt(l,n): return l*100+idx[n]
    for l in range(4):
        for n,(x,y) in PLAN.items():
            ops.node(nt(l,n),x,y,Z[l])
            if l==0: ops.fix(nt(l,n),1,1,1,1,1,1)
    for l in range(1,4):
        x,y=CM[l-1]; mm=900+l
        ops.node(mm,x,y,Z[l]); ops.fix(mm,0,0,1,1,1,0)
        ops.mass(mm,M[l-1],M[l-1],0,0,0,Jmass[l-1])
        ops.rigidDiaphragm(3,mm,*[nt(l,n) for n in names])
    ops.geomTransf("Linear",1,1,0,0)
    colsec(201,False); colsec(202,True)
    ops.beamIntegration("Lobatto",301,201,5); ops.beamIntegration("Lobatto",302,202,5)
    tag=1
    for l in range(1,4):
        for n in names:
            ops.element("forceBeamColumn",tag,nt(l-1,n),nt(l,n),1,302 if n=="C6" else 301)
            tag+=1
    E=22e3*((37.5+8)/10)**0.3; G=E/(2*1.2); A,Iy,Iz,J=rect(250,500)
    ops.section("Elastic",400,E,A,Iz,Iy,G,J)
    tr=1000; integ=2000; mat=3000; sec=4000
    for l in range(1,4):
        for _,a,b in BEAMS:
            xa,ya=PLAN[a]; xb,yb=PLAN[b]; L=math.hypot(xb-xa,yb-ya)
            ux=(xb-xa)/L; uy=(yb-ya)/L
            di=c6ext(ux,uy) if a=="C6" else 0; dj=c6ext(ux,uy) if b=="C6" else 0
            tr+=1; ops.geomTransf("Linear",tr,0,0,1,"-jntOffset",ux*di,uy*di,0,-ux*dj,-uy*dj,0)
            if mode=="direct":
                ops.element("elasticBeamColumn",tag,nt(l,a),nt(l,b),A,E,G,J,Iy,Iz,tr)
            else:
                ends=[]
                for _e in range(2):
                    mat+=1; mz=mat; ops.uniaxialMaterial("Elastic",mz,K)
                    mat+=1; my=mat; ops.uniaxialMaterial("Elastic",my,K)
                    sec+=1; ss=sec; ops.section("Aggregator",ss,mz,"Mz",my,"My"); ends.append(ss)
                integ+=1; ops.beamIntegration("ConcentratedPlasticity",integ,ends[0],ends[1],400)
                ops.element("forceBeamColumn",tag,nt(l,a),nt(l,b),tr,integ)
            tag+=1

def result(mode,K=1e15):
    build(mode,K)
    vals=ops.eigen("-fullGenLapack",6)
    T=[2*math.pi/math.sqrt(v) for v in vals if v>0]
    ops.timeSeries("Linear",9); ops.pattern("Plain",9,9)
    for n in (901,902,903): ops.load(n,1000/3,0,0,0,0,0)
    ops.wipeAnalysis(); ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.algorithm("Linear"); ops.integrator("LoadControl",1); ops.analysis("Static")
    ok=ops.analyze(1); u=ops.nodeDisp(903,1); k=1000/u
    print("MMUNIT",mode,f"Khinge={K:.3e}","T",",".join(f"{x:.6f}" for x in T),
          "roof_mm",f"{u:.9e}","K_Npmm",f"{k:.9e}","ok",ok)
    ops.wipe()

result("direct")
for K in (1e9,1e10,1e11,1e12,1e13,1e14,1e15):
    result("CP",K)
