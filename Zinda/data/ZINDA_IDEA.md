# Zinda — Ghost Pensioner Detection for IBM Z Datathon 2026

**Team:** Espresso (Padmesh / Pontiff, Jeeva, Vishruth, Swetha)  
**Event:** IBM Z Datathon, Oct 17–18 2026 (24 hours)  
**Theme:** Social Good / Public Welfare

---

## The Problem

In India, government welfare pensions (old-age, widow, disability) are stopped automatically when a beneficiary's Aadhaar is deactivated due to a death record match. The matching rule is:

> Name match ≥ 90% **AND** gender match = 100% **AND** no biometric activity after the recorded death date.
> — UIDAI deactivation pipeline, Aug 2023 guidelines

> **Verification status (Oct 2026): unverified claim.** Do not present this threshold or attribution as an established UIDAI rule. UIDAI's public Circular 02/2025 describes validation/matching of death-registration details with registrar and Aadhaar databases, and a process for reactivating wrongly reported deceased cases; it does not establish this exact 90% + exact-gender + no-biometric rule. The product UI and current demo do not implement it.

This rule is fragile. Indian names are short, highly repeated, and written inconsistently across registries (transliteration noise, initials vs. full names, honorifics). The result is mass false-positive "digital deaths":

| Case | What happened | Scale |
|---|---|---|
| **Haryana, PPP scheme** | Family-ID database marked people dead; pensions stopped automatically | 277,115 elderly + 52,479 widows declared dead since 2020 |
| **Rajasthan** | Pensions cancelled for "death or migration" after mandatory eKYC | 13.54 lakh of 90.98 lakh pensions cancelled |
| **Telangana, Samagra Vedika** | Supreme Court ordered field verification; re-check found wrongly rejected beneficiaries | At least 7.5% wrongly rejected out of 1.9M deleted cards |
| **UIDAI (Feb 2026)** | Over 2.5 crore Aadhaar numbers deactivated as deceased | Baseline scale of the problem |
| **US SSA (2025, for comparison)** | 12,504 erroneous death entries out of 5.6M | 0.22% — and the US has a unique 9-digit SSN |

> **Pitch line:** "The US has a unique 9-digit ID and still wrongly kills ~12,500 people a year on paper. India matches on names at 90%."

People who are wrongly declared dead lose pensions, ration cards, and bank access. To get reinstated, they must prove they are alive — which often requires navigating bureaucracies they have no means or mobility to navigate.

---

## What Zinda Does

Zinda is a **probabilistic record linkage system with a field-check queue**. It does NOT stop payments. It **finds the suspicious matches that UIDAI's rule accepted**, ranks them by expected harm, and surfaces them for a human field-check.

Three components:

### 1. Matcher — P(same person | death record, pension record)
A trained classifier that produces a match probability for a death-record / pension-record pair. Trained on real Indian name data.

**Features:**
- `token_sort_ratio`, `partial_ratio`, Jaro-Winkler on normalised full name (rapidfuzz)
- **Initials features** (critical for South India): extract single-letter tokens; mismatched initials + identical given name = strong "different person" signal. In Tamil convention, the initial is the father's name.
- Token Jaccard overlap; longest exact-matching token
- Indian-name phonetic normalisation: `th→t`, `aa→a`, `sh/s`, `w/v`, doubled letters collapsed
- Age consistency: `|(age_b − age_a) − (year_b − year_a)|`; missing-age indicator flag
- Same-state flag; same-sex flag

**What is NOT a feature:** constituency — it would leak the labelling procedure from the training source.

### 2. Evidence Fusion — P(death flag wrong | match score, sign-of-life signals)
Combines the matcher score with lightweight "signs of life": Jeevan Pramaan (Digital Life Certificate) submission, recent DBT credit, recent biometric activity. Shown on **synthetic pension registers** (clearly labelled as such in the demo).

### 3. Queue — Expected Harm Prioritisation
Orders flagged records by expected harm = `match_uncertainty × monthly_pension_value × months_since_stoppage`. Field-check officers see a ranked list. No payment is stopped based on the model alone.

---

## Why the Baseline Is Beatable

**Baseline B1 = reproduce UIDAI's rule verbatim** (≥90% name, 100% gender, no biometric).

