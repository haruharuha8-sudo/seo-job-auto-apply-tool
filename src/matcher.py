from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SeoCheckResult:
    seo_ok: bool
    seo_weak: bool
    negative_seo_hit: bool
    reasons: list[str]
    risks: list[str]


@dataclass
class MustCheckResult:
    must_pass: bool
    seo_weak: bool
    negative_seo_hit: bool
    reasons: list[str]
    risks: list[str]


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def seo_relevance(job: dict[str, Any], must_cfg: dict[str, Any]) -> SeoCheckResult:
    title = job.get("title", "")
    description = job.get("description", "")
    role_category = job.get("role_category", "")
    required_skills = job.get("required_skills", [])
    required_skills_text = " ".join(required_skills)

    combined_text = " ".join([title, description, required_skills_text])

    negative_hit = contains_any(combined_text, must_cfg["seo_negative_patterns"])
    role_hit = role_category in must_cfg["preferred_role_categories"]
    keyword_hit = contains_any(combined_text, must_cfg["seo_positive_keywords"])
    skill_hit = any("SEO" in skill for skill in required_skills)

    reasons: list[str] = []
    risks: list[str] = []

    if role_hit:
        reasons.append("希望職種（SEOライター/ディレクター）と一致")
    if keyword_hit:
        reasons.append("SEO関連キーワードを確認")
    if skill_hit:
        reasons.append("必須スキルにSEO関連項目あり")

    if negative_hit:
        risks.append("SEO関連性が低い・否定的な表現あり")

    seo_ok = (role_hit or (keyword_hit and skill_hit)) and not negative_hit
    seo_weak = (role_hit or keyword_hit or skill_hit) and not seo_ok

    if not seo_ok and not seo_weak:
        risks.append("SEO関連性が不足")

    return SeoCheckResult(
        seo_ok=seo_ok,
        seo_weak=seo_weak,
        negative_seo_hit=negative_hit,
        reasons=reasons,
        risks=risks,
    )


def evaluate_must_conditions(job: dict[str, Any], cfg: dict[str, Any]) -> MustCheckResult:
    reasons: list[str] = []
    risks: list[str] = []

    contract_ok = any(k in job.get("contract_type", "") for k in cfg["contract_type_includes"])
    if contract_ok:
        reasons.append("業務委託条件を満たす")
    else:
        risks.append("業務委託ではないため除外")

    seo = seo_relevance(job, cfg)
    reasons.extend(seo.reasons)
    risks.extend(seo.risks)

    must_pass = contract_ok and seo.seo_ok
    return MustCheckResult(
        must_pass=must_pass,
        seo_weak=seo.seo_weak,
        negative_seo_hit=seo.negative_seo_hit,
        reasons=reasons,
        risks=risks,
    )
