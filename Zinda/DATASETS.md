# Zinda dataset search

Last searched: 2026-10-13

## Recommendation

I found a publicly downloadable, ready-to-use real-person linkage benchmark: **NCVoters**, published by Hasso Plattner Institute. It includes 14,183 voter records, labeled duplicate pairs, and generated non-duplicate pairs. This is the strongest new dataset found for supervised record-linkage work, but it is North Carolina data, not Indian names or pension beneficiaries.

There is still no publicly downloadable, well documented Indian pensioner name-linkage dataset that I could verify. The best practical route is to train and test the matcher using multiple datasets with distinct roles:

1. Use TCPD candidate records already in `data/raw/` for India-specific training and holdout evaluation. They have person IDs for deriving pairs and Indian naming variation. Keep each person ID wholly inside one split.
2. Use NCVoters as the **additional real-world labeled benchmark** for general record-linkage behavior and a second supervised dataset if useful. Keep its records local and respect its non-commercial source restrictions; do not publish identifiable rows.
3. Use the 120 hand-labelled `indic-namematch` pairs as a small Indian-name stress test, not as the main training set.
4. Use FEBRL as a generic pipeline check and Aksharantar as a transliteration stress test. Neither proves performance on Indian pension records.
5. If feasible, request access to the NIC farmer / land-record matching data described below. It is the closest domain analogue, but I could not locate a public download.

Do not combine all these into one random train/test split. Report results by dataset and say clearly what each dataset can and cannot establish.

## Dataset inventory

