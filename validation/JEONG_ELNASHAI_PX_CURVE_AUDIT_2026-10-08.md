# Jeong–Elnashai +X diagnostic curve audit — 2026-10-08

Source: GitHub Actions run 37862635015, artifact 11586856382, `pushover_px.csv` (481 rows, 480 steps), commit `0e76696d`.

- Peak positive base shear: **483.766 kN at 89.647 mm roof displacement**.
- Final: **449.536 kN at 119.897 mm**.
- Postpeak reduction from peak to last point: **7.08%**.
- Secant stiffness at 10 mm: **15.79 kN/mm** (interpolated).
- OpenSees completed 480/480 increments with 0 recovery attempts.
- Model has elastic T-beams, provisional column reinforcement, simplified tributary gravity. Thus this curve is **diagnostic only**; no Fig. 2.8 quantitative agreement can be claimed.
- The observed descending branch is not proof of physical strength degradation or the published first-story mechanism. P–Delta and column plasticity are present, but beam plasticity and validated hinge mechanisms are not.

**Next required checks:** published Fig. 2.8 xp100 curve digitization, member reinforcement schedule, Fig. 2.6 gravity allocation, mode shape participation and 4-direction independent pushover. Preserve source-lock; do not proceed to FVD/NLTHA/MSA/FEMA P-58.
