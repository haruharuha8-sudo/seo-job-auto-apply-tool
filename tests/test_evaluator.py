from __future__ import annotations

import unittest
from pathlib import Path

from src.collectors.csv_collector import load_jobs_from_csv
from src.collectors.sample_collector import load_sample_jobs
from src.config_loader import load_config
from src.evaluator import evaluate_jobs
from src.profile_loader import load_profile
from src.scorer import decide


class EvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(Path("config/config.json"))
        cls.profile = load_profile(Path("config/profile.json"))
        cls.jobs = load_sample_jobs(Path("data/sample_jobs.json"))
        cls.results = evaluate_jobs(cls.jobs, cls.config, cls.profile)
        cls.csv_jobs = load_jobs_from_csv(Path("data/input_jobs.csv"))
        cls.csv_results = evaluate_jobs(cls.csv_jobs, cls.config, cls.profile)

    def test_profile_loads(self) -> None:
        self.assertEqual(self.profile["role"], "フリーランスのSEOディレクター")
        self.assertTrue(self.profile["strengths"])

    def test_csv_jobs_load(self) -> None:
        self.assertEqual(len(self.csv_jobs), 5)

    def test_csv_required_skills_to_list(self) -> None:
        alpha = self.csv_jobs[0]
        self.assertIsInstance(alpha["required_skills"], list)
        self.assertIn("SEO", alpha["required_skills"])

    def test_must_false_not_scored(self) -> None:
        target = next(r for r in self.results if r.job_title == "Webライター（単発）")
        self.assertFalse(target.must_pass)
        self.assertEqual(target.score, 0)
        self.assertEqual(target.score_breakdown, "必須条件を満たさないためスコアリング対象外")

    def test_negative_seo_job_is_drop(self) -> None:
        target = next(r for r in self.results if r.job_title == "Webライター（単発）")
        self.assertEqual(target.decision, "drop")
        self.assertIn("否定的", target.risk_flags)

    def test_threshold_decisions(self) -> None:
        thresholds = self.config["scoring"]["thresholds"]
        self.assertEqual(decide(90, True, thresholds), "keep")
        self.assertEqual(decide(57, True, thresholds), "hold")
        self.assertEqual(decide(20, True, thresholds), "drop")
        self.assertEqual(decide(100, False, thresholds), "drop")

    def test_keep_has_drafts(self) -> None:
        target = next(r for r in self.results if r.decision == "keep")
        self.assertTrue(target.draft_short)
        self.assertTrue(target.draft_long)

    def test_hold_contains_yokakunin(self) -> None:
        target = next(r for r in self.results if r.decision == "hold")
        self.assertIn("要確認", target.draft_short + target.draft_notes)

    def test_profile_reflected_in_drafts(self) -> None:
        target = next(r for r in self.results if r.decision == "keep")
        self.assertIn(self.profile["role"], target.draft_short)
        self.assertIn(self.profile["strengths"][0], target.draft_long)

    def test_prohibited_claims_not_in_drafts(self) -> None:
        for target in self.results:
            for claim in self.profile["prohibited_claims"]:
                self.assertNotIn(claim, target.draft_short)
                self.assertNotIn(claim, target.draft_long)
                self.assertNotIn(claim, target.draft_notes)

    def test_no_codex_citation_strings_in_drafts(self) -> None:
        for target in self.results:
            self.assertNotIn("codex-terminal-citation", target.draft_short)
            self.assertNotIn("codex-terminal-citation", target.draft_long)
            self.assertNotIn("codex-terminal-citation", target.draft_notes)
            self.assertNotIn("codex-terminal-citation", target.manual_apply_checklist)

    def test_hold_has_simple_prefix(self) -> None:
        target = next(r for r in self.results if r.decision == "hold")
        self.assertTrue(target.draft_short.startswith("【要確認】"))

    def test_drop_has_no_drafts(self) -> None:
        for target in (r for r in self.results if r.decision == "drop"):
            self.assertEqual(target.draft_short, "")
            self.assertEqual(target.draft_long, "")
            self.assertEqual(target.draft_notes, "")
            self.assertEqual(target.manual_apply_checklist, "")

    def test_csv_output_has_no_forbidden_strings(self) -> None:
        import csv
        with open("output/phase1_results.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        forbidden = [
            "codex-terminal-citation",
            "codex-file-citation",
            "line_range_start",
            "line_range_end",
            "terminal_chunk_id",
            "【F:",
            "git_url=",
        ]
        for row in rows:
            for col in ["draft_short", "draft_long", "draft_notes", "manual_apply_checklist"]:
                value = row[col]
                for token in forbidden:
                    self.assertNotIn(token, value)

    def test_decision_counts_unchanged(self) -> None:
        counts = {"keep": 0, "hold": 0, "drop": 0}
        for r in self.results:
            counts[r.decision] += 1
        self.assertEqual(counts, {"keep": 2, "hold": 1, "drop": 2})


    def test_csv_missing_required_columns_raises(self) -> None:
        import tempfile
        from src.collectors.csv_collector import load_jobs_from_csv

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as tmp:
            tmp.write("title,company\n案件A,会社A\n")
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaises(ValueError) as cm:
                load_jobs_from_csv(tmp_path)
            self.assertIn("CSVの必須列が不足", str(cm.exception))
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_csv_input_decision_and_drafts(self) -> None:
        counts = {"keep": 0, "hold": 0, "drop": 0}
        for r in self.csv_results:
            counts[r.decision] += 1
            if r.decision in {"keep", "hold"}:
                self.assertTrue(r.draft_short)
            if r.decision == "drop":
                self.assertEqual(r.draft_short, "")
        self.assertEqual(counts, {"keep": 2, "hold": 1, "drop": 2})


if __name__ == "__main__":
    unittest.main()
