"""Mass/gravity audit for MAE 04-03. No modal calibration."""
import math, json
from geometry_source import JOINTS, BEAMS, STORY_CENTERLINES, SLAB_THICKNESS
G=9.807; GAMMA=24.518 # kN/m3
FINISH=.5; LIVE=.6     # 0.3*2.0 kN/m2
# Plan boundary reconstructed from exterior beam centerlines, Fig 2.2.
POLY=[JOINTS[x] for x in ("C8","C7","C4","C2","C5")]

def polygon_props(p):
    A=cx=cy=0.
    for (x0,y0),(x1,y1) in zip(p,p[1:]+p[:1]):
        c=x0*y1-x1*y0; A+=c; cx+=(x0+x1)*c; cy+=(y0+y1)*c
    A*=.5; return abs(A),cx/(6*A),cy/(6*A)

def audit():
    A,cx,cy=polygon_props(POLY)
    slab=A*SLAB_THICKNESS*GAMMA
    imposed=A*(FINISH+LIVE)
    # This is intentionally only the slab + finish + reduced LL ledger.
    # Beam/column self-weight is kept separate until tributary allocation is source-reproduced.
    W=slab+imposed; M=W/G
    out={"status":"partial_mass_ledger_not_for_eigen",
      "plan_area_m2":A,"plan_centroid_m":[cx,cy],
      "slab_self_weight_kN":slab,"finish_plus_0p3LL_kN":imposed,
      "slab_service_seismic_weight_kN_per_floor":W,
      "slab_service_mass_t_per_floor":M,
      "excluded_pending":["beam self-weight","column self-weight","Fig 2.6 tributary allocation",
       "nodal condensation to beam-column connections","polar mass moment from nodal masses"]}
    print("JEONG_ELNASHAI_MASS_AUDIT",json.dumps(out))
if __name__=="__main__": audit()
