from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .matcher import evaluate_must_conditions
from .scorer import decide, score_job
from .draft_generator import generate_drafts


@dataclass
class JobResult:
    job_title: str
    company: str
    must_pass: bool
    decision: str
    score: int
    must_reasons: str
    score_breakdown: str
    risk_flags: str
    matched_skills: str
    url: str
    draft_short: str = ""
    draft_long: str = ""
    draft_notes: str = ""
    manual_apply_checklist: str = ""


def evaluate_jobs(jobs: list[dict[str, Any]], config: dict[str, Any], profile: dict[str, Any]) -> list[JobResult]:
    results: list[JobResult] = []
    for job in jobs:
        must = evaluate_must_conditions(job, config["must_conditions"])

        if must.must_pass:
            score, score_breakdown_list, matched_skills_list, scoring_risks = score_job(
                job,
                config["scoring"],
                must.seo_weak,
                must.negative_seo_hit,
            )
            score_breakdown = " / ".join(score_breakdown_list)
            matched_skills = ", ".join(matched_skills_list) if matched_skills_list else "なし"
            merged_risks = must.risks + scoring_risks
            risk_flags = " / ".join(merged_risks) if merged_risks else "なし"
        else:
            score = 0
            score_breakdown = "必須条件を満たさないためスコアリング対象外"
            matched_skills = "なし"
            risk_flags = " / ".join(must.risks) if must.risks else "なし"

        decision = decide(score, must.must_pass, config["scoring"]["thresholds"])
        row = JobResult(
                job_title=job.get("title", ""),
                company=job.get("company", ""),
                must_pass=must.must_pass,
                decision=decision,
                score=score,
                must_reasons=" / ".join(must.reasons) if must.reasons else "なし",
                score_breakdown=score_breakdown,
                risk_flags=risk_flags,
                matched_skills=matched_skills,
                url=job.get("url", ""),
            )
        draft = generate_drafts(row, profile)
        row.draft_short = draft.draft_short
        row.draft_long = draft.draft_long
        row.draft_notes = draft.draft_notes
        row.manual_apply_checklist = draft.manual_apply_checklist
        results.append(row)
    return results
