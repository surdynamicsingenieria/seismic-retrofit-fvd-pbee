"""ConcentratedPlasticity diagnostic: endpoint bending tangent sweep.

Uses identical fibre columns and elastic beam interiors. End sections contain ONLY
Mz and My, following Mazzoni & Scott's 3D ConcentratedPlasticity example.
Reports raw eigenvalues and static X roof stiffness.
"""
import sys,math
sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as src
import spear_m0_nonlinear_efcp_cp as cp

def build(K):
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=37.5e6
    ops.uniaxialMaterial("Concrete01",100,-fc,-0.002,-0.2*fc,-0.0037)
    ops.uniaxialMaterial("Steel02",101,352e6,200e9,0.005,18.0,0.925,0.15)
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

    E=22e9*((fc+8e6)/10e6)**0.3; G=E/(2*1.2)
    A,Iy,Iz,J=src.rect_props(0.25,0.50)
    ops.section("Elastic",400,E,A,Iz,Iy,G,J)
    tr=1000; integ=2000; mat=3000; sec=4000
    for l in range(1,4):
        for bname,a,b in src.BEAMS:
            xa,ya=src.PLAN[a]; xb,yb=src.PLAN[b]
            L=math.hypot(xb-xa,yb-ya); ux=(xb-xa)/L; uy=(yb-ya)/L
            di=src.c6_half_extent(ux,uy) if a=="C6" else 0
            dj=src.c6_half_extent(ux,uy) if b=="C6" else 0
            tr+=1; ops.geomTransf("Linear",tr,0,0,1,"-jntOffset",ux*di,uy*di,0,-ux*dj,-uy*dj,0)
            ends=[]
            for _ in range(2):
                mat+=1; mz=mat; ops.uniaxialMaterial("Elastic",mz,K)
                mat+=1; my=mat; ops.uniaxialMaterial("Elastic",my,K)
                sec+=1; ss=sec; ops.section("Aggregator",ss,mz,"Mz",my,"My")
                ends.append(ss)
            integ+=1; ops.beamIntegration("ConcentratedPlasticity",integ,ends[0],ends[1],400)
            ops.element("forceBeamColumn",tag,nt(l,a),nt(l,b),tr,integ); tag+=1
    return

def raw_eigs(n=9):
    try:
        return list(ops.eigen("-fullGenLapack",n))
    except Exception as e:
        return ["ERR:"+repr(e)]

def static_roof():
    ops.timeSeries("Linear",90); ops.pattern("Plain",90,90)
    for n in (901,902,903): ops.load(n,1000/3,0,0,0,0,0)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-12,50,0); ops.algorithm("Linear")
    ops.integrator("LoadControl",1.0); ops.analysis("Static")
    ok=ops.analyze(1); u=ops.nodeDisp(903,1)
    return ok,u,(1000/u if u else float("inf"))

for K in (1e6,1e7,1e8,1e9,1e10,1e11,1e12):
    try:
        build(K)
        vals=raw_eigs()
        print("CPSWEEP_EIG",f"{K:.3e}",",".join(str(x) for x in vals))
        ops.wipeAnalysis()
        ok,u,k=static_roof()
        print("CPSWEEP_STATIC",f"{K:.3e}","ok",ok,"roof",f"{u:.12e}","K",f"{k:.6e}")
    except Exception as e:
        print("CPSWEEP_ERR",K,repr(e))
    ops.wipe()
