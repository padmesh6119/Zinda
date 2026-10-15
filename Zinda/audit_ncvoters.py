#!/usr/bin/env python3
"""Check NCVoters pair difficulty and identity split integrity; outputs aggregates only."""
import json
import sys
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz
from sklearn.model_selection import train_test_split

from evaluate_linkage import ROOT, clean


def summarize(records, pairs, label, train_ids, test_ids):
    id_to_entity = records.entity.to_dict()
    id_to_name = records["_name"].to_dict()
    id_to_region = records["_region"].to_dict()
    same_train = same_test = cross = missing = 0
    exact = ratio90 = token90 = same_region = shared_token = 0
    ratios = []
    for a, b in pairs:
        a, b = str(a), str(b)
        ea, eb = id_to_entity.get(a), id_to_entity.get(b)
        if ea is None or eb is None:
            missing += 1
            continue
        if ea in train_ids and eb in train_ids:
            same_train += 1
        elif ea in test_ids and eb in test_ids:
            same_test += 1
        else:
            cross += 1
        na, nb = id_to_name[a], id_to_name[b]
        ratio = fuzz.ratio(na, nb) / 100 if na and nb else 0
        ratios.append(ratio)
        exact += bool(na and na == nb)
        ratio90 += ratio >= .90
        token90 += (fuzz.token_sort_ratio(na, nb) / 100 if na and nb else 0) >= .90
        same_region += bool(id_to_region[a] and id_to_region[a] == id_to_region[b])
        shared_token += bool(set(na.split()) & set(nb.split()))
    n = max(1, len(pairs) - missing)
    ratios.sort()
    return {
        "label": label, "pairs": len(pairs), "missing_endpoints": missing,
        "train_identity_pairs": same_train, "test_identity_pairs": same_test,
        "cross_split_or_mixed_identity_pairs": cross,
        "exact_normalized_name_fraction": exact / n,
        "name_ratio_ge_0_90_fraction": ratio90 / n,
        "token_sort_ge_0_90_fraction": token90 / n,
        "same_region_fraction": same_region / n,
        "shared_token_fraction": shared_token / n,
        "median_name_ratio": ratios[len(ratios)//2] if ratios else None,
    }


def main():
    data = pd.read_csv(ROOT / "datasets/ncvoters/ncvoters.tsv", sep="\t", dtype=str, keep_default_na=False)
    records = data.rename(columns={"id":"row_id", "ncid":"entity", "first_name":"first", "midl_name":"middle", "last_name":"last", "state_cd":"region"})
    records["name"] = records[["first", "middle", "last"]].agg(" ".join, axis=1)
    records["_name"] = records.name.map(clean)
    records["_region"] = records.region.map(clean)
    records.index = records.row_id.astype(str)
    dpl = pd.read_csv(ROOT / "datasets/ncvoters/ncvoters_DPL.tsv", sep="\t", dtype=str)
    ndpl = pd.read_csv(ROOT / "datasets/ncvoters/ncvoters_NDPL.tsv", sep="\t", dtype=str)
    entities = records.entity.drop_duplicates().to_numpy()
    train, test = train_test_split(entities, test_size=.20, random_state=20261013)
    train, test = set(train), set(test)
    positives = list(dpl[["id1", "id2"]].itertuples(index=False, name=None))
    negatives = list(ndpl[["id1", "id2"]].itertuples(index=False, name=None))
    test_positives = [(a, b) for a, b in positives if records.at[str(a), "entity"] in test and records.at[str(b), "entity"] in test]
    test_negatives = [(a, b) for a, b in negatives if records.at[str(a), "entity"] in test and records.at[str(b), "entity"] in test]
    results = [
        summarize(records, positives, "all provided duplicate pairs", train, test),
        summarize(records, negatives, "all provided generated non-duplicate pairs", train, test),
        summarize(records, test_positives, "held-out provided duplicate pairs", train, test),
        summarize(records, test_negatives, "held-out provided generated non-duplicate pairs", train, test),
    ]
    out = {
        "identity_split": "80/20 by NCID, seed 20261013; identity sets are disjoint by construction",
        "train_entities": len(train), "test_entities": len(test), "identity_intersection": len(train & test),
        "pair_difficulty": results,
        "interpretation": "This audit checks whether supplied negative pairs are much easier than positives. It uses names only for aggregate similarity summaries and does not export row-level data.",
    }
    path = ROOT / "reports/ncvoters_pair_audit.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n")
    lines = ["# NCVoters pair construction audit", "", "No row-level names or IDs are included.", "", f"Identity split: {len(train):,} train NCIDs and {len(test):,} test NCIDs; intersection: {len(train & test)}.", "", "| Pair source | Pairs | Name ratio ≥ .90 | Token-sort ≥ .90 | Exact name | Shared token | Same region | Median ratio |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in results:
        lines.append(f"| {r['label']} | {r['pairs']:,} | {r['name_ratio_ge_0_90_fraction']:.3f} | {r['token_sort_ge_0_90_fraction']:.3f} | {r['exact_normalized_name_fraction']:.3f} | {r['shared_token_fraction']:.3f} | {r['same_region_fraction']:.3f} | {r['median_name_ratio']:.3f} |")
    lines += ["", "## Interpretation", "", "The identity split prevents records belonging to the same NCID from crossing train and test. However, the benchmark's generated non-duplicate pairs may be easier than difficult real-world collisions. If their name-similarity rates are far below those for duplicates, near-perfect NCVoters scores should not be presented as evidence of robust hard-negative discrimination. The next validation step is a separately constructed same-region, shared-token negative set.", ""]
    (ROOT / "reports/ncvoters_pair_audit.md").write_text("\n".join(lines))
    print("NCVoters aggregate pair audit written.")


if __name__ == "__main__":
    main()
