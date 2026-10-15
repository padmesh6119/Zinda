#!/usr/bin/env python3
"""Evaluate Zinda name matching on TCPD and NCVoters without exporting PII."""

from __future__ import annotations

import itertools
import json
import math
import random
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz.distance import JaroWinkler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
SEED = 20261013
TEST_SIZE = 0.20
REVIEW_FRACTION = 0.05
TCPD_POSITIVE_PAIR_CAP = 10000
TOKEN_RE = re.compile(r"[^a-z0-9]+")
FEATURE_NAMES = [
    "name_exact",
    "name_ratio",
    "name_token_sort",
    "name_token_set",
    "name_jaro_winkler",
    "token_jaccard",
    "shared_token_count",
    "initial_coverage",
    "initial_conflict",
    "name_length_ratio",
    "length_difference",
    "age_difference",
    "age_present",
    "age_year_consistency",
    "sex_agree",
    "sex_present",
    "region_agree",
    "region_present",
]


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode().lower()
    return " ".join(TOKEN_RE.sub(" ", value).split())


def number(value: object) -> float:
    try:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return float("nan")
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def build_features(left: dict, right: dict) -> list[float]:
    a = left["_name"]
    b = right["_name"]
    ta = set(a.split()) if a else set()
    tb = set(b.split()) if b else set()
    inter = ta & tb
    union = ta | tb
    initials_a = {t for t in ta if len(t) == 1}
    initials_b = {t for t in tb if len(t) == 1}
    full_a = {t for t in ta if len(t) > 1}
    full_b = {t for t in tb if len(t) > 1}
    expanded_a = {t[0] for t in full_a}
    expanded_b = {t[0] for t in full_b}
    initials_coverage = 0.0
    if initials_a or initials_b:
        hits = len(initials_a & expanded_b) + len(initials_b & expanded_a)
        initials_coverage = hits / max(1, len(initials_a) + len(initials_b))
    initial_conflict = float(bool(initials_a and initials_b and not (initials_a & initials_b)))

    age_a, age_b = number(left.get("_age")), number(right.get("_age"))
    age_present = float(np.isfinite(age_a) and np.isfinite(age_b))
    age_diff = abs(age_a - age_b) if age_present else float("nan")
    year_a, year_b = number(left.get("_year")), number(right.get("_year"))
    if age_present and np.isfinite(year_a) and np.isfinite(year_b):
        age_year_consistency = 1.0 / (1.0 + abs((age_b - age_a) - (year_b - year_a)))
    else:
        age_year_consistency = float("nan")

    sex_a, sex_b = left.get("_sex", ""), right.get("_sex", "")
    sex_present = float(bool(sex_a and sex_b))
    sex_agree = float(sex_a == sex_b) if sex_present else float("nan")
    region_a, region_b = left.get("_region", ""), right.get("_region", "")
    region_present = float(bool(region_a and region_b))
    region_agree = float(region_a == region_b) if region_present else float("nan")
    max_length = max(len(a), len(b), 1)

    return [
        float(bool(a and a == b)),
        fuzz.ratio(a, b) / 100.0 if a and b else 0.0,
        fuzz.token_sort_ratio(a, b) / 100.0 if a and b else 0.0,
        fuzz.token_set_ratio(a, b) / 100.0 if a and b else 0.0,
        JaroWinkler.normalized_similarity(a, b) if a and b else 0.0,
        len(inter) / len(union) if union else 0.0,
        float(len(inter)),
        initials_coverage,
        initial_conflict,
        min(len(a), len(b)) / max_length,
        float(abs(len(a) - len(b))),
        age_diff,
        age_present,
        age_year_consistency,
        sex_agree,
        sex_present,
        region_agree,
        region_present,
    ]


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if "_entity" not in frame and "entity" in frame:
        frame["_entity"] = frame["entity"]
    frame["_name"] = (frame["name"].map(clean))
    frame["_sex"] = frame["sex"].map(clean)
    frame["_region"] = frame["region"].map(clean)
    frame["_age"] = frame["age"].map(number)
    frame["_year"] = frame["year"].map(number)
    return frame


