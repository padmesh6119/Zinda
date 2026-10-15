# NCVoters pair construction audit

No row-level names or IDs are included.

Identity split: 5,353 train NCIDs and 1,339 test NCIDs; intersection: 0.

| Pair source | Pairs | Name ratio ≥ .90 | Token-sort ≥ .90 | Exact name | Shared token | Same region | Median ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| all provided duplicate pairs | 9,819 | 0.765 | 0.761 | 0.714 | 0.999 | 1.000 | 1.000 |
| all provided generated non-duplicate pairs | 98,142 | 0.000 | 0.000 | 0.000 | 0.026 | 1.000 | 0.341 |
| held-out provided duplicate pairs | 1,954 | 0.773 | 0.765 | 0.712 | 1.000 | 0.999 | 1.000 |
| held-out provided generated non-duplicate pairs | 3,718 | 0.000 | 0.000 | 0.000 | 0.028 | 0.998 | 0.340 |

## Interpretation

The identity split prevents records belonging to the same NCID from crossing train and test. However, the benchmark's generated non-duplicate pairs may be easier than difficult real-world collisions. If their name-similarity rates are far below those for duplicates, near-perfect NCVoters scores should not be presented as evidence of robust hard-negative discrimination. The next validation step is a separately constructed same-region, shared-token negative set.
