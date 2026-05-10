from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FORBIDDEN_SNIPPETS = [
    "codex-terminal-citation",
    "codex-file-citation",
    "{line_range_start=",
    "line_range_end",
    "terminal_chunk_id",
    "【F:",
    "git_url=",
]


@dataclass
class DraftResult:
    draft_short: str
    draft_long: str
    draft_notes: str
    manual_apply_checklist: str


def _is_writer_role(job_title: str) -> bool:
    return "ライター" in job_title


def _sanitize_text(text: str) -> str:
    cleaned = text
    for token in FORBIDDEN_SNIPPETS:
        cleaned = cleaned.replace(token, "")
    return cleaned.strip()


def _profile_summary(profile: dict[str, Any]) -> str:
    role = profile.get("role", "フリーランス")
    strengths = profile.get("strengths", [])
    strengths_text = "・".join(strengths[:5]) if strengths else "SEO支援"
    return f"{role}として、{strengths_text}を中心に支援しています。"


def _base_checklist(result: Any) -> list[str]:
    checklist = [
        "送信前に人間が応募文全体を確認する",
        "募集要件と応募文の整合性を最終確認する",
    ]
    if result.score < 70:
        checklist.append("要確認: 単価・稼働条件が希望に合うか確認する")
    if "SEO関連性" in result.risk_flags:
        checklist.append("要確認: SEO関連要件の有無を再確認する")
    return checklist


def generate_drafts(result: Any, profile: dict[str, Any]) -> DraftResult:
    if result.decision == "drop":
        return DraftResult("", "", "", "")

    writer_role = _is_writer_role(result.job_title)
    role_text = "SEOライター案件" if writer_role else "SEOディレクター案件"
    summary = _profile_summary(profile)
    allowed_claims = "、".join(profile.get("writing_allowed_claims", []))
    notes_policy = profile.get("notes_for_drafts", "送信前に人間確認が必要です。")

    short = (
        f"{result.company}様\n"
        f"{role_text}に応募したくご連絡いたしました。{summary} "
        f"{allowed_claims}の範囲で、案件に合わせてご提案します。"
    )

    long_text = (
        f"{result.company}様\n\n"
        f"このたびは{role_text}の募集を拝見し、ご連絡いたしました。"
        f"私は{summary}\n\n"
        "案件要件に合わせて、現状分析・改善方針の整理・実行優先度の設計を行い、"
        "必要に応じてライティング実務やディレクションまで一貫して対応可能です。"
        "不明点は事前に確認し、認識を揃えたうえで進行します。\n\n"
        "※本ドラフトは送信前に人間確認が必要です。"
    )

    notes = f"送信前に人間確認が必要です。{notes_policy}"
    checklist = _base_checklist(result)

    if result.decision == "hold":
        short = f"【要確認】{short}"
        notes = "要確認: 条件精査のうえ送信可否を判断してください。"
        checklist.append("要確認: keep基準未満の理由（単価・条件・SEO関連性）を確認する")

    return DraftResult(
        draft_short=_sanitize_text(short),
        draft_long=_sanitize_text(long_text),
        draft_notes=_sanitize_text(notes),
        manual_apply_checklist=_sanitize_text(" / ".join(checklist)),
    )
