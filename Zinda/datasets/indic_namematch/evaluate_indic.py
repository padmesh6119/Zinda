#!/usr/bin/env python3
"""Aggregate-only evaluation of public hand-authored Indian name pairs."""
import csv
import json
from collections import defaultdict
from pathlib import Path

from rapidfuzz import fuzz
from sklearn.metrics import average_precision_score, roc_auc_score

from indic_namematch import REGISTRY

ROOT = Path(__file__).resolve().parent
THRESHOLD = 0.90


def metrics(scores, labels):
    predicted = [score >= THRESHOLD for score in scores]
    tp = sum(p and y for p, y in zip(predicted, labels))
    fp = sum(p and not y for p, y in zip(predicted, labels))
    fn = sum(not p and y for p, y in zip(predicted, labels))
    tn = sum(not p and not y for p, y in zip(predicted, labels))
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    return {
        "threshold": THRESHOLD,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(1e-12, precision + recall),
        "false_positive_rate": fp / max(1, fp + tn),
        "average_precision": average_precision_score(labels, scores),
        "roc_auc": roc_auc_score(labels, scores),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def main():
    with (ROOT / "name_pairs.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    labels = [r["label"] == "match" for r in rows]
    scores_by_matcher = {
        "fuzzy_ratio": [fuzz.ratio(r["name_a"], r["name_b"]) / 100 for r in rows],
        **{name: [fn(r["name_a"], r["name_b"]) for r in rows] for name, fn in REGISTRY.items()},
    }
    results = {name: metrics(scores, labels) for name, scores in scores_by_matcher.items()}
    categories = defaultdict(list)
    for i, row in enumerate(rows):
        categories[row["category"]].append(i)
    cat = {}
    for name, indexes in sorted(categories.items()):
        pos = sum(labels[i] for i in indexes)
        cat[name] = {
            "pairs": len(indexes),
            "matches": int(pos),
            "non_matches": int(len(indexes) - pos),
            "fuzzy_ratio_correct_at_0_90": int(sum((scores_by_matcher["fuzzy_ratio"][i] >= THRESHOLD) == labels[i] for i in indexes)),
            "rarity_weighted_correct_at_0_90": int(sum((scores_by_matcher["rarity_weighted"][i] >= THRESHOLD) == labels[i] for i in indexes)),
        }
    output = {
        "dataset": "indic-namematch hand-authored synthetic challenge pairs",
        "pair_count": len(rows),
        "matches": sum(labels),
        "non_matches": len(labels) - sum(labels),
        "unresolvable_pairs": sum(r["resolvable"] == "no" for r in rows),
        "threshold_note": "Fixed 0.90 for precision/recall/F1; AP and ROC AUC summarize ranking. This is descriptive challenge-set evaluation, not a population estimate.",
        "results": results,
        "category_aggregates": cat,
    }
    (ROOT / "evaluation.json").write_text(json.dumps(output, indent=2) + "\n")
    lines = ["# Indian name challenge evaluation", "", "The source is a small, hand-authored synthetic challenge set. These metrics are descriptive and are not pension-population estimates.", "", f"Pairs: {len(rows)} ({sum(labels)} matches, {len(labels)-sum(labels)} non-matches); unresolvable from names alone: {output['unresolvable_pairs']}.", "Fixed decision threshold: 0.90. No benchmark labels were used for training.", "", "| Matcher | AP | ROC AUC | Precision | Recall | F1 | FPR |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, m in results.items():
        lines.append(f"| {name} | {m['average_precision']:.3f} | {m['roc_auc']:.3f} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['false_positive_rate']:.3f} |")
    lines += ["", "## Category summary", "", "Correct count at the same fixed threshold; categories with very few pairs are especially noisy.", "", "| Category | Pairs | Matches | Fuzzy correct | Rarity weighted correct |", "|---|---:|---:|---:|---:|"]
    for name, c in cat.items():
        lines.append(f"| {name} | {c['pairs']} | {c['matches']} | {c['fuzzy_ratio_correct_at_0_90']} | {c['rarity_weighted_correct_at_0_90']} |")
    (ROOT / "evaluation.md").write_text("\n".join(lines) + "\n")
    print(f"Evaluated {len(rows)} pairs across {len(categories)} categories; aggregate reports written.")


if __name__ == "__main__":
    main()
