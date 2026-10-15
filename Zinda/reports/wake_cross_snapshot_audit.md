# Wake County cross-snapshot sample audit

Aggregate counts only; no row-level identifiers or personal details are included.

Older HPI sample date: Nov 6, 2018. Newer county file last modified: Oct 12, 2026.
HPI Wake rows: 1,728; distinct NCIDs: 1,402.
Current Wake rows scanned: 1,007,349.
Older sample NCIDs found in current Wake: 510; not found: 892.

## Administrative status/reason counts among the overlapping sample

| Status | Reason | Count |
|---|---|---:|
| A (ACTIVE) | A2 (CONFIRMATION PENDING) | 4 |
| A (ACTIVE) | AP (VERIFICATION PENDING) | 1 |
| A (ACTIVE) | AV (VERIFIED) | 405 |
| I (INACTIVE) | IN (CONFIRMATION NOT RETURNED) | 20 |
| I (INACTIVE) | IU (CONFIRMATION RETURNED UNDELIVERABLE) | 6 |
| R (REMOVED) | RD (DECEASED) | 18 |
| R (REMOVED) | RF (FELONY CONVICTION) | 1 |
| R (REMOVED) | RH (MOVED WITHIN STATE) | 2 |
| R (REMOVED) | RL (MOVED FROM COUNTY) | 13 |
| R (REMOVED) | RM (REMOVED AFTER 2 FED GENERAL ELECTIONS IN INACTIVE STATUS) | 31 |
| R (REMOVED) | RQ (REQUEST FROM VOTER) | 1 |
| R (REMOVED) | RS (MOVED FROM STATE) | 8 |

## Limits

This is a sample-continuity audit, not an end-to-end deletion-detection evaluation. An older ID absent from the current Wake file may have moved counties, been removed, or otherwise changed. NCSBE status and reason codes are administrative labels, not independent confirmation that an action was correct or wrongful. The 2018 HPI sample is only a small subset of the earlier roll.
