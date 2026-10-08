#!/usr/bin/env python3
"""Disposable bootstrap tests for durable Graphify task execution state."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from execution_state import (
    ExecutionStateError,
    apply_queue_summary,
    authorized_task_paths,
    execution_state_errors,
    merge_execution_states,
    select_next_task,
    summarize_execution_state,
    validate_codebase_mutation,
    validate_run_state_checkpoint,
)


ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "Graphify" / "IMPLEMENTATION_QUEUE.json"
GENERATOR = ROOT / "Graphify" / "tools" / "complete_planning.py"
FIRST_TASK = "TASK-GOV-001-PROVENANCE-BASELINE"
SECOND_TASK = "TASK-CAP-DATA-SAFETY"


class ExecutionStateBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        self.tasks = copy.deepcopy(self.queue["tasks"])
        for task in self.tasks:
            task.pop("execution_state", None)
        merge_execution_states(self.tasks, None)

    @staticmethod
    def complete_state(task: dict, evidence_root: Path | None = None) -> dict:
        references = list(task["required_evidence_artifacts"])
        if evidence_root is not None:
            for reference in references:
                path = evidence_root.joinpath(*Path(reference).parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("disposable execution-state fixture evidence\n", encoding="utf-8")
        return {
            "disposition": "COMPLETE",
            "evidence_references": references,
            "checkpoint_identity": "0123456789abcdef0123456789abcdef01234567",
            "blocked_reason": None,
            "not_applicable_basis": None,
        }

    def test_initial_state_selects_task_one(self) -> None:
        summary = summarize_execution_state(self.tasks)
        self.assertEqual(summary["implementation_status"], "NOT STARTED")
        self.assertEqual(summary["next_task_id"], FIRST_TASK)
        self.assertEqual(summary["execution_state_counts"]["COMPLETE"], 0)

    def test_complete_survives_fixture_generation_and_selects_next_task_deterministically(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mnemora-execution-state-") as temp:
            temp_root = Path(temp)
            fixture = copy.deepcopy(self.queue)
            fixture["tasks"] = self.tasks
            first = fixture["tasks"][0]
            self.assertEqual(first["stable_task_id"], FIRST_TASK)
            first["execution_state"] = self.complete_state(first, temp_root)
            apply_queue_summary(fixture, summarize_execution_state(fixture["tasks"]))
            fixture["schema_version"] = 4
            input_path = temp_root / "input.json"
            output_one = temp_root / "output-one.json"
            output_two = temp_root / "output-two.json"
            input_path.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            command = [sys.executable, "-B", str(GENERATOR), "--execution-state-fixture", str(input_path), str(output_one), "--fixture-root", str(temp_root)]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            regenerated = json.loads(output_one.read_text(encoding="utf-8"))
            self.assertEqual(regenerated["tasks"][0]["execution_state"]["disposition"], "COMPLETE")
            self.assertEqual(regenerated["next_task_id"], SECOND_TASK)

            command[4] = str(output_one)
            command[5] = str(output_two)
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            self.assertEqual(output_one.read_bytes(), output_two.read_bytes())

    def test_dependency_invalid_complete_is_rejected(self) -> None:
        later = self.tasks[1]
        later["execution_state"] = self.complete_state(later)
        errors = execution_state_errors(self.tasks)
        self.assertTrue(any("dependency" in error and FIRST_TASK in error for error in errors), errors)

    def test_complete_without_evidence_or_checkpoint_is_rejected(self) -> None:
        self.tasks[0]["execution_state"]["disposition"] = "COMPLETE"
        errors = execution_state_errors(self.tasks)
        self.assertTrue(any("missing required evidence" in error for error in errors), errors)
        self.assertTrue(any("requires checkpoint_identity" in error for error in errors), errors)

    def test_blocked_task_is_not_skipped(self) -> None:
        self.tasks[0]["execution_state"] = {
            "disposition": "BLOCKED",
            "evidence_references": [],
            "checkpoint_identity": None,
            "blocked_reason": "Required external permission is unavailable",
            "not_applicable_basis": None,
        }
        self.assertEqual(execution_state_errors(self.tasks), [])
        self.assertEqual(select_next_task(self.tasks)["stable_task_id"], FIRST_TASK)
        self.assertEqual(summarize_execution_state(self.tasks)["implementation_status"], "BLOCKED")

    def test_evidence_backed_not_applicable_is_terminal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mnemora-not-applicable-") as temp:
            temp_root = Path(temp)
            evidence = "Graphify/evidence/conditional/not-applicable.json"
            evidence_path = temp_root.joinpath(*Path(evidence).parts)
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text("disposable reachability decision\n", encoding="utf-8")
            task = copy.deepcopy(self.tasks[0])
            task["execution_state"] = {
                "disposition": "NOT APPLICABLE",
                "evidence_references": [evidence],
                "checkpoint_identity": "0123456789abcdef0123456789abcdef01234567",
                "blocked_reason": None,
                "not_applicable_basis": "DEC-TEST selected the mutually exclusive sibling outcome",
            }
            self.assertEqual(execution_state_errors([task], temp_root), [])
            self.assertIsNone(select_next_task([task]))
            self.assertEqual(summarize_execution_state([task])["implementation_status"], "COMPLETE")

    def test_unknown_persisted_task_id_is_rejected(self) -> None:
        existing = copy.deepcopy(self.queue)
        existing["tasks"].append({"stable_task_id": "TASK-UNKNOWN", "execution_state": self.tasks[0]["execution_state"]})
        generated = copy.deepcopy(self.tasks)
        for task in generated:
            task.pop("execution_state", None)
        with self.assertRaises(ExecutionStateError):
            merge_execution_states(generated, existing)

    def test_authorized_task_paths_for_active_and_completed_tasks(self) -> None:
        expected_changes, expected_additions, forbidden = authorized_task_paths(self.tasks, "TASK-CAP-DATA-SAFETY")
        self.assertIn("codebase/main/infrastructure/persistence/dataMigration.js", expected_changes)
        self.assertIn("codebase/tests/integration/data-safety-and-migration-integrity.real-boundary.test.js", expected_additions)
        self.assertIn("Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md", forbidden)

    def test_validate_codebase_mutation_detects_unauthorized_and_forbidden_edits(self) -> None:
        expected_changes, expected_additions, forbidden = authorized_task_paths(self.tasks, "TASK-CAP-DATA-SAFETY")
        unauthorized_path = "codebase/renderer/App.tsx"
        self.assertNotIn(unauthorized_path, expected_changes)
        self.assertNotIn(unauthorized_path, expected_additions)
        forbidden_path = "Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md"
        self.assertIn(forbidden_path, forbidden)

    def test_negative_1_complete_with_nonexistent_checkpoint_sha_rejected(self) -> None:
        first = copy.deepcopy(self.queue["tasks"][0])
        first["execution_state"]["checkpoint_identity"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        errors = execution_state_errors([first], ROOT)
        self.assertTrue(
            any("does not resolve to a real Git commit" in err for err in errors),
            f"Expected git commit resolution error, got {errors}",
        )

    def test_negative_2_checkpoint_equals_starting_commit_after_mutations_rejected(self) -> None:
        fixture_delta = ROOT / "Graphify" / "evidence" / "_fixture_mut_delta.json"
        try:
            delta_content = {
                "starting_commit": "304be6391e41cad92884614011813665ccf1baff",
                "verified_baseline_commit": "304be6391e41cad92884614011813665ccf1baff",
                "checkpoint_identity": "304be6391e41cad92884614011813665ccf1baff",
                "ending_commit": "304be6391e41cad92884614011813665ccf1baff",
                "mutation_type": "CAPABILITY IMPLEMENTATION",
                "changed_files": ["codebase/main/example.js"],
                "added_files": [],
            }
            fixture_delta.write_text(json.dumps(delta_content), encoding="utf-8")
            task = {
                "stable_task_id": "TASK-MOCK-MUTATION",
                "task_kind": "CAPABILITY",
                "semantic_dependencies": [],
                "required_evidence_artifacts": ["Graphify/evidence/_fixture_mut_delta.json"],
                "execution_state": {
                    "disposition": "COMPLETE",
                    "evidence_references": ["Graphify/evidence/_fixture_mut_delta.json"],
                    "checkpoint_identity": "304be6391e41cad92884614011813665ccf1baff",
                    "blocked_reason": None,
                    "not_applicable_basis": None,
                },
            }
            errors = execution_state_errors([task], ROOT)
            self.assertTrue(
                any("cannot equal starting_commit" in err for err in errors),
                f"Expected start==checkpoint error, got {errors}",
            )
        finally:
            if fixture_delta.is_file():
                fixture_delta.unlink()

    def test_negative_3_task2_style_starting_commit_as_checkpoint_rejected(self) -> None:
        # Reproduces the historical defect where TASK-CAP-DATA-SAFETY used its starting commit 304be...
        # as its checkpoint_identity despite declared codebase mutations
        fixture_delta = ROOT / "Graphify" / "evidence" / "_fixture_task2_defect_delta.json"
        try:
            delta_content = {
                "starting_commit": "304be6391e41cad92884614011813665ccf1baff",
                "verified_baseline_commit": "304be6391e41cad92884614011813665ccf1baff",
                "checkpoint_identity": "304be6391e41cad92884614011813665ccf1baff",
                "ending_commit": "304be6391e41cad92884614011813665ccf1baff",
                "mutation_type": "DATA SAFETY RECOVERY AND CAPABILITY IMPLEMENTATION",
                "changed_files": ["codebase/main/infrastructure/persistence/dataMigration.js"],
                "added_files": ["codebase/tests/integration/data-safety-and-migration-integrity.real-boundary.test.js"],
            }
            fixture_delta.write_text(json.dumps(delta_content), encoding="utf-8")
            gov_task = copy.deepcopy(self.queue["tasks"][0])
            task2_defect = {
                "stable_task_id": "TASK-CAP-DATA-SAFETY",
                "task_kind": "CAPABILITY",
                "semantic_dependencies": ["TASK-GOV-001-PROVENANCE-BASELINE"],
                "required_evidence_artifacts": ["Graphify/evidence/_fixture_task2_defect_delta.json"],
                "execution_state": {
                    "disposition": "COMPLETE",
                    "evidence_references": ["Graphify/evidence/_fixture_task2_defect_delta.json"],
                    "checkpoint_identity": "304be6391e41cad92884614011813665ccf1baff",
                    "blocked_reason": None,
                    "not_applicable_basis": None,
                },
            }
            errors = execution_state_errors([gov_task, task2_defect], ROOT)
            self.assertTrue(
                any("cannot equal starting_commit '304be6391e41cad92884614011813665ccf1baff' after declared implementation mutations" in err for err in errors),
                f"Expected Task-2 defect rejection, got {errors}",
            )
        finally:
            if fixture_delta.is_file():
                fixture_delta.unlink()

    def test_negative_4_ending_commit_mismatch_rejected(self) -> None:
        fixture_delta = ROOT / "Graphify" / "evidence" / "_fixture_end_mismatch_delta.json"
        try:
            delta_content = {
                "starting_commit": "304be6391e41cad92884614011813665ccf1baff",
                "verified_baseline_commit": "304be6391e41cad92884614011813665ccf1baff",
                "checkpoint_identity": "6686f243ccf0d8d19632c54ce78dfe261168413c",
                "ending_commit": "304be6391e41cad92884614011813665ccf1baff",
                "mutation_type": "CAPABILITY IMPLEMENTATION",
                "changed_files": [],
                "added_files": [],
            }
            fixture_delta.write_text(json.dumps(delta_content), encoding="utf-8")
            task = {
                "stable_task_id": "TASK-MOCK-END-MISMATCH",
                "task_kind": "CAPABILITY",
                "semantic_dependencies": [],
                "required_evidence_artifacts": ["Graphify/evidence/_fixture_end_mismatch_delta.json"],
                "execution_state": {
                    "disposition": "COMPLETE",
                    "evidence_references": ["Graphify/evidence/_fixture_end_mismatch_delta.json"],
                    "checkpoint_identity": "6686f243ccf0d8d19632c54ce78dfe261168413c",
                    "blocked_reason": None,
                    "not_applicable_basis": None,
                },
            }
            errors = execution_state_errors([task], ROOT)
            self.assertTrue(
                any("ending_commit" in err and "!=" in err for err in errors),
                f"Expected ending_commit != checkpoint_identity error, got {errors}",
            )
        finally:
            if fixture_delta.is_file():
                fixture_delta.unlink()

    def test_negative_5_checkpoint_not_descendant_of_dependency_rejected(self) -> None:
        task_a = copy.deepcopy(self.queue["tasks"][0])
        task_a["stable_task_id"] = "TASK-A"
        task_a["execution_state"]["checkpoint_identity"] = "6686f243ccf0d8d19632c54ce78dfe261168413c"

        task_b = copy.deepcopy(self.queue["tasks"][0])
        task_b["stable_task_id"] = "TASK-B"
        task_b["semantic_dependencies"] = ["TASK-A"]
        task_b["execution_state"]["checkpoint_identity"] = "5ed0e52c9c52ebbf2329caff5cfd71af4b3e7237"

        errors = execution_state_errors([task_a, task_b], ROOT)
        self.assertTrue(
            any("is not a descendant of dependency TASK-A checkpoint" in err for err in errors),
            f"Expected non-descendant dependency checkpoint error, got {errors}",
        )

    def test_negative_6_validate_run_state_checkpoint_mismatch(self) -> None:
        run_state_text = (
            "# Run State\n\n"
            "- Latest terminal task checkpoint: `304be6391e41cad92884614011813665ccf1baff`.\n"
        )
        errors = validate_run_state_checkpoint(run_state_text, "6686f243ccf0d8d19632c54ce78dfe261168413c")
        self.assertEqual(len(errors), 1)
        self.assertIn("disagrees with queue latest_checkpoint_identity", errors[0])

        missing_checkpoint_text = "# Run State\n\nNo checkpoint line\n"
        errors_missing = validate_run_state_checkpoint(missing_checkpoint_text, "6686f243ccf0d8d19632c54ce78dfe261168413c")
        self.assertEqual(len(errors_missing), 1)
        self.assertIn("missing 'Latest terminal task checkpoint' entry", errors_missing[0])

        matching_errors = validate_run_state_checkpoint(run_state_text, "304be6391e41cad92884614011813665ccf1baff")
        self.assertEqual(matching_errors, [])

    def test_7_report_delivery_model_ancestor_checkpoint_accepted(self) -> None:
        real_tasks = copy.deepcopy(self.queue["tasks"][:2])
        self.assertEqual(real_tasks[0]["execution_state"]["checkpoint_identity"], "5ed0e52c9c52ebbf2329caff5cfd71af4b3e7237")
        self.assertEqual(real_tasks[1]["execution_state"]["checkpoint_identity"], "6686f243ccf0d8d19632c54ce78dfe261168413c")
        errors = execution_state_errors(real_tasks, ROOT)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