Zinda beats B1 by:
- Using more name features (initials, phonetic, token structure), not just a single fuzzy score
- Using age consistency, which B1 ignores
- Producing a calibrated probability instead of a binary flag

Expected improvement: more true positives caught (living people flagged by B1 who survive Zinda's threshold) and fewer false positives passed to the queue.

---

## Why IBM Z

| Feature | How Zinda Uses It |
|---|---|
| **CPACF** (hardware AES/SHA on every core) | All Aadhaar tokens and name hashes encrypted at rest and in transit with near-zero overhead |
| **Crypto Express HSM (FIPS 140-2 Level 4)** | Key for Aadhaar Data Vault held in HSM; matches UIDAI Circular 14/2025 requirement. *Design only — not on LinuxONE Community Cloud.* |
| **Snap ML on s390x** | Gradient-boosted classifier trained directly on the LinuxONE VM; no model serialisation or endianness conversion needed |
| **Secure Execution (SE)** | Matcher inference runs in an isolated memory region; the raw name strings never leave the enclave |
| **IBM Z RAS (fault isolation)** | Appropriate for a production government welfare system with continuous uptime requirements |

**LinuxONE Community Cloud note:** Probably LinuxONE III / z15 generation — no NNPA AI accelerator. Snap ML will use the CPU path (transparent fallback). Check with `grep nnpa /proc/cpuinfo`. Train on the VM to avoid any big-endian serialisation issues.

---

## Training Data

**Source:** TCPD (Trivedi Centre for Political Data) election candidate files, downloaded from OpenCity.  
**Path:** `~/Projexts/zinda-data/raw/tcpd/` (17 state CSV files + `karnataka_tcpd_ae.csv`)

| Stat | Value |
|---|---|
| People (unique `pid`) | ~110,709 |
| Same-person pairs (across elections) | ~54,229 |
| Pairs with spelling variants | ~26,273 |
| Positive pairs built | 8,285 |
| Hard negative pairs (same state, same surname token) | 12,284 |

Labels come from TCPD's Surf tool — automated clustering + human review. Say "human-reviewed" in demos, not "ground truth".

**Additional test sets:**
- `wikidata_india_deceased_aliases.csv` — 4,379 deceased Indians with multiple name spellings; entirely independent, never trained on
- `aksharantar/tam.zip` + `aksharantar/hin.zip` — transliteration noise stress test

---

## Evaluation Protocol

- **Split by `pid`**, not by pair. Hold out 20% of people entirely.
- Block evaluation pool: all same-state pairs sharing a name token of 3+ letters.
- Report by state slice (Tamil Nadu vs. others) and by initials-present vs. full-names-only.
- Wikidata as second independent test.
- Aksharantar stress test: accuracy vs. transliteration-noise level.
- Calibration plot (reliability curve).
- For synthetic register results: train on 3 of 4 error types, test on unseen 4th — answers the "circular" charge.

---

## Privacy / Compliance Design

- No pension beneficiary PII ever leaves the vault.
- The matcher receives only tokenised, hashed representations.
- Every query is logged (audit trail).
- Design follows UIDAI Circular 14/2025 (Aadhaar Data Vault + HSM).
- Claim: **"minimises data use"** — do NOT claim full DPDP compliance.

---

## What Zinda Is NOT

- Not a payment-stop system. A match alone never cancels a pension.
- Not a "fraud detection" product (framing is beneficiary protection).
- Not using UIDAI's live API or real Aadhaar data (uses publicly available election data for training).

---

## Open Items Before Build

- [ ] Check official rules page (starhacks.org/ibmzdatathon-official-rule) in a browser — pre-event code policy unclear
- [ ] Team locks Zinda as final pick
- [ ] LinuxONE VM set up; test `conda install rapidfuzz snapml`
- [ ] Confirm z15 vs. z16 generation: `grep nnpa /proc/cpuinfo`
- [ ] Build evaluation pool script + UIDAI-rule-vs-Zinda comparison on TCPD pairs

---

## Fallback

If Zinda is blocked (rules disallow pre-event code), fallback to **Borewell / Dry-Well Watch**: forecast groundwater depletion from CGWB data, rank villages, flag faulty sensors. Real public data, weaker IBM Z story.
