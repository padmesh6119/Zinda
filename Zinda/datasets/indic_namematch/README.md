# Indian name challenge dataset

This directory contains the 120-pair synthetic, hand-authored challenge set and the upstream `indic-namematch` matcher package used for a descriptive comparison. Source: [kiranshivaraju/indic-namematch](https://github.com/kiranshivaraju/indic-namematch), retrieved from its `master` archive on 2026-10-13. The repository declares MIT licensing; the license is included here.

The dataset has 60 matches, 60 non-matches, and 18 pairs marked unresolvable from names alone. It is a small adversarial challenge set, not a representative population sample. Do not use these pairs for model training and do not interpret its scores as pensioner accuracy.

Run `python3 evaluate_indic.py` from this directory to regenerate aggregate-only `evaluation.md` and `evaluation.json`. The report does not emit the names or rationales in the source CSV.
