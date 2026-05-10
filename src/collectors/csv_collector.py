from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {
    "source",
    "title",
    "company",
    "role_category",
    "employment_type",
    "budget_min",
    "budget_max",
    "work_style",
    "description",
    "required_skills",
    "nice_to_have",
    "url",
    "posted_at",
}


def _split_csv_list(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_jobs_from_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSVヘッダーが見つかりません。必須列を含むヘッダー行を追加してください。")

        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames))
        if missing:
            raise ValueError(
                "CSVの必須列が不足しています: " + ", ".join(missing)
            )

        jobs: list[dict[str, Any]] = []
        for row in reader:
            jobs.append(
                {
                    "source": row["source"],
                    "title": row["title"],
                    "company": row["company"],
                    "role_category": row["role_category"],
                    "contract_type": row["employment_type"],
                    "budget_min": int(row["budget_min"] or 0),
                    "budget_max": int(row["budget_max"] or 0),
                    "work_style": row["work_style"],
                    "description": row["description"],
                    "required_skills": _split_csv_list(row["required_skills"]),
                    "nice_to_have": _split_csv_list(row["nice_to_have"]),
                    "url": row["url"],
                    "posted_at": row["posted_at"],
                }
            )
    return jobs
