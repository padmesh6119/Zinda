# Zinda: Research Dossier (IBM Z Datathon 2026)

Compiled 2026-10-12 for team Espresso. Event: Oct 17–18, 2026. Deadline per team chat: Oct 15.

**Evidence tags**
- **[V]** checked directly: data I downloaded and computed on, or a page I opened and read in full.
- **[S]** from search-result summaries of primary or secondary sources, or from reputable reporting. Open the source before quoting the exact wording on a slide.
- **[U]** unverified or open. Resolve before putting it on a slide.

---

## 0. Summary

1. **The harm is documented at state scale in India.**
   - Haryana: 2.77 lakh elderly people and 52,479 widows were declared dead and lost their pensions after 2020 [S].
   - Rajasthan: 13.54 lakh of 90.98 lakh pensions were cancelled [S].
   - Telangana: a Supreme Court-ordered re-check found **at least 7.5%** of cancelled food cards had been cancelled wrongly [S].
2. **The national pipeline that causes it is public.** UIDAI has deactivated **over 2.5 crore** Aadhaar numbers of deceased people (Lok Sabha, 4 Feb 2026) [S]. It marks a record as dead on a **≥90% name match + 100% gender match + no biometric use after the death date** [V, as reported by MediaNama].
3. **The rule can be tested on real Indian data.** In the TCPD files, "Kalyanasundaram R" vs "KALYANASUNDARAM S." match 100% on name and gender, yet they are two different people. In Tamil naming, the initial is the father's name.
4. **Real labelled Indian matching data is on disk.** It comes from 18 TCPD election files: 110,709 people, 54,229 same-person pairs, 26,273 of them with spelling variation (Section 6). **The labels are human-reviewed clusters from TCPD's semi-automated Surf tool, not independent ground truth.** Describe them as "human-reviewed", never "ground truth" (6.1).
5. **Even with a unique ID, the US gets this wrong.** The US Social Security death file had **12,504 erroneous death entries out of 5.6 M in 2025 (0.22%)** [S, SSA Inspector General audit].
6. **The regulation behind the IBM Z story is real.** UIDAI Circular 14 of 2025 (4 Nov 2025) requires Aadhaar data in an Aadhaar Data Vault with keys in an HSM [S; open the PDF before quoting]. IBM Crypto Express cards are FIPS 140-2 Level 4 HSMs [S].
7. **The free LinuxONE environment is probably older hardware (a LinuxONE III / z15-generation machine).** If so, it has CPACF crypto and can run Snap ML, but **no on-chip AI accelerator**, which needs z16 or later [S/U]. Verify with `grep nnpa /proc/cpuinfo`.
8. **The judging criteria (from an aggregator)** are Technical Innovation, Enterprise Impact, Scalability, Solution Quality and Presentation [S]. Teams are 4–6 people [S]. The official rules page renders only in a browser [U].
9. **Past winners deployed a model on LinuxONE and hit endianness bugs**, because IBM Z is big-endian. Plan for it (Section 8.6).
10. **The novelty gap is real.** Existing tools match names. None decides when a death match is allowed to stop a payment, or ranks doubtful cases for limited field-check capacity.

---

## 1. Event facts

| Item | Value | Tag |
|---|---|---|
| Dates | 17–18 Oct 2026, 24 hours, virtual + 8 university sites | [S] starhacks, internshala |
| LinuxONE setup session | 16 Oct, 7:30 PM IST | [S] from teammate's research |
| Themes | Real-Time AI for Critical Decisions · AI Secured: Innovation Without Exposure · Wildcard: Beyond the Obvious | [S] |
| Judging | Technical Innovation, Enterprise Impact, Scalability, Solution Quality, Presentation | [S] HireToday aggregator |
| Team size | 4–6 (Internshala says 1–5; most sources say 4–6) | [S] |
| Prize pool | "$50K+" in most sources, "$30K+" in one | [S] |
| Registration window | One aggregator lists 19 Jun – 1 Oct 2026. Team registered on 28 Sep | [S] |
| Official rules | https://www.starhacks.org/ibmzdatathon-official-rule (JS-rendered; text not retrievable) | [U] |
| Recognition | IBM Z Day feature, IBM Z community spotlight | [V] starhacks page |
| Mini-challenge rubric (hack2skill) | problem understanding, technical implementation, AI quality, reliability and responsible AI. Described as a readiness signal, not the final score | [S] |

**Open:** someone must open the rules page in a browser and record (a) whether code written before the event is allowed, (b) the deliverables (video? repo? deck?), (c) any data or synthetic-data restrictions.

---

## 2. The problem: evidence of harm

### 2.1 India

