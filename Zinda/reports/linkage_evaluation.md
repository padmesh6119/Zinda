# Zinda matcher evaluation

This report uses person-level 80/20 splits and reports TCPD and NCVoters independently.
Metrics refer only to the constructed candidate-pair pools; they are not pension-population accuracy estimates.

Split seed: `20261013`. Review budget: top 5% of each test pair pool.

| Dataset | Train pairs | Test pairs | Test positive rate | Exact name AP | Fuzzy 0.90 AP | Logistic AP | Logistic F1 | Logistic recall @ 5% review | Logistic precision @ 5% review | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TCPD (Indian election candidates) | 25,000 | 25,000 | 0.400 | 0.679 | 0.929 | 0.969 | 0.928 | 0.123 | 0.984 | 0.047 |
| NCVoters (North Carolina voter records) | 71,424 | 5,672 | 0.344 | 0.811 | 0.999 | 1.000 | 0.995 | 0.145 | 1.000 | 0.002 |

## Protocol and limitations

- TCPD negatives are hard negatives: different `pid`, same normalized state, and at least one shared name token of 3+ characters. Per-block candidate generation is capped, then negatives are sampled up to 1.5 per positive. Positive pairs are uniformly capped at 10,000 per split.
- NCVoters uses its supplied duplicate and non-duplicate pair files. Before evaluation, every positive pair was checked to share NCID and every negative pair to have different NCIDs.
- The model is logistic regression over fuzzy-name, token, initials, age, sex, and region agreement features. The decision threshold is selected on training data by F1; test labels are not used for threshold selection.
- Results are not comparable across datasets because their pair construction and class prevalence differ. Neither dataset represents pension beneficiaries.
- NCVoters contains identifiable public voter data and is covered by non-commercial-use terms. Raw files are locally ignored by Git and are not included in this report.
