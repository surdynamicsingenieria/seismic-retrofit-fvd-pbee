# SPEAR-M0 v1.0 — Model parameters

Status: **UNDER CONSTRUCTION — NOT PHYSICALLY VALIDATED**

| Parameter | Value | Unit | Source | State | Implementation |
|---|---:|---|---|---|---|
| Storeys | 3 | - | SPEAR published documentation | PUBLISHED | 3D model |
| Storey height | 3.00 each | m | Original SPEAR specimen documentation | PUBLISHED | z = 0,3,6,9 m |
| Slab thickness | 150 | mm | SPEAR documentation | PUBLISHED | rigid diaphragm; slab not shell-modelled |
| Columns C1-C5,C7-C9 | 250x250 | mm | SPEAR documentation | PUBLISHED | frame members |
| Column C6 | 250x750 | mm | SPEAR documentation | PUBLISHED | strong axis orientation to be verified against plan |
| Column reinforcement C1-C5,C7-C9 | 4Ø12 | - | SPEAR documentation | PUBLISHED | reserved for nonlinear fiber model |
| Column reinforcement C6 | 10Ø12 | - | original specimen documentation | PUBLISHED | reserved for nonlinear fiber model |
| Column transverse reinforcement | Ø8/250 | - | SPEAR documentation | PUBLISHED | reserved for nonlinear model |
| Beam nominal section | 250x500 | mm | SPEAR documentation | PUBLISHED | elastic baseline only; member-specific reinforcement required for nonlinear model |
| Beam stirrups | Ø8/200 | - | SPEAR documentation | PUBLISHED | reserved for nonlinear model |
| Concrete nominal f'c | 25 | MPa | original design/specimen | PUBLISHED | baseline material |
| Smooth reinforcing steel | fy to be model-specific | MPa | SPEAR documentation | PUBLISHED/CONFLICT | do not freeze nonlinear steel until source/model variant is selected |
| Floor 1 mass | 65.5 | t | EFCP/pre-test model | PUBLISHED | lumped rigid-diaphragm mass |
| Floor 2 mass | 65.5 | t | EFCP/pre-test model | PUBLISHED | lumped rigid-diaphragm mass |
| Roof mass | 64.1 | t | EFCP/pre-test model | PUBLISHED | lumped rigid-diaphragm mass |
| Polar mass moment floors 1-2 | 1254 | t m² | EFCP/pre-test model | PUBLISHED | diaphragm rotational inertia |
| Polar mass moment roof | 1196 | t m² | EFCP/pre-test model | PUBLISHED | diaphragm rotational inertia |
| CM floors 1-2 | (4.53, 5.29) | m | EFCP/pre-test model | PUBLISHED | master diaphragm node |
| CM roof | (4.57, 5.33) | m | EFCP/pre-test model | PUBLISHED | master diaphragm node |
| Modal targets EFCP | 0.559, 0.476, 0.385 | s | published reference | PUBLISHED | validation targets |
| Modal targets ETCP | 0.570, 0.484, 0.392 | s | published reference | PUBLISHED | secondary comparison |
| Staircase | omitted | - | SPEAR prototype definition | PUBLISHED | NOT APPLICABLE |
| Infill walls | omitted | - | SPEAR prototype definition | PUBLISHED | NOT APPLICABLE |
| Exact beam connectivity / member IDs | pending source lock | - | plan/reinforcement drawings | RECONSTRUCTED-PENDING | **validation blocker** |
| Member-specific beam longitudinal reinforcement | pending transcription | - | original drawings | PUBLISHED-PENDING-TRANSCRIPTION | **pushover blocker** |

## Modelling rule

No physical parameter may be silently tuned to match the target periods or pushover curves. Any change after a failed validation must identify the physical cause, source, and quantitative effect.
