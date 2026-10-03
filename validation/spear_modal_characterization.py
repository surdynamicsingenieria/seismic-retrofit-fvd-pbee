"""Modal characterization for SPEAR-M0 EFCP diagnostic.

Reports modal periods plus effective participation fractions in global X, global Y,
and torsional Rz using the three diaphragm master nodes. This script does not modify
the structural model.
"""
import math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"models"/"SPEAR"))

import openseespy.opensees as ops
import spear_m0_efcp as model

MASSES=model.MASSES
POLAR=model.POLAR
MASTERS=[901,902,903]

def characterize(n_modes=6):
    model.build_spear_m0_efcp()
    vals=ops.eigen("-fullGenLapack",n_modes)
    total_m=sum(MASSES)
    total_j=sum(POLAR)

    print("SPEAR EFCP MODAL CHARACTERIZATION")
    print("mode,T_s,MeffX_pct,MeffY_pct,MeffRz_pct,dominant")
    for mode,lam in enumerate(vals,1):
        T=2*math.pi/math.sqrt(lam)
        phix=[ops.nodeEigenvector(n,mode,1) for n in MASTERS]
        phiy=[ops.nodeEigenvector(n,mode,2) for n in MASTERS]
        phir=[ops.nodeEigenvector(n,mode,6) for n in MASTERS]

        Mn=sum(m*(x*x+y*y) + j*r*r
               for m,j,x,y,r in zip(MASSES,POLAR,phix,phiy,phir))
        Lx=sum(m*x for m,x in zip(MASSES,phix))
        Ly=sum(m*y for m,y in zip(MASSES,phiy))
        Lr=sum(j*r for j,r in zip(POLAR,phir))

        fx=(Lx*Lx/Mn)/total_m if Mn else 0.0
        fy=(Ly*Ly/Mn)/total_m if Mn else 0.0
        fr=(Lr*Lr/Mn)/total_j if Mn else 0.0
        parts={"X":fx,"Y":fy,"Rz":fr}
        dominant=max(parts,key=parts.get)
        print(f"MODECHAR Mode {mode}: T={T:.6f} s; "
              f"X={100*fx:.2f}%; Y={100*fy:.2f}%; Rz={100*fr:.2f}%; dominant={dominant}")

    print("REFERENCE: Stratan-Fajfar EFCP reports predominant M1=X, M2=Y, M3=Rz.")
    ops.wipe()

if __name__=="__main__":
    characterize()
