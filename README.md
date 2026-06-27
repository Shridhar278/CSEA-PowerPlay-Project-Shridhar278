# POWER PLAY — T20 Cricket Scheduling

> **CSEA — IIT Guwahati | Optimization Track | Hackathon Problem Statement**

---

(This(Readme.md) is a bit rushed (AI) due to approaching deadline)

## Overview

**POWER PLAY** is a combinatorial optimization problem centred on the scheduling of T20 cricket fixtures. Given a set of teams, venues, and temporal constraints, the objective is to construct a valid and optimal match schedule that satisfies all hard constraints while maximising performance under the defined soft criteria.

This repository contains the full solution submission for the CSEA IIT Guwahati Hackathon — Optimization Track.

**FINAL ANSWER PREVIEW** (from personal calculations...)

DataSet 1 | schedule1.json | 
Best Score | 38.362776074123964 Cr
Simulation time | 3279.949732 seconds
<img width="1918" height="334" alt="image" src="https://github.com/user-attachments/assets/ceae5e1a-da47-400e-852c-7b2cc8cadf88" />


DataSet 2 | schedule2.json | 
Best Score | 48.1349431800616 Cr
Simulation time | 2923.295274 seconds
<img width="1919" height="338" alt="image" src="https://github.com/user-attachments/assets/74d8aa4a-ea73-4135-8e7e-3b1d6ff38505" />

execute command: python main.py |- This runs the simulation and gives these answers

---

## Repository Structure

```
.
├── README.md               # This document
├── Presentation.docx        # Algorithm design & core decision path (detailed walkthrough)
├── schedule1.json          # Output schedule for Instance 1 (inst_1 dataset)
├── schedule2.json          # Output schedule for Instance 2 (inst_2 dataset)
├── inst_1/                 # Input dataset — Instance 1
└── inst_2/                 # Input dataset — Instance 2
├── loader.py               # loads & saves .json files
├── classes.py              # contains Team & Config classes
├── math_models.py          # contains all revenue & penalty functions
├── processor.py            # DFS search with priority handling to find best Schedules
├── main.py                 # the execution starts here
├── test.py                 # just an extra file separately test DFS for scheduling
└── plan.txt                # just running ideas & plans
```

---

## Quick Reference

| Resource | Description |
|---|---|
| `Presentation.docx` | Full documentation of the algorithmic approach and core decision logic |
| `schedule1.json` | Final answer for `inst_1` — directly consumable output |
| `schedule2.json` | Final answer for `inst_2` — directly consumable output |

> **Note:** For direct answer verification, refer to `schedule1.json` and `schedule2.json` for `inst_1` and `inst_2` datasets respectively.

---

## Details

| Name | Roll No. | Department  | Institute |
|---|---|---|---|
| Shridhar Sharma | 250101095 | CSE | IIT Guwahati |

---

## Acknowledgements

- **CSEA IIT Guwahati** — for organising the Optimization Track.

---