def candidate_negatives(frame: pd.DataFrame, target: int, seed: int) -> list[tuple[int, int]]:
    """Sample same-region pairs sharing a name token; cap large blocks."""
    rng = random.Random(seed)
    buckets: dict[tuple[str, str], list[int]] = defaultdict(list)
    for idx, row in frame.iterrows():
        if not row["_name"]:
            continue
        for token in set(row["_name"].split()):
            if len(token) >= 3:
                buckets[(row["_region"], token)].append(int(idx))

    out: set[tuple[int, int]] = set()
    for members in buckets.values():
        members = list(dict.fromkeys(members))
        if len(members) < 2:
            continue
        combinations = len(members) * (len(members) - 1) // 2
        cap = min(combinations, 1000)
        if combinations <= 1000:
            pairs = itertools.combinations(members, 2)
        else:
            sampled = set()
            while len(sampled) < cap:
                a, b = rng.sample(members, 2)
                sampled.add((min(a, b), max(a, b)))
            pairs = sampled
        for a, b in pairs:
            if frame.at[a, "_entity"] == frame.at[b, "_entity"]:
                continue
            out.add((min(a, b), max(a, b)))

    candidates = list(out)
    if len(candidates) > target:
        candidates = rng.sample(candidates, target)
    return candidates


def tcpd_records() -> pd.DataFrame:
    files = sorted((ROOT / "data/raw/tcpd").glob("*.csv"))
    files.append(ROOT / "data/raw/karnataka_tcpd_ae.csv")
    fields = {"Candidate", "pid", "Age", "Sex", "State_Name", "Year", "Constituency_Name"}
    chunks = []
    for path in files:
        data = pd.read_csv(path, usecols=lambda col: col in fields, dtype={"pid": "string"}, low_memory=False)
        if not {"Candidate", "pid"}.issubset(data.columns):
            continue
        if "Age" not in data:
            data["Age"] = np.nan
        if "Sex" not in data:
            data["Sex"] = ""
        if "State_Name" not in data:
            data["State_Name"] = ""
        if "Year" not in data:
            data["Year"] = np.nan
        data = data[data.pid.notna() & (data.pid.str.strip() != "")]
        if "Constituency_Name" not in data:
            data["Constituency_Name"] = ""
        chunks.append(data[["Candidate", "pid", "Age", "Sex", "State_Name", "Year", "Constituency_Name"]])
    records = pd.concat(chunks, ignore_index=True)
    records = records.rename(columns={"Candidate": "name", "pid": "entity", "Age": "age", "Sex": "sex", "State_Name": "region", "Year": "year"})
    records["entity"] = records.entity.astype(str).str.strip()
    records = records.drop_duplicates(subset=["entity", "year", "Constituency_Name", "name"])
    records["row_id"] = np.arange(len(records), dtype=np.int64)
    return add_features(records.set_index("row_id", drop=False))


def build_tcpd_split(frame: pd.DataFrame, entities: set[str], split_seed: int) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    subset = frame[frame.entity.isin(entities)]
    positives: list[tuple[int, int]] = []
    for _, rows in subset.groupby("entity", sort=False):
        ids = rows.index.to_list()
        positives.extend(itertools.combinations(ids, 2))
    if len(positives) > TCPD_POSITIVE_PAIR_CAP:
        positives = random.Random(split_seed).sample(positives, TCPD_POSITIVE_PAIR_CAP)
    negatives = candidate_negatives(subset, max(1, int(len(positives) * 1.5)), split_seed)
    return positives, negatives


