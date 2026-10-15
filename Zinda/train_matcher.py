#!/usr/bin/env python3
"""Train and save Zinda's TCPD-based pair matcher with an identity-held-out report."""
from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, precision_recall_curve, precision_score, recall_score, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from evaluate_linkage import (
    FEATURE_NAMES,
    SEED,
    TCPD_POSITIVE_PAIR_CAP,
    build_tcpd_split,
    make_feature_matrix,
    tcpd_records,
)


ROOT = Path(__file__).resolve().parent
MODEL_VERSION = "tcpd-mlp-17epoch-v1"
MAX_EPOCHS = 17


def make_pairs(positives: list[tuple], negatives: list[tuple]) -> list[tuple]:
    pairs = [(a, b, 1) for a, b in positives] + [(a, b, 0) for a, b in negatives]
    random.Random(SEED).shuffle(pairs)
    return pairs


def main() -> None:
    records = tcpd_records()
    entities = records.entity.drop_duplicates().to_numpy()
    train_entities, test_entities = train_test_split(entities, test_size=0.20, random_state=SEED)

    train_positive, train_negative = build_tcpd_split(records, set(train_entities), SEED)
    test_positive, test_negative = build_tcpd_split(records, set(test_entities), SEED + 1)
    train_pairs = make_pairs(train_positive, train_negative)
    test_pairs = make_pairs(test_positive, test_negative)
    x_train = make_feature_matrix(records, [(a, b) for a, b, _ in train_pairs])
    y_train = np.asarray([label for _, _, label in train_pairs], dtype=np.int8)
    x_test = make_feature_matrix(records, [(a, b) for a, b, _ in test_pairs])
    y_test = np.asarray([label for _, _, label in test_pairs], dtype=np.int8)

    model = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            batch_size=256,
            learning_rate_init=0.001,
            max_iter=MAX_EPOCHS,
            early_stopping=False,
            random_state=SEED,
        ),
    )
    model.fit(x_train, y_train)
    train_score = model.predict_proba(x_train)[:, 1]
    p, r, thresholds = precision_recall_curve(y_train, train_score)
    f1 = 2 * p[:-1] * r[:-1] / np.maximum(1e-12, p[:-1] + r[:-1])
    threshold = float(thresholds[int(np.argmax(f1))]) if len(thresholds) else 0.5

    test_score = model.predict_proba(x_test)[:, 1]
    predictions = test_score >= threshold
    tp = int(((predictions == 1) & (y_test == 1)).sum())
    fp = int(((predictions == 1) & (y_test == 0)).sum())
    fn = int(((predictions == 0) & (y_test == 1)).sum())
    tn = int(((predictions == 0) & (y_test == 0)).sum())
    precision = float(precision_score(y_test, predictions, zero_division=0))
    recall = float(recall_score(y_test, predictions, zero_division=0))
    report = {
        "model_version": MODEL_VERSION,
        "model_type": "MLPClassifier (64, 32 hidden units)",
        "training_epochs_max": MAX_EPOCHS,
        "training_data": "TCPD candidate records; identity is TCPD pid",
        "seed": SEED,
        "split": "80/20 by person ID before pair generation",
        "feature_names": FEATURE_NAMES,
        "records": int(len(records)),
        "entities": int(records.entity.nunique()),
        "train_entities": int(len(train_entities)),
        "test_entities": int(len(test_entities)),
        "train_positive_pairs": len(train_positive),
        "train_hard_negative_pairs": len(train_negative),
        "test_positive_pairs": len(test_positive),
        "test_hard_negative_pairs": len(test_negative),
        "positive_pair_cap_per_split": TCPD_POSITIVE_PAIR_CAP,
        "threshold": threshold,
        "threshold_selection": "F1-maximizing threshold on training candidate pairs; not calibrated for real-world match prevalence",
        "heldout_metrics": {
            "average_precision": float(average_precision_score(y_test, test_score)),
            "roc_auc": float(roc_auc_score(y_test, test_score)),
            "precision": precision,
            "recall": recall,
            "f1": float(2 * precision * recall / max(1e-12, precision + recall)),
            "confusion_counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        },
        "limits": [
            "TCPD is Indian election-candidate data, not pension-beneficiary data.",
            "Negative pairs are sampled hard negatives (same state, shared name token); pair prevalence is constructed.",
            "The output is a ranking score, not a calibrated real-world probability.",
            "The model must only prioritize manual review; it cannot establish identity or benefit status.",
        ],
    }

    model_dir = ROOT / "models"
    report_dir = ROOT / "reports"
    model_dir.mkdir(exist_ok=True)
    report_dir.mkdir(exist_ok=True)
    artifact_path = model_dir / "tcpd_linkage.joblib"
    joblib.dump({"pipeline": model, "threshold": threshold, "version": MODEL_VERSION, "features": FEATURE_NAMES}, artifact_path)
    (report_dir / "trained_model.json").write_text(json.dumps(report, indent=2) + "\n")

    md = [
        "# Trained matcher card",
        "",
        f"**Artifact:** `models/tcpd_linkage.joblib`  ",
        f"**Version:** `{MODEL_VERSION}`  ",
        f"**Model:** MLP with hidden layers (64, 32), trained for up to {MAX_EPOCHS} epochs.  ",
        "**Training data:** TCPD Indian election candidates; no voter or pension records used for fitting.",
        "",
        "The person-level holdout keeps each `pid` entirely in train or test. Positives are different records sharing a `pid`; hard negatives are different `pid`s from the same normalized state and sharing at least one name token of 3+ characters. Positive pairs are sampled uniformly up to 10,000 per split, and negatives up to 1.5 per positive. Training uses a maximum of 17 full passes (epochs) over the training pairs, without early stopping.",
        "",
        f"Held-out identities: {len(test_entities):,}. Held-out pairs: {len(test_pairs):,} ({len(test_positive):,} positive, {len(test_negative):,} hard negative).",
        f"AP: {report['heldout_metrics']['average_precision']:.3f}; ROC AUC: {report['heldout_metrics']['roc_auc']:.3f}; thresholded precision: {precision:.3f}; recall: {recall:.3f}; F1: {report['heldout_metrics']['f1']:.3f}.",
        f"The training-only F1 threshold is `{threshold:.4f}`. It is a demo review-routing threshold, not calibrated for a field population.",
        "",
        "## Limits",
        "",
        "These figures apply only to this constructed TCPD candidate-pair pool. TCPD is not representative of pension beneficiaries, and hard negatives are sampled rather than exhaustive. The model score is not a real-world match probability. It cannot confirm identity, death, eligibility, or wrongful removal; use it only to order records for a human reviewer.",
        "",
    ]
    (report_dir / "trained_model.md").write_text("\n".join(md))
    print(f"Saved {artifact_path.relative_to(ROOT)}")
    print(f"Held-out TCPD: AP={report['heldout_metrics']['average_precision']:.4f}, F1={report['heldout_metrics']['f1']:.4f}, threshold={threshold:.4f}")


if __name__ == "__main__":
    main()
