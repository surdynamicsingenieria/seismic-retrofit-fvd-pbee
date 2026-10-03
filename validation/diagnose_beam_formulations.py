"""Compare beam formulations with identical fibre columns, masses and geometry."""
import sys,math
sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as src
import spear_m0_nonlinear_efcp_cp as cp

def build(mode):
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    fc=37.5e6
    ops.uniaxialMaterial("Concrete01",100,-fc,-0.002,-0.2*fc,-0.0037)
    ops.uniaxialMaterial("Steel02",101,352e6,200e9,0.005,18,0.925,0.15)
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
            ops.element("forceBeamColumn",tag,nt(l-1,n),nt(l,n),1,302 if n=="C6" else 301)
            tag+=1

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
            if mode=="elasticBeamColumn":
                ops.element("elasticBeamColumn",tag,nt(l,a),nt(l,b),A,E,G,J,Iy,Iz,tr)
            elif mode=="forceElastic":
                integ+=1; ops.beamIntegration("Lobatto",integ,400,5)
                ops.element("forceBeamColumn",tag,nt(l,a),nt(l,b),tr,integ)
            elif mode in ("CP","CP2"):
                # CP2 explicitly defines both bending plastic-deformation modes, as in the
                # OpenSees 3D ConcentratedPlasticity example.
                mat+=1; myi=mat; ops.uniaxialMaterial("Elastic",myi,1e15)
                if mode=="CP":
                    sec+=1; si=sec; ops.section("Uniaxial",si,myi,"My")
                else:
                    mat+=1; mzi=mat; ops.uniaxialMaterial("Elastic",mzi,1e15)
                    sec+=1; si=sec; ops.section("Aggregator",si,mzi,"Mz",myi,"My")
                mat+=1; myj=mat; ops.uniaxialMaterial("Elastic",myj,1e15)
                if mode=="CP":
                    sec+=1; sj=sec; ops.section("Uniaxial",sj,myj,"My")
                else:
                    mat+=1; mzj=mat; ops.uniaxialMaterial("Elastic",mzj,1e15)
                    sec+=1; sj=sec; ops.section("Aggregator",sj,mzj,"Mz",myj,"My")
                integ+=1; ops.beamIntegration("ConcentratedPlasticity",integ,si,sj,400)
                ops.element("forceBeamColumn",tag,nt(l,a),nt(l,b),tr,integ)
            tag+=1
    vals=ops.eigen("-fullGenLapack",6)
    return [2*math.pi/math.sqrt(v) for v in vals]

for mode in ("elasticBeamColumn","forceElastic","CP","CP2"):
    try:
        p=build(mode)
        print("BEAMFORM",mode,",".join(f"{x:.6f}" for x in p))
    except Exception as e:
        print("BEAMFORM_ERR",mode,repr(e))
ops.wipe()
