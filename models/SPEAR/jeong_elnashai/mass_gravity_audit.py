"""Mass/gravity ledger for MAE 04-03. No modal calibration."""
import math, json
from geometry_source import JOINTS, BEAMS, STORY_CENTERLINES, SLAB_THICKNESS
G=9.807; GAMMA=24.518
FINISH=.5; LIVE_REDUCED=.6
POLY=[JOINTS[x] for x in ("C8","C7","C4","C2","C5")]

def polygon_props(p):
    A=cx=cy=0.
    for (x0,y0),(x1,y1) in zip(p,p[1:]+p[:1]):
        q=x0*y1-x1*y0; A+=q; cx+=(x0+x1)*q; cy+=(y0+y1)*q
    A*=.5; return abs(A),cx/(6*A),cy/(6*A)

def length(i,j):
    x0,y0=JOINTS[i]; x1,y1=JOINTS[j]; return math.hypot(x1-x0,y1-y0)

def audit():
    A,cx,cy=polygon_props(POLY)
    slab=A*SLAB_THICKNESS*GAMMA
    imposed=A*(FINISH+LIVE_REDUCED)
    # Beam web below 150-mm slab only: 250 x (500-150) mm, avoids slab double count.
    beam=sum(length(i,j)*.25*(.50-SLAB_THICKNESS)*GAMMA for _,i,j in BEAMS)
    # Three-metre storey columns: 8 regular 250x250 + C6 750x250.
    col=(8*.25*.25+.75*.25)*3.0*GAMMA
    W=slab+imposed+beam+col; M=W/G
    out={"status":"complete_weight_ledger_pending_nodal_allocation",
      "plan_area_m2":A,"plan_centroid_m":[cx,cy],
      "slab_self_weight_kN":slab,"finish_plus_0p3LL_kN":imposed,
      "beam_web_self_weight_kN":beam,"column_self_weight_kN":col,
      "seismic_weight_kN_per_typical_floor":W,"mass_t_per_typical_floor":M,
      "note":"column weight currently assigned wholly to the floor ledger; nodal allocation will split/storey-consistently before eigen",
      "pending":["Fig 2.6 tributary nodal allocation","nodal CM and polar mass moment","rigid offsets/C6 arms"]}
    print("JEONG_ELNASHAI_MASS_AUDIT",json.dumps(out))
if __name__=="__main__": audit()
