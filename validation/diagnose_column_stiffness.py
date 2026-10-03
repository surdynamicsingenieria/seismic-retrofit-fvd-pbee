"""Isolate initial column stiffness: fibre vs elastic, no beams."""
import math,sys
sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as nl

def build(kind):
    ops.wipe(); ops.model("basic","-ndm",3,"-ndf",6)
    names=list(nl.PLAN); idx={n:i+1 for i,n in enumerate(names)}
    def nt(l,n): return l*100+idx[n]
    for l in range(4):
        for n,(x,y) in nl.PLAN.items():
            ops.node(nt(l,n),x,y,nl.Z[l])
            if l==0: ops.fix(nt(l,n),1,1,1,1,1,1)
    for l in range(1,4):
        mx,my=nl.CM[l-1]; m=900+l
        ops.node(m,mx,my,nl.Z[l]); ops.fix(m,0,0,1,1,1,0)
        ops.mass(m,nl.MASSES[l-1],nl.MASSES[l-1],0,0,0,nl.POLAR[l-1])
        ops.rigidDiaphragm(3,m,*[nt(l,n) for n in names])
    ops.geomTransf("Linear",1,1,0,0)
    E=22e9*((37.5e6+8e6)/10e6)**0.3
    G=E/(2*1.2)
    if kind=="fiber":
        ops.uniaxialMaterial("Concrete01",100,-37.5e6,-0.002,-0.2*37.5e6,-0.0037)
        ops.uniaxialMaterial("Steel02",101,352e6,200e9,0.005,18.0,0.925,0.15)
        nl.build_column_section(201,False); nl.build_column_section(202,True)
        ops.beamIntegration("Lobatto",301,201,5); ops.beamIntegration("Lobatto",302,202,5)
    tag=1
    for l in range(1,4):
        for n in names:
            if kind=="fiber":
                ops.element("forceBeamColumn",tag,nt(l-1,n),nt(l,n),1,302 if n=="C6" else 301)
            else:
                if n=="C6":
                    # source-consistent orientation: 0.25 X x 0.75 Y.
                    # local y ~ global Y, local z ~ global X => Iy weak, Iz strong.
                    A=0.25*0.75; Iy=0.75*0.25**3/12; Iz=0.25*0.75**3/12
                    J=nl.rect_props(0.75,0.25)[3]
                else:
                    A,Iy,Iz,J=nl.rect_props(0.25,0.25)
                ops.element("elasticBeamColumn",tag,nt(l-1,n),nt(l,n),A,E,G,J,Iy,Iz,1)
            tag+=1
    vals=ops.eigen("-fullGenLapack",6)
    return [2*math.pi/math.sqrt(v) for v in vals]

for k in ("elastic","fiber"):
    try:
        p=build(k)
        print("COLONLY",k,",".join(f"{x:.6f}" for x in p))
    except Exception as e:
        print("COLONLY_ERR",k,repr(e))
ops.wipe()