| Dataset | What it contains | Relevance to Zinda | Access / license notes | Recommendation |
|---|---|---|---|---|
| **NCVoters / North Carolina Voter Registration benchmark** | Downloaded to `datasets/ncvoters/`. HPI's prepared sample based on the Nov. 6, 2018 North Carolina voter snapshot has **14,183 records**, a duplicate list with **9,819 entries**, and **98,142 generated non-duplicate pairs**. The prepared records have lowercasing and special-character cleanup. | Strongest newly found downloadable supervised record-linkage benchmark. It contains real names and record errors. The underlying voter identifier (NCID) provides the identity key used to derive matches. It can support pair-classification training and evaluation, but the population and names are not Indian. | Source page: [HPI dataset page](https://hpi.de/naumann/projects/repeatability/datasets/ncvoters-dataset.html). The source NC voter files are designated for **non-commercial use** in the dataset paper; verify terms before use. They contain identifiable people, so keep locally and do not put raw records in public demos or submissions. | **Use as the additional real labeled dataset**, subject to non-commercial use terms. Split by identity cluster, not pair, and report metrics separately from TCPD. |
| **TCPD election candidates** (already present) | Indian candidates across elections, with TCPD `pid` person identifiers; the local research dossier reports 110,709 people and 54,229 same-person pairs after deduplication. | Best available Indian labeled source for training name and demographic pair features. Repeated candidacies create spelling and formatting variants. | Local files are under `data/raw/`. Labels are TCPD Surf person clusters, a semi-automated process with human review; not independent ground truth. The dossier notes non-commercial / attribution / share-alike terms on at least one mirrored file; confirm each source file's license and cite it. | **Primary training data**, with pid-level split and caveats. Do not claim pensioner accuracy. |
| **NIC CoE-AI Name Matching Across Datasets** | A government AI proof of concept describes farmer name datasets and land-record datasets from Gujarat, Maharashtra, Odisha, and Uttar Pradesh; matching fields include geography and personal identity attributes. | Closest match to cross-registry welfare linkage in India. | NIC's page says the datasets were provided for the proof of concept; I found no public download or reuse license. Treat as access-restricted unless NIC confirms otherwise. [Project page](https://ai.nic.in/AI/NameMatchingCaseML). | **Request access** from NIC / CoE-AI; potentially strongest external validation if permission is granted. |
| **indic-namematch benchmark** | 120 hand-labelled person-name pairs, evenly split into match / non-match across 21 categories, including initials, transliteration, patronymics, honorifics, OCR noise, and common-name collisions. | Indian-specific independent stress test of name-only behavior. | Benchmark CSV and methodology are in the [public GitHub repository](https://github.com/kiranshivaraju/indic-namematch/tree/master/benchmark); project declares MIT license. Small and not suitable as the sole training set. | **Use as a held-out challenge set**, after checking there is no overlap with our examples or rules. Do not train on it and report it as independent test performance. |
| **FEBRL 1–4** | Synthetic person records with known duplicate links and generated errors; FEBRL4 has 5,000 original and 5,000 duplicate records. | Useful for verifying pair generation, calibration code, and generic linkage metrics. Its population and name conventions are not Indian. | Available through the Python Record Linkage Toolkit; see [dataset docs](https://recordlinkage.readthedocs.io/en/stable/ref-datasets.html). FEBRL software is under an open-source license; check the package and dataset notices when redistributing. | **Pipeline sanity check only**, not evidence about Indian performance. |
| **SPIDER** | 50,000 synthetic person records: 40,000 base and 10,000 controlled duplicates, with variations such as spelling, nicknames, and addresses. | May exercise multi-field linkage and the workflow at a larger size. Public docs do not establish an Indian name distribution. | Dataset is hosted on [Figshare](https://doi.org/10.6084/m9.figshare.29595599.v2); the GitHub documentation asks users to cite the dataset and paper. Verify the Figshare license before use or redistribution. | Optional synthetic scale test. Not Indian-specific and not a replacement for real labeled cases. |
| **Wikidata deceased aliases** (already present) | Deceased public figures with aliases and death dates. | Can provide alias and death-date examples for a demo or name-variant stress test. | Local file `data/raw/wikidata_india_deceased_aliases.csv`; research dossier says CC0. Alias rows do not automatically mean two records are the same person in a pension-record setting; titles and loose aliases need filtering. | Use for a carefully filtered **alias test/demo**, not representative training or error-rate claims. |
| **Aksharantar** (already present) | Transliteration pairs for Indian languages, including Tamil and Hindi. | Can generate controlled Romanization variants for stress testing. | Local archives in `data/raw/aksharantar/`; dataset card / paper and archive license should be cited as specified by AI4Bharat. | Use for a separate transliteration stress test, not identity labels. |
| **SGER / Indian KYC pairs (paper only)** | A 2026 paper describes 20,000 curated training pairs and a 50,000-pair held-out evaluation set from production KYC records. | Excellent domain relevance, but the paper's evaluation is not an open benchmark we can run. | Its ethics section explicitly says the records are proprietary and drawn from anonymized platform KYC data. I found no released pair file. [Paper](https://arxiv.org/abs/2605.23597). | **Not available for our build.** Ask authors about access, but plan without it. Do not repeat the paper's scores as our results. |
| **DataTrapture synthetic India KYC** | Vendor advertises synthetic Indian person/KYC data and answer keys, with a 10-row demo bundle and paid full catalog. | Could be tailored to KYC fields and labels, if answer keys cover cross-record identity pairs and licensing permits use. | [Vendor demo page](https://datatrapture.com/demo); full access appears commercial. Claims and license need independent review. | Not a core benchmark unless the team obtains the full data, confirms labels, license, and rules allow it. |

## What I ruled out

- UIDAI's public developer pages provide **test identities** for exercising authentication APIs, not a labeled record-linkage dataset. They are not appropriate for training a matcher.
- Naamapadam and HiNER label person-name mentions in text (NER); they do not label whether two identity records refer to one person.
- Generic business entity-resolution datasets, including Indian business listings, concern companies rather than people and should not be used to claim person-matching performance.

## Suggested evaluation protocol

1. Deduplicate source rows, then split TCPD by `pid` before creating pair samples. Avoid leakage through a person's other election rows.
2. Create positives only from separate records under the same `pid`; include both exact and variant-name pairs, but report the strata separately.
3. Create hard negatives from different `pid`s sharing state and at least one common name token. Include same-name/different-person examples. Keep easier random negatives out of the headline score because they inflate performance.
4. Compare against at least two simple baselines: exact normalized name + gender, and a single fuzzy-name threshold. Evaluate precision, recall, PR-AUC, calibration, and recall at a fixed review-queue size.
5. Hold out the `indic-namematch` benchmark and report per-category errors. Its small size means the numbers are descriptive, not a stable population estimate.
6. Keep synthetic pension registers separate. They can demonstrate sign-of-life evidence fusion and queue behavior, but cannot establish real-world pension error rates.
7. Record provenance, licenses, filters, and pair construction for every source. Do not collect or use real Aadhaar or beneficiary data without explicit authorization.

## Source links

- [NIC CoE-AI: Name Matching Across Datasets](https://ai.nic.in/AI/NameMatchingCaseML)
- [HPI NCVoters prepared benchmark and TSV downloads](https://hpi.de/naumann/projects/repeatability/datasets/ncvoters-dataset.html)
- [North Carolina State Board of Elections voter registration snapshots](https://www.ncsbe.gov/results-data/voter-registration-data)
- [Paper describing the large NC voter-derived linkage benchmark](https://wolle.science/publications/wingerath-2021-edbt-duplicate-detection-data.pdf)
- [indic-namematch benchmark and code](https://github.com/kiranshivaraju/indic-namematch)
- [Python Record Linkage Toolkit dataset documentation](https://recordlinkage.readthedocs.io/en/stable/ref-datasets.html)
- [SPIDER dataset documentation and Figshare DOI](https://github.com/Praveenc1988/spider-entity-resolution-dataset)
- [SGER paper on arXiv](https://arxiv.org/abs/2605.23597)
- [DataTrapture demo bundle](https://datatrapture.com/demo)
- [AI4Bharat Aksharantar paper](https://arxiv.org/abs/2205.03018)
