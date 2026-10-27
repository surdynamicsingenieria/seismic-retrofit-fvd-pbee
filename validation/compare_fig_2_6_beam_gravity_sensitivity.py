"""Compare the non-accepted Fig. 2.6 beam-gravity sensitivity to Fig. 2.8."""
import csv, json
from collections import defaultdict
from pathlib import Path

ROOT = Path("results/SPEAR/jeong_elnashai")
SENS = ROOT / "sensitivity/fig_2_6_beam_gravity"

def read(path, curve=None):
    out=[]
    for r in csv.DictReader(path.open()):
        if curve is None or r.get("curve") == curve:
            out.append((abs(float(r["top_displacement_mm"])), abs(float(r["base_shear_kN"]))))
    return sorted(out)

def interp(a,x):
    for (x0,y0),(x1,y1) in zip(a,a[1:]):
        if x0 <= x <= x1: return y0+(y1-y0)*(x-x0)/(x1-x0)
    return None

rows=[]
for case in ("xp100","xn100","yp100","yn100"):
    ref=read(ROOT/"reference/fig_2_8_digitized.csv",case)
    sim=read(SENS/f"pushover/{case}.csv")
    rp=max(ref,key=lambda p:p[1]); sp=max(sim,key=lambda p:p[1])
    row={"case":case,"reference_peak_kN":rp[1],"sim_peak_kN":sp[1],
         "peak_error_pct":100*(sp[1]-rp[1])/rp[1],"reached_mm":sim[-1][0]}
    for x in (20,40):
        yr,ys=interp(ref,x),interp(sim,x)
        row[f"secant_error_pct_at_{x}mm"]=100*(ys-yr)/yr
    rows.append(row)
(SENS/"comparison_summary.json").write_text(json.dumps(rows,indent=2)+"\n")
print(json.dumps(rows,indent=2))
