"""Static stiffness check: direct beams vs zeroLength rigid-end assembly."""
import sys
sys.path.insert(0,"validation"); sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import diagnose_beam_formulations as bf
import diagnose_zeroLength_constraints as zl

def lateral(label,builder):
    builder()
    ops.timeSeries("Linear",99); ops.pattern("Plain",99,99)
    for n in (901,902,903): ops.load(n,1000/3,0,0,0,0,0)
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-12,30); ops.algorithm("Linear")
    ops.integrator("LoadControl",1); ops.analysis("Static")
    ok=ops.analyze(1)
    u=ops.nodeDisp(903,1)
    print("STATICCHECK",label,"ok",ok,"roofX",f"{u:.12e}","K_Npm",f"{1000/u:.6e}" if u else "inf")
    ops.wipe()

lateral("direct",lambda: bf.build("elasticBeamColumn"))
lateral("zl_K1e8",lambda: zl.build(1e8))
lateral("zl_K1e12",lambda: zl.build(1e12))
