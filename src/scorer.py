from __future__ import annotations

from typing import Any


def score_job(job: dict[str, Any], cfg: dict[str, Any], seo_weak: bool, negative_seo_hit: bool) -> tuple[int, list[str], list[str], list[str]]:
    weights = cfg["weights"]
    prefs = cfg["preferences"]
    score = 0
    breakdown: list[str] = []
    risk_flags: list[str] = []

    if job.get("role_category") in ["seo_writer", "seo_director"]:
        score += weights["role_fit"]
        breakdown.append(f"希望職種と一致（+{weights['role_fit']}）")

    if (job.get("budget_min") or 0) >= prefs["min_budget"]:
        score += weights["budget_fit"]
        breakdown.append(f"予算条件を満たす（+{weights['budget_fit']}）")
    elif (job.get("budget_max") or 0) >= prefs["min_budget"]:
        partial = weights["budget_fit"] // 2
        score += partial
        breakdown.append(f"予算条件を一部満たす（+{partial}）")
    else:
        breakdown.append("予算条件を満たさない（+0）")

    if job.get("work_style") in prefs["preferred_work_style"]:
        score += weights["work_style_fit"]
        breakdown.append(f"リモート可（+{weights['work_style_fit']}）")
    elif job.get("work_style") == "hybrid":
        partial = weights["work_style_fit"] // 2
        score += partial
        breakdown.append(f"ハイブリッド勤務（+{partial}）")
    else:
        breakdown.append("勤務形態の条件に合わない（+0）")

    skills = job.get("required_skills", [])
    matched = [s for s in prefs["skill_keywords"] if s in skills]
    if matched:
        skill_score = min(weights["skill_fit"], len(matched) * 5)
        score += skill_score
        breakdown.append(f"スキル一致 {', '.join(matched)}（+{skill_score}）")
    else:
        breakdown.append("優先スキル一致なし（+0）")

    description = job.get("description", "")
    if any(k in description for k in ["長期", "中長期", "継続"]):
        score += weights["continuity_signal"]
        breakdown.append(f"継続性が見込める（+{weights['continuity_signal']}）")

    clarity_fields = [job.get("budget_min"), job.get("work_style"), job.get("required_skills")]
    if all(clarity_fields):
        score += weights["clarity_bonus"]
        breakdown.append(f"案件情報が明確（+{weights['clarity_bonus']}）")

    if negative_seo_hit:
        score -= weights["seo_negative_penalty"]
        breakdown.append(f"SEO関連性が弱いため減点（-{weights['seo_negative_penalty']}）")
        risk_flags.append("SEO否定表現あり")
    elif seo_weak:
        score -= weights["seo_weak_penalty"]
        breakdown.append(f"SEO関連性が弱いため減点（-{weights['seo_weak_penalty']}）")
        risk_flags.append("SEO関連性が弱い")

    return max(0, min(score, 100)), breakdown, matched, risk_flags


def decide(score: int, must_pass: bool, thresholds: dict[str, int]) -> str:
    if not must_pass:
        return "drop"
    if score >= thresholds["keep_min_score"]:
        return "keep"
    if score >= thresholds["hold_min_score"]:
        return "hold"
    return "drop"
