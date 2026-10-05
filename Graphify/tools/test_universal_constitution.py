#!/usr/bin/env python3
"""Unit tests for the Universal App Constitution governance authority and validator rules."""

from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

from semantic_validator import (
    MASTER_HASHES,
    git_blob_sha256,
    universal_constitution_errors,
)

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "Graphify"
QUEUE_PATH = G / "IMPLEMENTATION_QUEUE.json"
CONST_JSON_PATH = G / "UNIVERSAL_APP_CONSTITUTION.json"
CONST_MD_PATH = G / "UNIVERSAL_APP_CONSTITUTION.md"
GAP_JSON_PATH = G / "MNEMORA_UNIVERSAL_RULES_GAP_REPORT.json"
GAP_MD_PATH = G / "MNEMORA_UNIVERSAL_RULES_GAP_REPORT.md"
AUDIT_MD_PATH = G / "CONSTITUTION_AUDIT.md"
START_HERE_PATH = G / "START-HERE.md"

ALL_UAC_IDS = [f"UAC-{i:02d}" for i in range(1, 23)]


class UniversalConstitutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.queue_tasks = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))["tasks"]
        self.const_json = json.loads(CONST_JSON_PATH.read_text(encoding="utf-8"))
        self.const_md = CONST_MD_PATH.read_text(encoding="utf-8")
        self.gap_json = json.loads(GAP_JSON_PATH.read_text(encoding="utf-8"))
        self.gap_md = GAP_MD_PATH.read_text(encoding="utf-8")
        self.audit_md = AUDIT_MD_PATH.read_text(encoding="utf-8")
        self.start_here = START_HERE_PATH.read_text(encoding="utf-8")

    def test_constitution_json_has_twenty_two_rules(self) -> None:
        self.assertEqual(self.const_json.get("schema_version"), 1)
        self.assertEqual(self.const_json.get("rule_count"), 22)
        rules = self.const_json.get("rules", [])
        self.assertEqual(len(rules), 22)
        rule_ids = [r["stable_rule_id"] for r in rules]
        self.assertEqual(rule_ids, ALL_UAC_IDS)

        for r in rules:
            self.assertTrue(r.get("title"))
            self.assertTrue(r.get("normative_text"))
            self.assertGreaterEqual(len(r.get("clauses", [])), 1)
            self.assertTrue(r.get("applicability"))
            self.assertTrue(r.get("verification_expectations"))

    def test_constitution_md_has_all_twenty_two_rules_and_matches_json(self) -> None:
        for r in self.const_json["rules"]:
            rid = r["stable_rule_id"]
            title = r["title"]
            self.assertIn(rid, self.const_md)
            expected_heading = f"{rid} — {title}"
            self.assertIn(expected_heading, self.const_md)

    def test_master_plan_hashes_verified(self) -> None:
        for name, expected in MASTER_HASHES.items():
            actual = git_blob_sha256(f"Graphify/Master Plan/{name}")
            self.assertEqual(actual, expected, f"Hash mismatch for {name}")
            self.assertIn(expected, self.audit_md)

    def test_constitution_audit_completeness_and_governance_correction(self) -> None:
        self.assertIn("6a9858a", self.audit_md)
        self.assertIn("ZERO MASTER PLAN CONFLICTS", self.audit_md)
        self.assertIn("PASS", self.audit_md)
        for rid in ALL_UAC_IDS:
            self.assertIn(rid, self.audit_md, f"Audit missing evaluation of {rid}")

    def test_gap_report_json_and_md_completeness(self) -> None:
        evals = self.gap_json.get("evaluations", [])
        self.assertEqual(len(evals), 22)
        eval_ids = [e["stable_rule_id"] for e in evals]
        self.assertEqual(eval_ids, ALL_UAC_IDS)

        q_ids = {t["stable_task_id"] for t in self.queue_tasks}

        for e in evals:
            rid = e["stable_rule_id"]
            self.assertIn(rid, self.gap_md)
            status = e.get("status")
            self.assertIn(status, {"SATISFIED", "PARTIAL", "MISSING", "CONFLICT", "NOT_APPLICABLE"})
            if status == "SATISFIED":
                self.assertTrue(bool(e.get("evidence_paths")) or bool(e.get("evidence_explanation")))
            elif status in {"PARTIAL", "MISSING"}:
                self.assertTrue(bool(e.get("missing_implementation")))
                if e.get("queue_change_required"):
                    for tid in e.get("affected_task_ids", []):
                        self.assertIn(tid, q_ids, f"Queue task {tid} missing for {rid}")

    def test_authority_hierarchy_in_start_here(self) -> None:
        authority_section = ""
        if "## Authority order" in self.start_here:
            authority_section = self.start_here.split("## Authority order", 1)[1].split("##", 1)[0]
        else:
            authority_section = self.start_here
        uac_pos = authority_section.find("Universal App Constitution")
        if uac_pos == -1:
            uac_pos = authority_section.find("UNIVERSAL_APP_CONSTITUTION")
        mp_pos = authority_section.find("Master Plan")
        self.assertNotEqual(uac_pos, -1, "START-HERE.md missing Universal App Constitution")
        self.assertNotEqual(mp_pos, -1, "START-HERE.md missing Master Plan")
        self.assertLess(uac_pos, mp_pos, "Universal App Constitution must be authority #1 above Master Plan")

    def test_validator_clean_on_current_repository_state(self) -> None:
        errors = universal_constitution_errors(self.queue_tasks)
        self.assertEqual(errors, [], f"Universal constitution errors detected: {errors}")

    def test_negative_fixture_deleting_uac_04_fails(self) -> None:
        corrupted = copy.deepcopy(self.const_json)
        corrupted["rules"] = [r for r in corrupted["rules"] if r.get("stable_rule_id") != "UAC-04"]
        errors = universal_constitution_errors(self.queue_tasks, const_json_override=corrupted)
        self.assertTrue(any("UAC-04" in e for e in errors))

    def test_negative_fixture_deleting_uac_06_fails(self) -> None:
        corrupted = copy.deepcopy(self.const_json)
        corrupted["rules"] = [r for r in corrupted["rules"] if r.get("stable_rule_id") != "UAC-06"]
        errors = universal_constitution_errors(self.queue_tasks, const_json_override=corrupted)
        self.assertTrue(any("UAC-06" in e for e in errors))

    def test_negative_fixture_deleting_uac_11_fails(self) -> None:
        corrupted = copy.deepcopy(self.const_json)
        corrupted["rules"] = [r for r in corrupted["rules"] if r.get("stable_rule_id") != "UAC-11"]
        errors = universal_constitution_errors(self.queue_tasks, const_json_override=corrupted)
        self.assertTrue(any("UAC-11" in e for e in errors))

    def test_negative_fixture_changing_stable_rule_id_fails(self) -> None:
        corrupted = copy.deepcopy(self.const_json)
        corrupted["rules"][0]["stable_rule_id"] = "UAC-99"
        errors = universal_constitution_errors(self.queue_tasks, const_json_override=corrupted)
        self.assertTrue(any("unrecognized or modified stable_rule_id" in e or "missing rule" in e for e in errors))

    def test_negative_fixture_markdown_json_disagreement_fails(self) -> None:
        corrupted_md = self.const_md.replace("UAC-04 — NAS / PRIVATE-LAN SUPPORT", "UAC-04 — ALTERED TITLE")
        errors = universal_constitution_errors(self.queue_tasks, const_md_override=corrupted_md)
        self.assertTrue(any("disagrees with JSON" in e for e in errors))

    def test_negative_fixture_audit_omitting_rule_fails(self) -> None:
        corrupted_audit = self.audit_md.replace("UAC-15", "OMITTED_RULE_15")
        errors = universal_constitution_errors(self.queue_tasks, audit_text_override=corrupted_audit)
        self.assertTrue(any("missing evaluation of rule UAC-15" in e for e in errors))

    def test_negative_fixture_false_satisfied_with_no_evidence_fails(self) -> None:
        corrupted_gap = copy.deepcopy(self.gap_json)
        for ev in corrupted_gap["evaluations"]:
            if ev.get("stable_rule_id") == "UAC-01":
                ev["status"] = "SATISFIED"
                ev["evidence_paths"] = []
                ev["evidence_explanation"] = ""
                ev["evidence_references"] = []
        errors = universal_constitution_errors(self.queue_tasks, gap_json_override=corrupted_gap)
        self.assertTrue(any("false SATISFIED with no evidence" in e for e in errors))

    def test_negative_fixture_unresolved_gap_with_no_queue_coverage_fails(self) -> None:
        tasks_no_nas = [t for t in self.queue_tasks if t.get("stable_task_id") not in {"TASK-DEC-NAS", "TASK-OUT-NAS-DEFAULT", "TASK-OUT-NAS-DEVIATION"}]
        errors = universal_constitution_errors(tasks_no_nas)
        self.assertTrue(any("missing from queue" in e for e in errors))

    def test_negative_fixture_runtime_hermes_dependency_fails(self) -> None:
        hermes_sample = "const { orchestrate } = require('@hermes/core');"
        forbidden_pattern = re.compile(
            r"""(?:from\s+['"]?(?:Graphify|hermes)|import\s+.*['"]?(?:Graphify|hermes)|require\s*\(\s*['"][^'"]*(?:Graphify|hermes))""",
            re.I,
        )
        self.assertTrue(bool(forbidden_pattern.search(hermes_sample)))

    def test_negative_fixture_silent_external_mutation_claimed_compliant_fails(self) -> None:
        corrupted_gap = copy.deepcopy(self.gap_json)
        for ev in corrupted_gap["evaluations"]:
            if ev.get("stable_rule_id") == "UAC-11":
                ev["status"] = "SATISFIED"
                ev["evidence_explanation"] = "Silent overwrite of divergent external modifications is accepted without flagging."
        errors = universal_constitution_errors(self.queue_tasks, gap_json_override=corrupted_gap)
        self.assertTrue(any("Silent external mutation cannot be claimed compliant" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
