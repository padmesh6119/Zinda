# Indian name challenge evaluation

The source is a small, hand-authored synthetic challenge set. These metrics are descriptive and are not pension-population estimates.

Pairs: 120 (60 matches, 60 non-matches); unresolvable from names alone: 18.
Fixed decision threshold: 0.90. No benchmark labels were used for training.

| Matcher | AP | ROC AUC | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|---:|---:|
| fuzzy_ratio | 0.558 | 0.563 | 0.552 | 0.267 | 0.360 | 0.217 |
| exact | 0.626 | 0.633 | 0.944 | 0.283 | 0.436 | 0.017 |
| levenshtein | 0.695 | 0.638 | 0.694 | 0.417 | 0.521 | 0.183 |
| jaro_winkler | 0.714 | 0.670 | 0.607 | 0.567 | 0.586 | 0.367 |
| token_set | 0.765 | 0.728 | 0.829 | 0.567 | 0.673 | 0.117 |
| phonetic | 0.801 | 0.783 | 0.816 | 0.667 | 0.734 | 0.150 |
| hybrid | 0.836 | 0.834 | 0.776 | 0.750 | 0.763 | 0.217 |
| rarity_weighted | 0.846 | 0.847 | 0.905 | 0.633 | 0.745 | 0.067 |

## Category summary

Correct count at the same fixed threshold; categories with very few pairs are especially noisy.

| Category | Pairs | Matches | Fuzzy correct | Rarity weighted correct |
|---|---:|---:|---:|---:|
| common_name_collision | 5 | 0 | 4 | 4 |
| control_negative | 10 | 0 | 10 | 10 |
| control_positive | 10 | 10 | 6 | 10 |
| gender_variant | 4 | 0 | 2 | 4 |
| honorific_masking | 4 | 0 | 2 | 3 |
| honorific_suffix | 5 | 5 | 1 | 5 |
| initial_collision | 5 | 0 | 5 | 5 |
| initials_expanded | 7 | 7 | 0 | 1 |
| married_name_change | 4 | 4 | 0 | 0 |
| middle_name_dropped | 6 | 6 | 0 | 3 |
| ocr_noise | 5 | 5 | 4 | 1 |
| one_edit_apart | 8 | 0 | 4 | 7 |
| patronymic_convention | 5 | 5 | 0 | 2 |
| shared_common_surname | 5 | 0 | 5 | 5 |
| sibling | 8 | 0 | 4 | 8 |
| spacing_punctuation | 4 | 4 | 3 | 4 |
| spouse_shared_surname | 4 | 0 | 4 | 4 |
| subset_token | 3 | 0 | 3 | 3 |
| token_reorder | 6 | 6 | 0 | 6 |
| transliteration | 8 | 8 | 2 | 6 |
| transposed_different | 4 | 0 | 4 | 3 |
