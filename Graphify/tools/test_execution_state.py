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
    execution_state_errors,
    merge_execution_states,
    select_next_task,
    summarize_execution_state,
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
