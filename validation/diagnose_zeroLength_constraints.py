"""Test zeroLength rotational hinges with exact translational constraints."""
import sys,math
sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as src
import spear_m0_nonlinear_efcp_cp as cp

def build(K):
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=37.5e6
    ops.uniaxialMaterial("Concrete01",100,-fc,-0.002,-0.2*fc,-0.0037)
    ops.uniaxialMaterial("Steel02",101,352e6,200e9,0.005,18,0.925,0.15)
    ops.uniaxialMaterial("Elastic",110,1e12)
    names=list(src.PLAN); idx={n:i+1 for i,n in enumerate(names)}
    def nt(l,n): return l*100+idx[n]
    for l in range(4):
        for n,(x,y) in src.PLAN.items():
            ops.node(nt(l,n),x,y,src.Z[l])
            if l==0: ops.fix(nt(l,n),1,1,1,1,1,1)
    for l in range(1,4):
        mx,my=src.CM[l-1]; m=900+l
        ops.node(m,mx,my,src.Z[l]); ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,src.MASSES[l-1],src.MASSES[l-1],0,0,0,src.POLAR[l-1])
        ops.rigidDiaphragm(3,m,*[nt(l,n) for n in names])
    ops.geomTransf("Linear",1,1,0,0)
    cp.build_col_section(201,False); cp.build_col_section(202,True)
    ops.beamIntegration("Lobatto",301,201,5); ops.beamIntegration("Lobatto",302,202,5)
    tag=1
    for l in range(1,4):
        for n in names:
            ops.element("forceBeamColumn",tag,nt(l-1,n),nt(l,n),1,302 if n=="C6" else 301); tag+=1

    E=22e9*((fc+8e6)/10e6)**0.3; G=E/(2*1.2); A,Iy,Iz,J=src.rect_props(0.25,0.50)
    node=10000; mat=2000; tr=3000
    for l in range(1,4):
        for bname,a,b in src.BEAMS:
            xa,ya=src.PLAN[a]; xb,yb=src.PLAN[b]
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            ends=[]
            for name,sgn in ((a,1),(b,-1)):
                main=nt(l,name); x,y=src.PLAN[name]
                if name=="C6":
                    d=src.c6_half_extent(ux,uy); x+=sgn*ux*d; y+=sgn*uy*d
                    face=node; node+=1; ops.node(face,x,y,src.Z[l]); ops.rigidLink("beam",main,face)
                else: face=main
                dup=node; node+=1; ops.node(dup,x,y,src.Z[l])
                # exact translation continuity, no translational penalty springs
                ops.equalDOF(face,dup,1,2,3)
                mat+=1; ops.uniaxialMaterial("Elastic",mat,K)
                # rot x, rot y, rot z local; only local-z stiffness K varied, other two near-rigid
                trmat1=110; trmat2=110
                ops.element("zeroLength",tag,face,dup,
                    "-mat",trmat1,trmat2,mat,"-dir",4,5,6,
                    "-orient",ux,uy,0,0,0,1)
                tag+=1; ends.append(dup)
            tr+=1; ops.geomTransf("Linear",tr,0,0,1)
            ops.element("elasticBeamColumn",tag,ends[0],ends[1],A,E,G,J,Iy,Iz,tr); tag+=1
    vals=ops.eigen("-fullGenLapack",6)
    return [2*math.pi/math.sqrt(v) for v in vals]

for K in (1e4,1e6,1e8,1e12):
    try:
        p=build(K); print("ZLEXACT",f"{K:.3e}",",".join(f"{x:.6f}" for x in p))
    except Exception as e:
        print("ZLEXACT_ERR",K,repr(e))
ops.wipe()