def ncvoter_records_and_pairs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    directory = ROOT / "datasets/ncvoters"
    records = pd.read_csv(directory / "ncvoters.tsv", sep="\t", dtype=str, keep_default_na=False)
    records = records.rename(columns={"id": "row_id", "ncid": "entity", "first_name": "first", "midl_name": "middle", "last_name": "last", "state_cd": "region"})
    records["name"] = records[["first", "middle", "last"]].agg(" ".join, axis=1)
    records["entity"] = records.entity.astype(str).str.strip()
    records["row_id"] = records.row_id.astype(str).str.strip()
    records["year"] = ""
    records["sex"] = records.sex_code
    records = add_features(records.set_index("row_id", drop=False))
    dpl = pd.read_csv(directory / "ncvoters_DPL.tsv", sep="\t", dtype=str).rename(columns={"id1": "left", "id2": "right"})
    ndpl = pd.read_csv(directory / "ncvoters_NDPL.tsv", sep="\t", dtype=str).rename(columns={"id1": "left", "id2": "right"})
    return records, dpl, ndpl


def make_feature_matrix(records: pd.DataFrame, pairs: list[tuple[str | int, str | int]]) -> pd.DataFrame:
    rows_by_id = records.to_dict(orient="index")
    rows = [build_features(rows_by_id[left], rows_by_id[right]) for left, right in pairs]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)


def score_predictions(y: np.ndarray, probability: np.ndarray, threshold: float) -> dict:
    prediction = probability >= threshold
    positives = int(y.sum())
    k = max(1, math.ceil(len(y) * REVIEW_FRACTION))
    top = np.argsort(-probability)[:k]
    top_hits = int(y[top].sum())
    return {
        "threshold": float(threshold),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "f1": float(2 * precision_score(y, prediction, zero_division=0) * recall_score(y, prediction, zero_division=0) / max(1e-12, precision_score(y, prediction, zero_division=0) + recall_score(y, prediction, zero_division=0))),
        "average_precision": float(average_precision_score(y, probability)),
        "roc_auc": float(roc_auc_score(y, probability)) if len(np.unique(y)) == 2 else None,
        "brier_score": float(brier_score_loss(y, probability)),
        "review_budget_fraction": REVIEW_FRACTION,
        "precision_at_review_budget": top_hits / k,
        "recall_at_review_budget": top_hits / max(1, positives),
        "predicted_positive_count": int(prediction.sum()),
    }


def train_and_evaluate(records: pd.DataFrame, train_pairs: list[tuple], test_pairs: list[tuple], dataset: str) -> dict:
    train_labels = np.asarray([label for _, _, label in train_pairs], dtype=np.int8)
    test_labels = np.asarray([label for _, _, label in test_pairs], dtype=np.int8)
    train_keys = [(a, b) for a, b, _ in train_pairs]
    test_keys = [(a, b) for a, b, _ in test_pairs]
    x_train = make_feature_matrix(records, train_keys)
    x_test = make_feature_matrix(records, test_keys)

    model = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
        StandardScaler(),
        LogisticRegression(max_iter=1000, random_state=SEED),
    )
    model.fit(x_train, train_labels)
    train_probability = model.predict_proba(x_train)[:, 1]
    precision, recall, thresholds = precision_recall_curve(train_labels, train_probability)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(1e-12, precision[:-1] + recall[:-1])
    learned_threshold = float(thresholds[int(np.argmax(f1))]) if len(thresholds) else 0.5
    model_probability = model.predict_proba(x_test)[:, 1]

    exact_probability = x_test["name_exact"].to_numpy(dtype=float)
    fuzzy_probability = x_test["name_ratio"].to_numpy(dtype=float)
    results = {
        "dataset": dataset,
        "train_pairs": int(len(train_labels)),
        "test_pairs": int(len(test_labels)),
        "train_positive_rate": float(train_labels.mean()),
        "test_positive_rate": float(test_labels.mean()),
        "baselines": {
            "exact_normalized_name": score_predictions(test_labels, exact_probability, 0.5),
            "fuzzy_ratio_ge_0.90": score_predictions(test_labels, fuzzy_probability, 0.90),
        },
        "logistic_regression": score_predictions(test_labels, model_probability, learned_threshold),
    }
    return results