| Case | What happened | Numbers | Tag | Source |
|---|---|---|---|---|
| **Haryana, Parivar Pehchan Patra (PPP)** | A family-ID database built from linked records marked people dead. Pensions stopped automatically and people had to prove they were alive | **277,115 elderly + 52,479 widows** declared dead and pensions stopped since 2020; "several thousands" were alive. 102-year-old Dhuli Chand staged a mock wedding to prove he was alive | [S] | [Al Jazeera, Jan 2024](https://www.aljazeera.com/economy/2024/1/25/in-india-an-algorithm-declares-them-dead-they-have-to-prove-theyre) |
| Haryana, field cases | Rohtak, Sonepat, Jhajjar: pensioners shown as dead. One man was marked dead together with his wife | about 3,000 stuck in Karnal from PPP errors | [S] | [Tribune](https://www.tribuneindia.com/news/haryana/errors-in-death-related-records-several-persons-denied-pension-for-months-431501), [Tribune Karnal](https://www.tribuneindia.com/news/haryana/errors-in-family-ids-add-to-woes-of-3k-pension-beneficiaries-433529) |
| Haryana, how it gets fixed | Ram Chander and Ompati (both 60) were marked dead in Mar 2022. A notarised affidavit fixed PPP, but the error persisted in a second database. Pension resumed after about 6 months | n/a | [S] | Al Jazeera |
| **Rajasthan** | Pensions cancelled for "death or migration" after mandatory eKYC (Dec 2022) | **13.54 lakh of 90.98 lakh** pensions cancelled | [S] | [ThePrint](https://theprint.in/ground-reports/rajasthans-elderly-are-victims-of-digital-murder-ekyc-gaps-leave-lakhs-without-pension/2347032/), [Pulitzer/The Wire](https://pulitzercenter.org/stories/companies-gain-elders-lose-rajasthans-turn-cradle-grave-digital-governance) |
| Rajasthan 2015 | An Aadhaar-seeding drive removed 7 lakh people, including 2.97 lakh "dead". A Dainik Bhaskar door-to-door survey found most were alive | 2.97 lakh | [S] | [Scroll](https://scroll.in/article/813132/rajasthans-living-dead-thousands-of-pensioners-without-aadhaar-or-bank-accounts-struck-off-lists) |
| **Telangana, Samagra Vedika** | Commercial "entity resolution" linked welfare claimants to car and property records. Syed Ali (a rickshaw puller) was confused with Syed Hyder Ali (a car owner) | 1.86 M food cards cancelled 2014–19. The Supreme Court (Apr 2022) ordered re-verification of 1.9 M; of 205,734 processed, **15,471 were approved, so at least 7.5% were wrong** | [S] | [Al Jazeera](https://www.aljazeera.com/economy/2024/1/24/how-an-algorithm-denied-food-to-thousands-of-poor-in-indias-telangana) |
| Telangana, official claim | The government claimed errors under 5% and a 95% filter rate | n/a | [S] | same |
| **Tamil Nadu SIR 2025–26** | Voter-roll revision deletions, aggregate by constituency | **97.38 lakh deleted**: 26.95 lakh "deceased", 66.45 lakh shifted/absent, 3.98 lakh duplicates, across 234 constituencies | [V] computed from OpenCity CSV (source elections.tn.gov.in) | `/tmp` copy, see 6.4 |

> Pitch note: Telangana is the closest analogue. It is the same technology (fuzzy entity resolution across government databases) causing the same failure (a confident wrong match against a poor person). And the Supreme Court has already forced a field re-verification, which is exactly the step Zinda inserts before a payment stops.

### 2.2 National scale

| Fact | Value | Tag | Source |
|---|---|---|---|
| Aadhaar numbers of deceased people deactivated | **> 2.5 crore** (written Lok Sabha reply, 4 Feb 2026) | [S] | [UIDAI PDF](https://uidai.gov.in/images/Over_25_Crore_Aadhaar_Numbers_of_Deceased_Persons_Deactivated_to_Prevent_Identity_Fraud.pdf), [Business Standard](https://www.business-standard.com/india-news/uidai-deactivates-aadhaar-numbers-deceased-prevent-identity-fraud-126020401231_1.html) |
| Earlier milestone | 1.17 crore deactivated (Jul 2025) from 1.55 crore CRS death records from 24 States/UTs | [S] | [Outlook Business](https://www.outlookbusiness.com/news/uidai-deactivates-117-crore-aadhaar-ids-targets-misuse-of-deceased-persons-identity) |
| Death registration coverage (CRS 2023) | 97.2% of deaths registered; 8.66 M deaths; 19 States/UTs at 100% | [S] | [Vision IAS summary of CRS 2023](https://visionias.in/current-affairs/news-today/2025-10-14/society/vital-statistics-of-india-based-on-civil-registration-system-crs-report-2023-released) |
| Digital life certificates (Jeevan Pramaan) FY25-26 | about 1.90 crore DLCs, about 1.15 crore by face authentication, 14.16 lakh from people aged 80+ | [S] | [Outlook Money](https://www.outlookmoney.com/retirement/digital-life-certificate-over-14-million-super-seniors-generated-online-jeevan-pramaan-patra-in-fy25-26) |
| NSAP pensions | District-wise old-age, widow and disability counts published (AIKosh) | [S] | [AIKosh](https://aikosh.indiaai.gov.in/home/datasets/details/district_wise_pension_data_under_the_national_social_assistance_programme_nsap_1.html) |

### 2.3 International analogues (why this is a known, hard problem)

| Country | Fact | Tag | Source |
|---|---|---|---|
| USA (SSA Death Master File) | CY2025: 5.6 M death records posted, **12,504 later found erroneous (0.22%)**, roughly the same rate as 2007–10 (about 12,000/yr). Causes include mistyped SSNs and wrong reports from relatives, banks and agencies | [S] | [SSA OIG, Jul 2026](https://oig.ssa.gov/assets/uploads/2026-july-numident-death-entry.pdf), [OIG 2011 summary](https://oig-files.ssa.gov/audits/summary/html/A-06-09-29095.html) |
| UK (Tell Us Once) | One death report is shared with DWP, HMRC and councils. The Jodey Whiting inquiry found DWP had no process or timescale for acting on these notifications | [S] | [AccessAble](https://www.accessable.co.uk/articles/jodey-whiting-dwp-continued-to-phone-woman-who-took-her-own-life-inquiry-finds) |

> Pitch line: "The US has a unique 9-digit ID and still wrongly kills about 12,500 people a year on paper. India matches on names, at 90%."

---

## 3. How the system works today

### 3.1 UIDAI deactivation pipeline (Aug 2023 guidelines, as reported) [S]
1. Death records from the Civil Registration System are matched against the Aadhaar database.
2. A record is marked for deactivation if **name match ≥ 90%** and **gender match = 100%**.
3. Final check: no biometric authentication after the recorded death date. If there was activity, further verification follows.
4. If a deactivated Aadhaar is later used, the person is told to visit a centre for biometric re-verification.
5. A "Reporting of Death" option on myAadhaar is integrated with 25 States/UTs.

Source: [MediaNama, Feb 2026](https://www.medianama.com/2026/02/223-uidai-deactivates-25-million-deceased-aadhaar/). **[U]** I didn't find the primary Aug 2023 guideline. Cite MediaNama as the source.

**What this means for Zinda:** reproduce rule step 2 as **Baseline B1** (see 7.4). It uses no age, no relative's name, no initials, and no evidence of being alive except biometric use, which many elderly pensioners don't have.

### 3.2 Pension side
- **Jeevan Pramaan:** the pensioner proves they're alive once a year (biometric or face). The burden is on the pensioner. It doesn't question an incoming death record [S].
- **State schemes** (e.g. Rajasthan SSP, Haryana PPP) cancel payments from database flags. Restoration requires an affidavit and office visits; reported delays run 6+ months [S].

### 3.3 Courts
- Pension is treated as **property under Article 300-A**. Delayed or arbitrary stoppage has drawn interest (6–10%) and costs in High Court and Supreme Court rulings [S]: [LiveLaw](https://www.livelaw.in/amp/high-court/punjab-and-haryana-high-court/punjab-haryana-high-court-imposes-cost-on-itself-for-delay-in-issuing-pension-neither-judicial-officer-nor-his-family-after-his-death-treated-with-dignity-286127), [gconnect](https://www.gconnect.in/judgements/widow-wins-pension-battle-court-orders-interest-and-costs.html).
- In the Telangana Samagra Vedika case (SQ Masood / ASEEM), the Supreme Court ordered field verification of 1.9 M deleted cards [S].
- **[U]** I found no specific judgment on old-age pensions stopped by a wrongful death declaration. Search Indian Kanoon for "declared dead" + "old age pension" before claiming one.

---

## 4. Existing solutions and the gap

| System / tool | What it does | What it doesn't do | Tag |
|---|---|---|---|
| UIDAI death deactivation | Name ≥90% + gender match + biometric-activity check | No relative or initial logic; no ranked review; acts first, fixes after | [S] |
| Jeevan Pramaan | Pensioner proves they're alive | Never questions the death record; burden on the elderly | [S] |
| myAadhaar death reporting | Family reports a death | A new source of wrong reports (cf. SSA) | [S] |
| Haryana PPP | Family-level database linkage plus "logic-based AI" | Opaque; RTI requests unanswered; no review before stopping | [S] |
| Telangana Samagra Vedika | ML entity resolution across databases | High-precision claims disproven by the court-ordered re-check | [S] |
| UK Tell Us Once | One report shared with all departments | Operational gaps (Whiting inquiry); no checks for false deaths found | [S] |
| Splink (UK Ministry of Justice) | Open-source probabilistic record linkage (Fellegi-Sunter, unsupervised training, term-frequency adjustment, DuckDB/Spark) | A general tool; doesn't decide whether a payment should stop | [S] [gov.uk](https://www.gov.uk/government/publications/joined-up-data-in-government-the-future-of-data-linking-methods/splink-mojs-open-source-library-for-probabilistic-record-linkage-at-scale) |
| Commercial Indian KYC name match (Cashfree, HyperVerge, Informatica India rules) | Handle initials, name order, S/O, transliteration | Single comparisons for verification, not welfare decisions | [S] |
| NIC custom Soundex for Indian names | Phonetic matching | Same | [S] [GJEIS](https://gjeis.com/index.php/GJEIS/article/view/349) |
| 2022 Springer paper: India-centric DeepMatcher de-duplication | Regional name conventions | Research only; data not public | [S] |

**Zinda's claimed novelty:** a **decision layer** that turns a match probability plus independent signs of life into pay / verify / stop, with **ranked field-check queues under a fixed weekly budget**. It's measured against the actual government rule on real Indian names.

---

## 5. Legal and regulatory

| Instrument | Relevance | Tag |
|---|---|---|
| **UIDAI Circular No. 14 of 2025 (4 Nov 2025)** | Aadhaar numbers and linked data must sit in an **Aadhaar Data Vault (ADV)**, on-premises or on a MeitY-empanelled government cloud, with keys in an HSM. It supersedes the 2017 circular and Circular 8/2025 | [S] [PDF](https://www.uidai.gov.in/images/Circular-No.14_of-2025.pdf) |
| ADV FAQs (3 Nov 2025) | Implementation details | [S] [PDF](https://www.uidai.gov.in/images/FAQs_Aadhaar_Data_Vault_03112025_v10.pdf) |
| HSM standard | Secondary sources say FIPS 140-2 Level 3 minimum, and that hashed Aadhaar numbers may no longer serve as reference keys | [U] confirm in the circular PDF |
| **DPDP Act 2023 + Rules 2025** (G.S.R. 846(E), 13 Nov 2025) | State processing for subsidies and benefits is covered by Rule 5 and Schedules 2 and 7. Sections 7 and 17 exemptions for the State are broad | [S] [MediaNama](https://www.medianama.com/2025/11/223-dpdp-framework-personal-data-companies-door-open-for-state/) |
| Article 300-A | Pension is property; stopping it requires authority of law | [S] |

**How to use this in the pitch:** "Zinda is built to sit inside the Aadhaar Data Vault model: narrow yes/no queries, no copying of profiles, every query logged." Don't claim DPDP compliance, only that the design minimises data use.

---

## 6. Data inventory

All paths are relative to `~/Projexts/zinda-data/`.

### 6.1 Real Indian labelled matching data: TCPD election candidates [V]
Source: Trivedi Centre for Political Data (Ashoka University) files with the `pid` person identifier, mirrored on data.opencity.in. lokdhaba.ashoka.edu.in refused HTTPS connections from this machine.

| File | Rows | Coverage |
|---|---|---|
| `raw/karnataka_tcpd_ae.csv` | 23,719 | Karnataka assembly elections 1978–2023 (38 elections incl. by-polls); 18,081 people; 2,426 in 2+ elections; 11,689 same-person pairs (6,210 spelled differently); age 42% filled |
| `raw/tcpd/ls-2019.csv` | 91,669 | **All Lok Sabha general elections 1962–2021, plus 2,818 by-election rows** (`Poll_No` > 0, hence 52 distinct years). Every row is `Election_Type = Lok Sabha Election (GE)`, 40 states/UTs. Mislabelled "parliamentary-elections-2019" on OpenCity; no Age column |
| `raw/tcpd/tn-2011/2016/2021*.csv` | 2,764 / 3,988 / 4,232 (+ summaries) | Tamil Nadu assembly |
| `raw/tcpd/maharashtra-2014/2019*.csv`, `telangana-2014/2018*.csv`, `delhi-2015/2020.csv`, `karnataka-2018.csv` | 300–4,400 each | Single elections |

**Combined (deduplicated on pid + year + constituency + name):**
- 136,530 rows; **110,709 people**; **14,072 in 2+ elections**
- **54,229 same-person pairs**, **26,273 with spelling variation**
- Age filled 22.4%
- People by state: Karnataka 21.1k, Tamil Nadu 14.8k, UP 14.6k, Maharashtra 13.3k, Bihar 7.7k, AP 5.2k, MP 5.1k, Telangana 3.6k, Delhi 3.5k, WB 3.3k

**Training-pair sample built** (first two elections per person; negatives = same state, same surname token, different person):
- 8,285 positive pairs (spelling differs)
- 12,284 hard negative pairs

**Real error types found in the data:**

| Type | Example |
|---|---|
| Initials collapse | DESAI AYYAPPA BASAVARAJ → A.B. DESAI → DESAI AB |
| Transliteration | HUTCHAMASTHY GOWDA N. ↔ N. HUCHAMASTI GOWDA; KIRPA ↔ KRIPA; PRATHAP ↔ PRATAP |
| Initial position | N. PRAKASH ↔ PRAKASH.N |
| Initial typo | K.H. ↔ K.B. RAMAKRISHNAIAH |
| **Same name, different father (hard negative)** | Kalyanasundaram R ≠ KALYANASUNDARAM S.; K. N. NANJUNDAIAH ≠ R. NANJUNDAIAH |
| **Probable label error (father/son merged)** | pid AEKA1002: SHIVALINGAPPA PATIL NARIBOL (53 in 2004) → DODDAPPAGOUDA S. PATIL NARIBOL (36 in 2008) |

**How `pid` was assigned (this matters for every accuracy claim)** [S]:
- TCPD assigned person IDs with **Surf**, its own name-resolution tool: automated clustering (phonetic and edit-distance similarity tuned for Indian names) followed by **human review** that merges and splits clusters.
- Surf also uses gender, constituency, caste, age and **"streaks"** (the same person contesting consecutive elections).
- **It only suggests a match when at least one name token is identical.**
- Sources: [Surf](https://tcpd.ashoka.edu.in/surf/), [Surf paper page](https://tcpd.ashoka.edu.in/surf-an-entity-mapping-and-resolution-system-for-indian/), [Individual Incumbency Dataset](https://tcpd.ashoka.edu.in/incumbency-mapping/), [PCT codebook 2.1](https://lokdhaba.ashoka.edu.in/pct/data/2022Jan31PCTCodebook_2_1.pdf).

**What follows:**
1. **Wording:** say "agreement with TCPD's human-reviewed person clusters", not "ground truth". The circularity charge stays answered, because humans reviewed the clusters, but the claim is softer.
2. **Coverage bias:** same-person pairs with **no** shared token (every token spelled differently) are mostly missing. Report accuracy only on candidate pairs sharing at least one token, and say so.
3. **Leakage risk:** Surf used constituency continuity. **Don't use same-constituency as a matcher feature**, or the model learns TCPD's procedure instead of name matching. State and sex are acceptable; also report a "name-only" model.

**Limits:**
- Candidates are mostly male and politically active, not typical pensioners.
- No S/O or W/O field.
- `pid` labels aren't perfect (see the AEKA1002 father/son case above).
- Some elections appear in two files, which may slightly inflate pair counts.

**Licence:** TCPD content on OpenCity is listed under non-commercial, attribution, share-alike terms (CC BY-NC-SA 4.0 on at least one file) [S]. Cite *"TCPD Indian Elections Data v2.0, Trivedi Centre for Political Data, Ashoka University"*.

### 6.2 Real Indian name variants with death dates: Wikidata [V]
- `raw/wikidata_india_deceased_aliases.csv`: 6,679 rows, **4,379 Indian citizens who died on or after 1990**, with alias spellings, date of birth and date of death. CC0 licence.
- Examples: Zohra Sehgal ↔ Zohra Segal ↔ Zohra Mumtaz Sehgal; Zakir Hussain ↔ Zakir Allarakha Qureshi.
- Use: a small real "death list" for the demo and an extra test set.
- Caveat: aliases include titles ("Ustad", "Mar") and loosely related names. Filter them.

### 6.3 Real Indian transliteration: Aksharantar (AI4Bharat) [V]
- `raw/aksharantar/tam.zip`: Tamil, train JSON 542 MB, plus valid and test sets
- `raw/aksharantar/hin.zip`: Hindi, train JSON 191 MB
- 26 M pairs overall across 21 languages; open licence (IndicXlit). [Paper](https://arxiv.org/pdf/2205.03018)
- Use: generate spelling variants (several English spellings of one native-script word) and run a stress test of the matcher.

### 6.4 Aggregates (calibration and pitch), not person-level [V]
- **TN SIR additions/deletions by constituency:** 234 constituencies; deceased 26,94,672; shifted/absent 66,44,881; duplicates 3,98,278; total 97,37,831. Electors after SIR (Dec 2025): 5,43,76,756 across 234 constituencies, computed after dropping the "Grand Total" row. Deletions are therefore about 15% of the pre-SIR base (97.4 lakh ÷ (5.44 crore + 0.97 crore), ignoring additions). Source: [OpenCity](https://data.opencity.in/dataset/tamil-nadu-sir-voter-rolls-2026), from elections.tn.gov.in.
- OpenCity "voter roll" CSVs for Chennai and TN contain **counts only**. The Chennai Jan 2025 "PDF" is a 5-page Tamil press release. **No person-level voter data is available there.**
- `raw/loksabha_candidates.csv` (India Data Portal, 26,114 rows, 2009+, ODC-BY): **no pid**, so not usable for labels.

### 6.5 Confirmed available, not downloaded

| Dataset | Size | Labels | Use |
|---|---|---|---|
| North Carolina voter snapshots ([2024](https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20240101.zip) 1.22 GB, [2020](https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20200101.zip) 1.03 GB, statewide current 524 MB) [V] | millions | NCID voter ID (ground truth "may not be error-free" per the d-blink paper) | Large-scale benchmark |
| FEBRL 1–4 via `pip install recordlinkage` [S] | 1k–5k | `rec_id` | Sanity check |
| ABS synthetic census (dblink-experiments GitHub) [S] | mid | yes | Synthetic comparison |
| NSAP district-wise pensions (AIKosh) [S] | counts | n/a | Size the synthetic pension registers |
| CRS annual report 2022 ([PDF](https://dc.crsorgi.gov.in/assets/download/Annual-Reports/crs/2022.pdf)) [S] | counts | n/a | Death base rates per district |
| SRS abridged life tables ([lifetable.de](https://www.lifetable.de/File/GetDocument/data\IND\IND000020152019AU1.pdf)) [S] | rates | n/a | Age-specific mortality for the synthetic generator |
| MyNeta candidate pages ([myneta.info](https://www.myneta.info)) [S] | per candidate | S/O / W/O fields visible on pages | Relative-name feature; needs scraping, check terms |

### 6.6 Not available / dead ends
- Proprietary Indian KYC 50k pairs ([arXiv 2605.23597](https://arxiv.org/pdf/2605.23597)).
- India deduplication generator (MIT-WPU paper), not released.
- Person-level electoral rolls: captcha- and JS-gated, with garbled Tamil extraction. They also carry privacy and political risk. **Don't use them.**
- NEWS transliteration shared-task data, not fully public.

---

## 7. Methods

### 7.1 Framing
Zinda has three components:
- **Matcher:** P(same person | death record, pension record). Trained and tested on **real** data (6.1).
- **Evidence fusion:** P(death flag wrong | match probability, sign-of-life answers). Shown on **synthetic** registers, labelled as synthetic.
- **Queue:** expected harm under a weekly field-check budget, using decision logic only.

### 7.2 Matcher features
- Name: rapidfuzz `token_sort_ratio`, `partial_ratio`, Jaro-Winkler on the normalised full name.
- **Initials features (key for South India):** extract single-letter tokens and compare the sets. In Tamil convention the initial is the father's name, so mismatched initials with an identical given name is a strong "different person" signal.
- Token overlap (Jaccard), and the longest token matching exactly.
- Phonetic: a simple Indian-name normalisation (th→t, aa→a, sh/s, w/v, double letters collapsed) before comparing. Optional: an NIC-style Soundex.
- Age consistency: `|(age_b − age_a) − (year_b − year_a)|` when both ages are known; otherwise a missing-age indicator.
- Same state; same sex. **Not same-constituency**: Surf used constituency streaks to assign `pid`, so including it leaks TCPD's labelling procedure into the model (see 6.1).
- Training data: TCPD positives plus hard negatives (same surname token, same state), plus easy random negatives.

### 7.3 Model
- Gradient-boosted trees: Snap ML `BoostingMachineClassifier` on IBM Z, with scikit-learn `HistGradientBoostingClassifier` as fallback.
- Calibrate probabilities (isotonic regression or Platt scaling on a validation split).
- Splink (Fellegi-Sunter, unsupervised EM) is an optional comparison baseline [S].

### 7.4 Baselines (the headline chart)

| ID | Rule | Purpose |
|---|---|---|
| **B1** | **UIDAI rule:** name similarity ≥ 0.90 AND same gender | The current government practice |
| B2 | Exact normalised name + same gender | Naive |
| B3 | B1 + age consistency | Shows how much age alone adds |
| Z | Zinda matcher (calibrated GBT) | The contribution |

**Define the comparison pool first (blocking).** Without this, every precision and "per 10,000" number is meaningless, because hand-sampled negatives (12,284 vs 8,285 positives) are far more balanced than reality.
- **Blocking rule:** all pairs of records **within the same state** that **share at least one name token of 3+ letters**. This mirrors Surf's own "1 exact token" constraint and what a real death-to-pension matcher would compare.
- Generate **every** candidate pair under that rule for the held-out people. Positives = same `pid`, negatives = everything else in the pool.
- Report the pool size and positive rate explicitly ("N candidate pairs, p% true matches").

**Report, all on that pool:**
- precision, recall and F1 on held-out people;
- **false matches per 10,000 candidate pairs in the pool**;
- the **"living people wrongly stopped at the same catch rate"** figure: Z's false-positive count at B1's recall, on the same pool.

### 7.5 Evaluation protocol
- **Split by person (`pid`), not by pair.** Hold out 20% of people entirely.
- Report results by state (Tamil Nadu vs others) and by "initials present" vs "full names". That's the fairness and regional slice.
- **Wikidata as a second, independent test:** never trained on.
- **Aksharantar stress test:** report accuracy as the transliteration-noise level goes up.
- Synthetic registers: train on 3 of the 4 error types, test on the unseen 4th, to answer the "circular results" charge. Report as ranges.
- Calibration plot (reliability curve).

### 7.6 Queue
- Expected harm = P(flag wrong) × months unpaid × (optional vulnerability weight: age 80+, no other income). **Don't weight by pension amount**, because that favours richer pensioners.
- Compare against first-come-first-served and against "stop on any match" at a fixed number of field checks per week.

### 7.7 Privacy design notes
- **Avoid Bloom-filter privacy-preserving linkage.** Published attacks re-identify encoded values; up to 20.7% were re-identified 1-to-1 on North Carolina voter data without hardening [S] ([IJPDS](https://ijpds.org/index.php/ijpds/article/view/725), [Christen et al.](https://users.cecs.anu.edu.au/~christen/publications/vidanage2019icde.pdf)).
- Instead:
  - fuzzy matching only inside one protected service;
  - keyed HMAC for exact ID joins;
  - AES-GCM at rest;
  - registers answer yes/no plus a date range;
  - every query logged.
- Wording: "reduces exposure", never "unbreakable".

---

## 8. IBM Z platform

### 8.1 LinuxONE Community Cloud (L1CC)
- No-charge, 120-day virtual server; Red Hat, SUSE or Ubuntu [S] ([IBM Developer](https://developer.ibm.com/gettingstarted/ibm-linuxone)).
- Instances are now provisioned through Marist College [S] ([openSUSE wiki](https://en.opensuse.org/ZSystems/Community_cloud_access)).
- Community posts describe the hardware as **LinuxONE III** (z15 generation) [S]. If that's still true, there's **no Telum AI accelerator** (z16+), so Snap ML runs on the CPU. **[U]** Run on day one: `lscpu`, `grep -o nnpa /proc/cpuinfo`, `cat /proc/sysinfo | grep -i type`.
- Past datathon teams got Ubuntu with Docker and **pre-built images containing TensorFlow, PyTorch and scikit-learn** [S] ([Code Catalysts](https://community.ibm.com/community/user/blogs/christopher-eliot-hall/2024/04/10/ibm-z-datathon), [Team Oasis](https://community.ibm.com/community/user/blogs/akshata-pandit/2025/04/24/our-experience-using-ibm-linuxone-from-datathon-pa)).

### 8.2 CPACF (crypto built into every core)
- OpenSSL uses CPACF for AES and SHA automatically, with no configuration. Builds compiled with `no-asm` disable it [S] ([IBM docs](https://www.ibm.com/docs/en/linuxonibm/lxos/lxos_osl_lonz_support.html)).
- Since z14 / LinuxONE II there is one CPACF per core, so throughput scales with cores [S]. Python `cryptography` (built on OpenSSL) gets it automatically.
- Enabling requires feature code 3863 microcode (no charge). Check with `cat /proc/cpuinfo | grep features` (look for `msa`) or `icainfo` if libica is installed [S].
- **[U]** I found no published AES-GCM overhead numbers. Zinda's measurement (encryption on vs off, per decision) is original evidence.

### 8.3 Crypto Express HSM
- A tamper-responding HSM, **FIPS 140-2 Level 4**, partitionable into up to 85 domains (virtual HSMs). Current adapters are CEX8A/C/P on z16, z17, LinuxONE 4 and 5 [S] ([IBM docs](https://www.ibm.com/docs/en/linuxonibm/lxsw/lxsw_hsms.html)).
- Matches the HSM requirement in UIDAI Circular 14/2025. **Design only**: not available on L1CC.

### 8.4 Secure Execution for Linux
- Introduced with z15 / LinuxONE III. **No hardware admin, KVM code or KVM admin can read the guest's data** [S] ([IBM docs](https://www.ibm.com/docs/en/linuxonibm/ldva/ldva_c_secex.html)).
- Requirements: the KVM host in LPAR mode, kernel 5.7+, `prot_virt=1`. No live migration. Can use CEX8S domains on z16 / LinuxONE 4 [S].
- **Design only** for Zinda: the production answer to "what if the matching host is compromised?"

### 8.5 Snap ML on IBM Z
- s390x wheels are on PyPI, but numpy, scipy and scikit-learn must come from conda first (PyPI builds compile from source). `libgomp1` is required [S] ([docs](https://snapml.readthedocs.io/en/latest/installation.html)).
- zDNN (accelerator library) is supported. If it isn't auto-detected, set `SNAPML_ZDNN_LIB` or `LD_LIBRARY_PATH`. It's used only on z16+; on z15 Snap ML falls back to the CPU transparently [S] ([IBM](https://github.com/IBM/ibmz-accelerated-for-snapml)).
- The IBM Z Accelerated for Snap ML container needs IBM container-registry credentials [S].

### 8.6 Package and endianness gotchas
- **rapidfuzz:** PyPI **dropped s390x wheels from 3.14.3** [S]. Use Anaconda `main` (3.12.1 for linux-s390x) or `apt install python3-rapidfuzz` (Ubuntu/Debian s390x) [S]. jellyfish has no s390x wheel.
- **Endianness:** s390x is **big-endian**. Past winners got nonsense outputs from weights trained on x86 until they used endian-aware versions or re-saved the models [S]. For Zinda:
  - **train the GBT on the LinuxONE VM itself** (seconds), or
  - export portable formats (XGBoost JSON / ONNX / PMML, which Snap ML can import);
  - avoid pickles of numpy-heavy objects across architectures. **[U]** Test this.
- Install path: Miniconda s390x → `conda install numpy scipy scikit-learn pandas cryptography flask rapidfuzz` → `pip install snapml`.

---

## 9. What past winners did

| Team | Project | What stood out | Tag |
|---|---|---|---|
| Team Oasis (GAT Bengaluru) | Lake-encroachment detection from satellite and drone images (CNN, OpenCV) | Containerised; deployed on L1CC; fixed big-endian PyTorch issue; "near-zero latency" demo | [S] |
| Code Catalysts (2023 edition) | AI/ML solution on L1CC | Used pre-built Docker images; trained locally, deployed on L1CC; hit byte-order issue | [S] |

**Takeaways:**
- A real local problem.
- A working model deployed on LinuxONE.
- A short story about adapting to the platform.
- No elaborate cryptography needed to win, but a **measured** platform result sets you apart.

---

## 10. Judge Q&A prep

| Likely question | Answer, backed by this dossier |
|---|---|
| "Your data is synthetic." | The matcher is trained and tested on 54k real same-person pairs of Indian names from 60 years of election records, labelled by TCPD's human-reviewed matching, plus an independent Wikidata death-list test. Only the pension, death and ration registers are synthetic, because they're legally private (UIDAI Circular 14/2025). |
| "Isn't this just fuzzy matching?" | The matcher is one part. The contribution is the decision rule: when a match may stop a payment, using independent signs of life, plus a budgeted review queue. It's benchmarked against UIDAI's actual ≥90% name + gender rule. |
| "Why IBM Z?" | It's the platform for regulated identity data: CPACF encrypts every register at measured overhead (show the number); Crypto Express is a FIPS 140-2 L4 HSM matching the Aadhaar Data Vault requirement; Secure Execution is the production answer for a compromised host. Don't claim scale or speed beyond what's measured. |
| "Doesn't linking databases repeat Haryana and Telangana?" | Zinda never stops a payment on a match alone. It asks narrow yes/no questions, builds no profile, logs every query, sends doubtful cases to a human, and keeps paying while in doubt. Telangana's court-ordered re-check (7.5% wrong) is exactly the step we automate up front. |
| "Who uses it?" | State pension department (e.g. Rajasthan Social Justice and Empowerment); death feed from the State Registrar via CRS; field checks by the block development officer (BDO) or gram sabha. Pilot: one district in shadow mode for a month. |
| "How accurate is it?" | Quote only measured numbers: held-out-person precision and recall vs B1, and false matches per 10k. |
| "What about bias?" | Report by state and by initials-vs-full-name. Weight harm by months unpaid and vulnerability, not pension amount. |

---

## 11. Open items checklist

- [ ] Open the official rules in a browser: pre-event code allowed? deliverables? synthetic-data rules?
- [ ] Team locks Zinda (BatchGuard was still being considered on Oct 11).
- [ ] Request an L1CC VM now; record `lscpu`, `nnpa`, `msa`, RAM and distro.
- [ ] Install test on s390x: Miniconda, the conda packages, `pip install snapml`, rapidfuzz.
- [ ] Endianness test: train on the VM, or export to JSON/ONNX.
- [ ] Confirm the HSM FIPS level wording in the Circular 14/2025 PDF.
- [ ] Confirm the TCPD licence and citation text.
- [ ] Build the evaluation pool with the blocking rule in 7.4 before computing any precision number.
- [ ] Read the PCT codebook 2.1 PDF for the exact `pid` methodology wording to cite.
- [ ] Decide whether to download the North Carolina snapshots (2.2 GB) for large-scale numbers.
- [ ] Optional: scrape S/O / W/O for TN 2021 from MyNeta (check terms first).
- [ ] Find a court judgment specific to wrongful death declaration and old-age pension (Indian Kanoon).

---

## 12. Source index

**Event:** [starhacks](https://www.starhacks.org/ibm-z-datathon-2026) · [rules (JS)](https://www.starhacks.org/ibmzdatathon-official-rule) · [hack2skill](https://hack2skill.com/event/datathon-2026) · [HireToday](https://www.hiretoday.in/competitiondetails/40000079) · [Internshala](https://internshala.com/competitions/ibm-z-datathon-2026/)

**Harm (India):** [Al Jazeera Haryana](https://www.aljazeera.com/economy/2024/1/25/in-india-an-algorithm-declares-them-dead-they-have-to-prove-theyre) · [Al Jazeera Telangana](https://www.aljazeera.com/economy/2024/1/24/how-an-algorithm-denied-food-to-thousands-of-poor-in-indias-telangana) · [ThePrint Rajasthan](https://theprint.in/ground-reports/rajasthans-elderly-are-victims-of-digital-murder-ekyc-gaps-leave-lakhs-without-pension/2347032/) · [Pulitzer](https://pulitzercenter.org/stories/companies-gain-elders-lose-rajasthans-turn-cradle-grave-digital-governance) · [Scroll 2016](https://scroll.in/article/813132/rajasthans-living-dead-thousands-of-pensioners-without-aadhaar-or-bank-accounts-struck-off-lists) · [Tribune](https://www.tribuneindia.com/news/haryana/errors-in-death-related-records-several-persons-denied-pension-for-months-431501)

**National:** [UIDAI 2.5 crore](https://uidai.gov.in/images/Over_25_Crore_Aadhaar_Numbers_of_Deceased_Persons_Deactivated_to_Prevent_Identity_Fraud.pdf) · [MediaNama process](https://www.medianama.com/2026/02/223-uidai-deactivates-25-million-deceased-aadhaar/) · [CRS 2022](https://dc.crsorgi.gov.in/assets/download/Annual-Reports/crs/2022.pdf) · [Jeevan Pramaan stats](https://www.outlookmoney.com/retirement/digital-life-certificate-over-14-million-super-seniors-generated-online-jeevan-pramaan-patra-in-fy25-26)

**International:** [SSA OIG 2026](https://oig.ssa.gov/assets/uploads/2026-july-numident-death-entry.pdf) · [SSA OIG 2011](https://oig-files.ssa.gov/audits/summary/html/A-06-09-29095.html)

**Law:** [UIDAI Circular 14/2025](https://www.uidai.gov.in/images/Circular-No.14_of-2025.pdf) · [ADV FAQ](https://www.uidai.gov.in/images/FAQs_Aadhaar_Data_Vault_03112025_v10.pdf) · [DPDP Rules commentary](https://www.medianama.com/2025/11/223-dpdp-framework-personal-data-companies-door-open-for-state/)

**Data:** [OpenCity](https://data.opencity.in) · [TCPD](https://tcpd.ashoka.edu.in/?p=696) · [Aksharantar](https://arxiv.org/pdf/2205.03018) · [HF Aksharantar](https://huggingface.co/datasets/ai4bharat/Aksharantar) · [NC voter data](https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20240101.zip) · [Christen NCVR report](https://cs.anu.edu.au/people/Peter.Christen/publications/ncvoter-report-29june2014.pdf) · [d-blink](https://arxiv.org/pdf/1909.06039) · [SHRUG](https://devdatalab.medium.com/open-access-geospatial-data-for-india-b9dceb7196bb)

**Methods:** [Splink](https://www.gov.uk/government/publications/joined-up-data-in-government-the-future-of-data-linking-methods/splink-mojs-open-source-library-for-probabilistic-record-linkage-at-scale) · [Bloom cryptanalysis](https://users.cecs.anu.edu.au/~christen/publications/vidanage2019icde.pdf) · [Hardening eval](https://ijpds.org/index.php/ijpds/article/view/725) · [NIC Soundex](https://gjeis.com/index.php/GJEIS/article/view/349)

**IBM Z:** [CPACF/OpenSSL](https://www.ibm.com/docs/en/linuxonibm/lxos/lxos_osl_lonz_support.html) · [HSMs](https://www.ibm.com/docs/en/linuxonibm/lxsw/lxsw_hsms.html) · [Secure Execution](https://www.ibm.com/docs/en/linuxonibm/ldva/ldva_c_secex.html) · [Snap ML install](https://snapml.readthedocs.io/en/latest/installation.html) · [Snap ML accelerated](https://github.com/IBM/ibmz-accelerated-for-snapml) · [L1CC](https://developer.ibm.com/gettingstarted/ibm-linuxone) · [Code Catalysts blog](https://community.ibm.com/community/user/blogs/christopher-eliot-hall/2024/04/10/ibm-z-datathon) · [Team Oasis blog](https://community.ibm.com/community/user/blogs/akshata-pandit/2025/04/24/our-experience-using-ibm-linuxone-from-datathon-pa)
