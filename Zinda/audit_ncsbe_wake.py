#!/usr/bin/env python3
"""Aggregate-only comparison of HPI's 2018 Wake sample with current Wake records."""
import json
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
HPI_PATH = ROOT / "datasets/ncvoters/ncvoters.tsv"
NCSBE_PATH = ROOT / "datasets/ncsbe_current/ncvoter92.zip"


def main():
    hpi = pd.read_csv(HPI_PATH, sep="\t", dtype=str, keep_default_na=False, usecols=["ncid", "county_desc"])
    hpi_wake = hpi[hpi.county_desc.str.strip().str.casefold().eq("wake")]
    # HPI's prepared extract lowercases its values; compare identifiers case-insensitively.
    old_ids = set(hpi_wake.ncid.str.strip().str.casefold()) - {""}

    found = set()
    statuses = Counter()
    county_rows = 0
    with zipfile.ZipFile(NCSBE_PATH) as archive, archive.open("ncvoter92.txt") as stream:
        chunks = pd.read_csv(
            stream,
            sep="\t",
            dtype=str,
            keep_default_na=False,
            encoding="cp1252",
            usecols=["ncid", "status_cd", "voter_status_desc", "reason_cd", "voter_status_reason_desc"],
            chunksize=200_000,
        )
        for chunk in chunks:
            county_rows += len(chunk)
            chunk["ncid"] = chunk.ncid.str.strip().str.casefold()
            matched = chunk[chunk.ncid.isin(old_ids)]
            for row in matched[["ncid", "status_cd", "voter_status_desc", "reason_cd", "voter_status_reason_desc"]].itertuples(index=False, name=None):
                ncid, status_cd, status_desc, reason_cd, reason_desc = row
                found.add(ncid)
                # Aggregate only; never write or print row-level IDs or descriptions.
                statuses[(status_cd.strip(), status_desc.strip(), reason_cd.strip(), reason_desc.strip())] += 1

    result = {
        "older_source": "HPI prepared NCVoters sample, Nov 6 2018 snapshot",
        "newer_source": "NCSBE Wake County current voter file, file last modified Oct 12 2026",
        "older_wake_rows": int(len(hpi_wake)),
        "older_distinct_ncid_count": len(old_ids),
        "newer_wake_row_count": county_rows,
        "older_sample_ncid_present_in_newer_wake": len(found),
        "older_sample_ncid_not_found_in_newer_wake": len(old_ids - found),
        "matched_status_reason_counts": [
            {"status_cd": key[0], "status_desc": key[1], "reason_cd": key[2], "reason_desc": key[3], "count": count}
            for key, count in sorted(statuses.items())
        ],
        "interpretation": "This is only a sample-continuity audit. An older NCID absent from the current Wake file may have moved counties, been removed, or otherwise changed; absence here is not evidence of wrongful deletion. Status/reason codes are administrative labels, not independently verified error labels.",
    }
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "wake_cross_snapshot_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    rows = [
        "# Wake County cross-snapshot sample audit",
        "",
        "Aggregate counts only; no row-level identifiers or personal details are included.",
        "",
        f"Older HPI sample date: Nov 6, 2018. Newer county file last modified: Oct 12, 2026.",
        f"HPI Wake rows: {len(hpi_wake):,}; distinct NCIDs: {len(old_ids):,}.",
        f"Current Wake rows scanned: {county_rows:,}.",
        f"Older sample NCIDs found in current Wake: {len(found):,}; not found: {len(old_ids-found):,}.",
        "",
        "## Administrative status/reason counts among the overlapping sample",
        "",
        "| Status | Reason | Count |",
        "|---|---|---:|",
    ]
    for row in result["matched_status_reason_counts"]:
        rows.append(f"| {row['status_cd']} ({row['status_desc']}) | {row['reason_cd']} ({row['reason_desc']}) | {row['count']:,} |")
    rows += [
        "",
        "## Limits",
        "",
        "This is a sample-continuity audit, not an end-to-end deletion-detection evaluation. An older ID absent from the current Wake file may have moved counties, been removed, or otherwise changed. NCSBE status and reason codes are administrative labels, not independent confirmation that an action was correct or wrongful. The 2018 HPI sample is only a small subset of the earlier roll.",
        "",
    ]
    (report_dir / "wake_cross_snapshot_audit.md").write_text("\n".join(rows))
    print("Wrote aggregate-only Wake cross-snapshot report.")


if __name__ == "__main__":
    main()
