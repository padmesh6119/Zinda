# NCVoters record-linkage benchmark

Downloaded 2026-10-13 from the Hasso Plattner Institute dataset page:
<https://hpi.de/naumann/projects/repeatability/datasets/ncvoters-dataset.html>

## Files

- `ncvoters.tsv`: 14,183 voter records (14,184 lines including the header).
- `ncvoters_DPL.tsv`: 9,819 duplicate-list entries (9,820 lines including the header).
- `ncvoters_NDPL.tsv`: 98,142 generated non-duplicate pair entries (98,143 lines including the header).

The files are tab-separated. The record file includes names, age, sex, race/ethnicity, voter and registration identifiers, address, and other voter registration fields. HPI says the sample comes from the North Carolina voter registration snapshot dated 2018-11-06 and that it lowercases values and removes special characters. The provided pair lists are the linkage labels. The underlying North Carolina voter identifier (NCID) was used to identify voters across records.

## Use and handling

This is U.S. voter data, not an Indian or pension-beneficiary population. Use it to train or evaluate general record linkage behavior, and report it separately from TCPD results. Do not describe its results as validated on Indian pensioners.

The source paper states that North Carolina voter registration data are available for non-commercial use. The files contain identifiable records and sensitive demographic/address fields. Keep them local, restrict access to the project team, and do not publish the raw files or include personal records in a public demo/submission. Check the current HPI and North Carolina terms before redistribution or use outside this project.

## Sources

- Dataset page and file downloads: <https://hpi.de/naumann/projects/repeatability/datasets/ncvoters-dataset.html>
- North Carolina voter data terms and historical snapshots: <https://www.ncsbe.gov/results-data/voter-registration-data>
- Dataset paper, *Generating Realistic Test Datasets for Duplicate Detection at Scale Using Historical Voter Data*: <https://wolle.science/publications/wingerath-2021-edbt-duplicate-detection-data.pdf>
