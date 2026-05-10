from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def write_csv(path: Path, rows: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "job_title",
                "company",
                "must_pass",
                "decision",
                "score",
                "must_reasons",
                "score_breakdown",
                "risk_flags",
                "matched_skills",
                "url",
                "draft_short",
                "draft_long",
                "draft_notes",
                "manual_apply_checklist",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
