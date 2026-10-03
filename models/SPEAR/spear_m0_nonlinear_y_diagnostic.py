"""Diagnostic +Y pushover for the current SPEAR nonlinear reconstruction.

Uses the same frozen nonlinear model and gravity state as spear_m0_nonlinear.py.
Selects the mode with the largest effective Y participation among the first
three modes, then applies a mass-proportional modal load pattern in +Y.

DIAGNOSTIC ONLY until B13/B14 topology is reconciled.
"""
import json, math, sys
from pathlib import Path
import openseespy.opensees as ops

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import spear_m0_nonlinear as base

OUT=Path("results/SPEAR/pushover")
OUT.mkdir(parents=True,exist_ok=True)

def modal_y_pattern(masters,nmodes=3):
    vals=ops.eigen("-fullGenLapack",nmodes)
    candidates=[]
    for mode in range(1,nmodes+1):
        ph=[ops.nodeEigenvector(m,mode,2) for m in masters]
        modal_mass=sum(base.MASSES[i]*ph[i]*ph[i] for i in range(3))
        part=(sum(base.MASSES[i]*ph[i] for i in range(3))**2/modal_mass) if modal_mass else 0.0
        candidates.append((part,mode,ph))
    _,mode,ph=max(candidates,key=lambda x:x[0])
    if sum(base.MASSES[i]*ph[i] for i in range(3))<0:
        ph=[-x for x in ph]
    f=[base.MASSES[i]*ph[i] for i in range(3)]
    s=sum(abs(x) for x in f)
    f=[x/s for x in f]
    return vals,mode,ph,f,[(m,p) for p,m,_ in candidates]

def run_pushover_y(target=0.20,du=0.00025):
    names,idx,nt,masters,Ec=base.build()
    gok=base.gravity(names,nt)
    if gok!=0:
        print("GRAVITY_FAIL",gok)
        return 2

    vals,mode,phi,forces,parts=modal_y_pattern(masters)
    periods=[2*math.pi/math.sqrt(v) for v in vals]
    print("PUSHY_SELECTED_MODE",mode,"Y_PARTICIPATION_RANK",parts)

    ops.timeSeries("Linear",30); ops.pattern("Plain",30,30)
    for m,f in zip(masters,forces):
        ops.load(m,0,f,0,0,0,0)

    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr",1e-7,50); ops.algorithm("Newton")
    ops.integrator("DisplacementControl",masters[-1],2,du)
    ops.analysis("Static")

    rows=[(0.0,0.0)]
    nsteps=int(target/du)
    base_nodes=[nt(0,n) for n in names]
    ok=0

    for step in range(1,nsteps+1):
        ok=ops.analyze(1)
        if ok!=0:
            recovered=False
            for fac,alg in [(0.5,"NewtonLineSearch"),(0.25,"KrylovNewton"),(0.10,"ModifiedNewton")]:
                ops.integrator("DisplacementControl",masters[-1],2,du*fac)
                ops.test("NormDispIncr",1e-6,120)
                if alg=="NewtonLineSearch":
                    ops.algorithm("NewtonLineSearch",0.8)
                elif alg=="KrylovNewton":
                    ops.algorithm("KrylovNewton")
                else:
                    ops.algorithm("ModifiedNewton","-initial")
                if ops.analyze(1)==0:
                    recovered=True
                    rem=du*(1.0-fac)
                    nsub=max(1,round(rem/(du*fac)))
                    ops.integrator("DisplacementControl",masters[-1],2,rem/nsub)
                    for _ in range(nsub):
                        if ops.analyze(1)!=0:
                            break
                    break
            ops.algorithm("Newton"); ops.test("NormDispIncr",1e-7,50)
            ops.integrator("DisplacementControl",masters[-1],2,du)
            ok=0 if recovered else -1

        if ok!=0:
            print(f"NONCONVERGENCE_Y step={step} roof={ops.nodeDisp(masters[-1],2):.6f}")
            break

        ops.reactions()
        vb=-sum(ops.nodeReaction(n,2) for n in base_nodes)
        u=ops.nodeDisp(masters[-1],2)
        rows.append((u,vb))
        if step%20==0:
            print(f"PUSHY step={step} u={u:.5f} Vb={vb/1e3:.2f} kN")

    csv=OUT/"pushover_y_diagnostic.csv"
    csv.write_text("roof_disp_m,base_shear_N\n"+"\n".join(f"{u:.8f},{v:.6f}" for u,v in rows)+"\n")
    peak=max(abs(v) for _,v in rows) if rows else 0.0
    summary={
        "status":"success" if ok==0 and rows[-1][0]>=target-du*1.5 else "partial",
        "direction":"+Y",
        "diagnostic_only":True,
        "target_m":target,
        "reached_m":rows[-1][0],
        "peak_base_shear_kN":peak/1e3,
        "selected_y_mode":mode,
        "modal_periods_s":periods,
        "modal_shape_y":phi,
        "modal_pattern":forces,
        "warning":"B13/B14 nonlinear topology unresolved; do not use this curve as final validation."
    }
    (OUT/"pushover_y_diagnostic_summary.json").write_text(json.dumps(summary,indent=2))
    print("PUSHOVER_Y_SUMMARY",json.dumps(summary))
    ops.wipe()
    return 0 if summary["status"]=="success" else 3

if __name__=="__main__":
    raise SystemExit(run_pushover_y())
