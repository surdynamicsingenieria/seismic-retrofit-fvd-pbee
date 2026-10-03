import sys
sys.path.insert(0,"models/SPEAR")
import openseespy.opensees as ops
import spear_m0_nonlinear_efcp as m

info=m.build_model()
m.run_gravity()
ops.timeSeries("Linear",50)
ops.pattern("Plain",50,50)
for n in info["masters"]:
    ops.load(n,1e3/3,0,0,0,0,0)
ops.wipeAnalysis()
ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
ops.test("NormDispIncr",1e-10,50); ops.algorithm("Newton")
ops.integrator("LoadControl",1.0); ops.analysis("Static")
print("DEBUG_SMALL_X ok=",ops.analyze(1))
for e in info["hinges"][:12]:
    try:
        d=ops.eleResponse(e,"deformation")
        f=ops.eleResponse(e,"force")
        print("HINGE",e,"DEF",d,"FORCE",f)
    except Exception as ex:
        print("HINGEERR",e,ex)
print("PERIODS",m.modal_periods(3))
ops.wipe()
