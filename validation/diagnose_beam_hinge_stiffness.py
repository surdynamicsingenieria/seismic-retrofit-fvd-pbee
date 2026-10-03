"""Diagnostic sweep of beam-end rotational spring stiffness."""
import sys,math
sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as nl

orig=nl.make_hysteretic

def periods():
    vals=ops.eigen("-fullGenLapack",3)
    return [2*math.pi/math.sqrt(v) for v in vals]

for K in (1e4,1e5,1e6,1e7,1e8,1e10,1e12):
    def mk(mat,data,K=K):
        ops.uniaxialMaterial("Elastic",mat,K)
    nl.make_hysteretic=mk
    try:
        nl.build_model()
        p=periods()
        print("HINGEK",f"{K:.3e}",",".join(f"{x:.6f}" for x in p))
    except Exception as e:
        print("HINGEK_ERR",K,repr(e))
    ops.wipe()

nl.make_hysteretic=orig
nl.build_model()
print("HINGEK_PUBLISHED",",".join(f"{x:.6f}" for x in periods()))
ops.wipe()