def evaluate_tcpd() -> dict:
    records = tcpd_records()
    unique_entities = records.entity.drop_duplicates().to_numpy()
    train_entities, test_entities = train_test_split(unique_entities, test_size=TEST_SIZE, random_state=SEED)
    train_pos, train_neg = build_tcpd_split(records, set(train_entities), SEED)
    test_pos, test_neg = build_tcpd_split(records, set(test_entities), SEED + 1)

    rng = random.Random(SEED)
    train_pairs = [(a, b, 1) for a, b in train_pos] + [(a, b, 0) for a, b in train_neg]
    test_pairs = [(a, b, 1) for a, b in test_pos] + [(a, b, 0) for a, b in test_neg]
    rng.shuffle(train_pairs)
    rng.shuffle(test_pairs)
    result = train_and_evaluate(records, train_pairs, test_pairs, "TCPD (Indian election candidates)")
    result["records"] = int(len(records))
    result["entities"] = int(records.entity.nunique())
    result["train_entities"] = int(len(train_entities))
    result["test_entities"] = int(len(test_entities))
    result["train_positive_pairs"] = int(len(train_pos))
    result["train_hard_negative_pairs"] = int(len(train_neg))
    result["test_positive_pairs"] = int(len(test_pos))
    result["test_hard_negative_pairs"] = int(len(test_neg))
    result["hard_negative_definition"] = "Different TCPD pid, same normalized state, at least one shared name token of length >=3; at most 1,000 sampled candidates per state-token block; negatives sampled up to 1.5 per positive. Positive pairs are capped at 10,000 per split by uniform sampling when needed."
    return result


def evaluate_ncvoters() -> dict:
    records, dpl, ndpl = ncvoter_records_and_pairs()
    id_to_entity = records.entity.to_dict()
    positive_pairs = [(str(a), str(b)) for a, b in dpl[["left", "right"]].itertuples(index=False, name=None)]
    negative_pairs = [(str(a), str(b)) for a, b in ndpl[["left", "right"]].itertuples(index=False, name=None)]
    positive_valid = sum(id_to_entity.get(a) == id_to_entity.get(b) for a, b in positive_pairs)
    negative_valid = sum(id_to_entity.get(a) != id_to_entity.get(b) for a, b in negative_pairs)
    if positive_valid != len(positive_pairs) or negative_valid != len(negative_pairs):
        raise ValueError("NCVoters pair labels did not agree with NCID identity clusters")

    entities = records.entity.drop_duplicates().to_numpy()
    train_entities, test_entities = train_test_split(entities, test_size=TEST_SIZE, random_state=SEED)
    train_set, test_set = set(train_entities), set(test_entities)

    def partition(pairs: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        train, test = [], []
        for a, b in pairs:
            entity_a, entity_b = id_to_entity[a], id_to_entity[b]
            if entity_a in train_set and entity_b in train_set:
                train.append((a, b))
            elif entity_a in test_set and entity_b in test_set:
                test.append((a, b))
        return train, test

    train_pos, test_pos = partition(positive_pairs)
    train_neg, test_neg = partition(negative_pairs)
    train_pairs = [(a, b, 1) for a, b in train_pos] + [(a, b, 0) for a, b in train_neg]
    test_pairs = [(a, b, 1) for a, b in test_pos] + [(a, b, 0) for a, b in test_neg]
    random.Random(SEED).shuffle(train_pairs)
    random.Random(SEED + 1).shuffle(test_pairs)
    result = train_and_evaluate(records, train_pairs, test_pairs, "NCVoters (North Carolina voter records)")
    result["records"] = int(len(records))
    result["entities"] = int(records.entity.nunique())
    result["train_entities"] = int(len(train_entities))
    result["test_entities"] = int(len(test_entities))
    result["source_duplicate_entries"] = int(len(positive_pairs))
    result["source_nonduplicate_entries"] = int(len(negative_pairs))
    result["train_positive_pairs"] = int(len(train_pos))
    result["train_negative_pairs"] = int(len(train_neg))
    result["test_positive_pairs"] = int(len(test_pos))
    result["test_negative_pairs"] = int(len(test_neg))
    result["positive_label_agreement_with_ncid"] = float(positive_valid / len(positive_pairs))
    result["negative_label_agreement_with_ncid"] = float(negative_valid / len(negative_pairs))
    return result


def main() -> None:
    result = {
        "protocol": {
            "seed": SEED,
            "split": "80/20 by person identity (TCPD pid; NCVoters NCID), before model fitting",
            "metrics_note": "Precision, recall, F1 and average precision apply only to the constructed candidate-pair sets. TCPD negatives are sampled hard negatives; NCVoters includes its provided non-duplicate pairs. Neither estimates real pension-population error rates.",
            "review_budget_note": "Top 5% of each test candidate-pair list; this is a comparison within that dataset's constructed pool, not real field-team capacity.",
            "tcpd_pair_cap": TCPD_POSITIVE_PAIR_CAP,
            "features": FEATURE_NAMES,
            "limits": [
                "TCPD labels are human-reviewed candidate identity clusters and contain possible errors.",
                "TCPD candidates are not representative of pension beneficiaries.",
                "NCVoters is U.S. voter data and is subject to non-commercial-use terms.",
                "No demographic, geographic, or language subgroup claims are made in this first run.",
            ],
        },
        "results": [evaluate_tcpd(), evaluate_ncvoters()],
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "linkage_evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Zinda matcher evaluation",
        "",
        "This report uses person-level 80/20 splits and reports TCPD and NCVoters independently.",
        "Metrics refer only to the constructed candidate-pair pools; they are not pension-population accuracy estimates.",
        "",
        f"Split seed: `{SEED}`. Review budget: top {int(REVIEW_FRACTION * 100)}% of each test pair pool.",
        "",
        "| Dataset | Train pairs | Test pairs | Test positive rate | Exact name AP | Fuzzy 0.90 AP | Logistic AP | Logistic F1 | Logistic recall @ 5% review | Logistic precision @ 5% review | Brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["results"]:
        baselines = row["baselines"]
        model = row["logistic_regression"]
        lines.append(
            "| {dataset} | {train_pairs:,} | {test_pairs:,} | {test_positive_rate:.3f} | {exact:.3f} | {fuzzy:.3f} | {ap:.3f} | {f1:.3f} | {recall:.3f} | {precision:.3f} | {brier:.3f} |".format(
                dataset=row["dataset"],
                train_pairs=row["train_pairs"],
                test_pairs=row["test_pairs"],
                test_positive_rate=row["test_positive_rate"],
                exact=baselines["exact_normalized_name"]["average_precision"],
                fuzzy=baselines["fuzzy_ratio_ge_0.90"]["average_precision"],
                ap=model["average_precision"],
                f1=model["f1"],
                recall=model["recall_at_review_budget"],
                precision=model["precision_at_review_budget"],
                brier=model["brier_score"],
            )
        )
    lines += [
        "",
        "## Protocol and limitations",
        "",
        "- TCPD negatives are hard negatives: different `pid`, same normalized state, and at least one shared name token of 3+ characters. Per-block candidate generation is capped, then negatives are sampled up to 1.5 per positive. Positive pairs are uniformly capped at 10,000 per split.",
        "- NCVoters uses its supplied duplicate and non-duplicate pair files. Before evaluation, every positive pair was checked to share NCID and every negative pair to have different NCIDs.",
        "- The model is logistic regression over fuzzy-name, token, initials, age, sex, and region agreement features. The decision threshold is selected on training data by F1; test labels are not used for threshold selection.",
        "- Results are not comparable across datasets because their pair construction and class prevalence differ. Neither dataset represents pension beneficiaries.",
        "- NCVoters contains identifiable public voter data and is covered by non-commercial-use terms. Raw files are locally ignored by Git and are not included in this report.",
        "",
    ]
    (reports / "linkage_evaluation.md").write_text("\n".join(lines))
    print(f"Wrote aggregate reports to {reports.relative_to(ROOT)}")
    for row in result["results"]:
        print(f"{row['dataset']}: train={row['train_pairs']} test={row['test_pairs']} AP={row['logistic_regression']['average_precision']:.4f} F1={row['logistic_regression']['f1']:.4f}")


if __name__ == "__main__":
    main()
