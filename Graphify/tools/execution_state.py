#!/usr/bin/env python3
"""Durable execution-state rules for the authoritative implementation queue."""

from __future__ import annotations

import copy
import json
from pathlib import Path, PurePosixPath
from typing import Any


ALLOWED_DISPOSITIONS = ("NOT STARTED", "COMPLETE", "NOT APPLICABLE", "BLOCKED")
TERMINAL_DISPOSITIONS = frozenset({"COMPLETE", "NOT APPLICABLE"})
EXECUTION_STATE_FIELDS = (
    "disposition",
    "evidence_references",
    "checkpoint_identity",
    "blocked_reason",
    "not_applicable_basis",
)


class ExecutionStateError(ValueError):
    """Raised when persisted task execution state is unsafe to regenerate."""


def default_execution_state() -> dict[str, Any]:
    return {
        "disposition": "NOT STARTED",
        "evidence_references": [],
        "checkpoint_identity": None,
        "blocked_reason": None,
        "not_applicable_basis": None,
    }


def execution_state_contract() -> dict[str, Any]:
    return {
        "authority": "Each task's execution_state is durable mutable state; generated task-definition fields remain planning contracts.",
        "task_id_field": "stable_task_id",
        "required_fields": list(EXECUTION_STATE_FIELDS),
        "allowed_dispositions": list(ALLOWED_DISPOSITIONS),
        "terminal_dispositions": sorted(TERMINAL_DISPOSITIONS),
        "complete_rule": "All semantic dependencies must be terminal; every required_evidence_artifact must be referenced and exist; checkpoint_identity is required.",
        "not_applicable_rule": "All semantic dependencies must be terminal; evidence_references, checkpoint_identity and not_applicable_basis are required.",
        "blocked_rule": "blocked_reason is required and the blocked task remains the next task; evidence_references and checkpoint_identity are either both present or both absent.",
    }


def _ordered(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(tasks, key=lambda task: (task.get("ordering_index", task.get("execution_order", -1)), task.get("stable_task_id", "")))


def _repo_relative_evidence_path(reference: Any) -> tuple[PurePosixPath | None, str | None]:
    if not isinstance(reference, str) or not reference.strip():
        return None, "must be a non-empty repository-relative path"
    normalized = reference.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return None, "must stay within the repository"
    return path, None


def execution_state_errors(tasks: list[dict[str, Any]], evidence_root: Path | None = None) -> list[str]:
    """Validate per-task state, dependency closure, and referenced evidence."""
    errors: list[str] = []
    task_by_id: dict[str, dict[str, Any]] = {}
    for task in tasks:
        task_id = task.get("stable_task_id")
        if not isinstance(task_id, str) or not task_id:
            errors.append("Task without a stable_task_id cannot carry execution state")
            continue
        if task_id in task_by_id:
            errors.append(f"Duplicate execution-state task ID: {task_id}")
        task_by_id[task_id] = task

    for task_id, task in task_by_id.items():
        state = task.get("execution_state")
        if not isinstance(state, dict):
            errors.append(f"{task_id}: execution_state must be an object")
            continue
        missing = [field for field in EXECUTION_STATE_FIELDS if field not in state]
        extra = sorted(set(state) - set(EXECUTION_STATE_FIELDS))
        if missing:
            errors.append(f"{task_id}: execution_state missing fields {missing}")
        if extra:
            errors.append(f"{task_id}: execution_state has unsupported fields {extra}")

        disposition = state.get("disposition")
        evidence = state.get("evidence_references")
        checkpoint = state.get("checkpoint_identity")
        blocked_reason = state.get("blocked_reason")
        not_applicable_basis = state.get("not_applicable_basis")
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{task_id}: unsupported execution disposition {disposition!r}")
            continue
        if not isinstance(evidence, list):
            errors.append(f"{task_id}: evidence_references must be a list")
            evidence = []
        elif len(evidence) != len(set(str(item) for item in evidence)):
            errors.append(f"{task_id}: duplicate evidence reference")

        valid_references: list[tuple[str, PurePosixPath]] = []
        for reference in evidence:
            path, path_error = _repo_relative_evidence_path(reference)
            if path_error:
                errors.append(f"{task_id}: evidence reference {reference!r} {path_error}")
            elif path is not None:
                valid_references.append((str(reference), path))
        if evidence_root is not None and disposition != "NOT STARTED":
            for reference, path in valid_references:
                if not evidence_root.joinpath(*path.parts).is_file():
                    errors.append(f"{task_id}: evidence file does not exist: {reference}")

        if disposition == "NOT STARTED":
            if evidence or checkpoint is not None or blocked_reason is not None or not_applicable_basis is not None:
                errors.append(f"{task_id}: NOT STARTED must not retain execution evidence, checkpoint, blocked reason, or not-applicable basis")
        elif disposition == "COMPLETE":
            required_evidence = task.get("required_evidence_artifacts", [])
            missing_evidence = sorted(set(required_evidence) - set(evidence))
            if missing_evidence:
                errors.append(f"{task_id}: COMPLETE is missing required evidence references {missing_evidence}")
            if not isinstance(checkpoint, str) or not checkpoint.strip():
                errors.append(f"{task_id}: COMPLETE requires checkpoint_identity")
            if blocked_reason is not None or not_applicable_basis is not None:
                errors.append(f"{task_id}: COMPLETE cannot carry blocked_reason or not_applicable_basis")
        elif disposition == "NOT APPLICABLE":
            if not evidence:
                errors.append(f"{task_id}: NOT APPLICABLE requires evidence_references")
            if not isinstance(checkpoint, str) or not checkpoint.strip():
                errors.append(f"{task_id}: NOT APPLICABLE requires checkpoint_identity")
            if not isinstance(not_applicable_basis, str) or not not_applicable_basis.strip():
                errors.append(f"{task_id}: NOT APPLICABLE requires not_applicable_basis")
            if blocked_reason is not None:
                errors.append(f"{task_id}: NOT APPLICABLE cannot carry blocked_reason")
        elif disposition == "BLOCKED":
            if not isinstance(blocked_reason, str) or not blocked_reason.strip():
                errors.append(f"{task_id}: BLOCKED requires blocked_reason")
            if not_applicable_basis is not None:
                errors.append(f"{task_id}: BLOCKED cannot carry not_applicable_basis")
            if bool(evidence) != bool(isinstance(checkpoint, str) and checkpoint.strip()):
                errors.append(f"{task_id}: BLOCKED evidence_references and checkpoint_identity must be present together")

        if disposition != "NOT STARTED":
            for dependency in task.get("semantic_dependencies", []):
                dependency_task = task_by_id.get(dependency)
                if dependency_task is None:
                    errors.append(f"{task_id}: unknown execution dependency {dependency}")
                    continue
                dependency_state = dependency_task.get("execution_state")
                dependency_disposition = dependency_state.get("disposition") if isinstance(dependency_state, dict) else None
                if dependency_disposition not in TERMINAL_DISPOSITIONS:
                    errors.append(f"{task_id}: {disposition} is invalid while dependency {dependency} is {dependency_disposition!r}")
    return errors


def select_next_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first dependency-valid nonterminal task; BLOCKED is not skipped."""
    task_by_id = {task.get("stable_task_id"): task for task in tasks}
    for task in _ordered(tasks):
        state = task.get("execution_state") or {}
        if state.get("disposition") in TERMINAL_DISPOSITIONS:
            continue
        dependencies_ready = all(
            (task_by_id.get(dependency, {}).get("execution_state") or {}).get("disposition") in TERMINAL_DISPOSITIONS
            for dependency in task.get("semantic_dependencies", [])
        )
        if dependencies_ready:
            return task
    return None


def summarize_execution_state(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {disposition: 0 for disposition in ALLOWED_DISPOSITIONS}
    for task in tasks:
        disposition = (task.get("execution_state") or {}).get("disposition")
        if disposition in counts:
            counts[disposition] += 1
    next_task = select_next_task(tasks)
    terminal_count = sum(counts[item] for item in TERMINAL_DISPOSITIONS)
    if tasks and terminal_count == len(tasks):
        implementation_status = "COMPLETE"
    elif next_task and next_task["execution_state"]["disposition"] == "BLOCKED":
        implementation_status = "BLOCKED"
    elif terminal_count or counts["BLOCKED"]:
        implementation_status = "IN PROGRESS"
    else:
        implementation_status = "NOT STARTED"
    terminal_tasks = [
        task for task in _ordered(tasks)
        if (task.get("execution_state") or {}).get("disposition") in TERMINAL_DISPOSITIONS
    ]
    latest_checkpoint = terminal_tasks[-1]["execution_state"]["checkpoint_identity"] if terminal_tasks else None
    return {
        "implementation_status": implementation_status,
        "execution_state_counts": counts,
        "terminal_task_count": terminal_count,
        "next_task_id": next_task.get("stable_task_id") if next_task else None,
        "next_task_disposition": next_task.get("execution_state", {}).get("disposition") if next_task else None,
        "latest_checkpoint_identity": latest_checkpoint,
    }


def aggregate_implementation_status(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return "NOT STARTED"
    dispositions = [(task.get("execution_state") or {}).get("disposition") for task in tasks]
    if all(item in TERMINAL_DISPOSITIONS for item in dispositions):
        return "COMPLETE"
    if "BLOCKED" in dispositions:
        return "BLOCKED"
    if any(item in TERMINAL_DISPOSITIONS for item in dispositions):
        return "IN PROGRESS"
    return "NOT STARTED"


def apply_queue_summary(queue: dict[str, Any], summary: dict[str, Any]) -> None:
    for field in ("implementation_status", "execution_state_counts", "terminal_task_count", "next_task_id", "next_task_disposition", "latest_checkpoint_identity"):
        queue[field] = summary[field]
    queue["execution_state_contract"] = execution_state_contract()


def merge_execution_states(
    generated_tasks: list[dict[str, Any]],
    existing_queue: dict[str, Any] | None,
    evidence_root: Path | None = None,
) -> dict[str, Any]:
    """Merge valid persisted state by stable ID without carrying task definitions forward."""
    generated_ids = [task.get("stable_task_id") for task in generated_tasks]
    if len(generated_ids) != len(set(generated_ids)):
        raise ExecutionStateError("Generated task definitions contain duplicate stable_task_id values")

    preserved: dict[str, dict[str, Any]] = {}
    if existing_queue is not None:
        existing_tasks = existing_queue.get("tasks")
        if not isinstance(existing_tasks, list):
            raise ExecutionStateError("Existing IMPLEMENTATION_QUEUE.json tasks must be a list")
        existing_ids = [task.get("stable_task_id") for task in existing_tasks if isinstance(task, dict)]
        if len(existing_ids) != len(set(existing_ids)):
            raise ExecutionStateError("Existing IMPLEMENTATION_QUEUE.json contains duplicate task IDs")
        unknown = sorted(set(existing_ids) - set(generated_ids))
        if unknown:
            raise ExecutionStateError(f"Existing execution state refers to unknown task IDs: {unknown}")
        for task in existing_tasks:
            if isinstance(task, dict) and "execution_state" in task:
                preserved[task["stable_task_id"]] = copy.deepcopy(task["execution_state"])

    for task in generated_tasks:
        task_id = task["stable_task_id"]
        task["execution_state"] = preserved.get(task_id, default_execution_state())
    errors = execution_state_errors(generated_tasks, evidence_root)
    if errors:
        raise ExecutionStateError("Invalid persisted implementation execution state:\n" + "\n".join(f"- {error}" for error in errors))
    return summarize_execution_state(generated_tasks)


def regenerate_fixture_queue(input_path: Path, output_path: Path, evidence_root: Path) -> None:
    """Exercise the generator merge against an isolated queue fixture."""
    existing_queue = json.loads(input_path.read_text(encoding="utf-8"))
    generated_tasks = copy.deepcopy(existing_queue.get("tasks", []))
    for task in generated_tasks:
        task.pop("execution_state", None)
    summary = merge_execution_states(generated_tasks, existing_queue, evidence_root)
    regenerated = copy.deepcopy(existing_queue)
    regenerated["schema_version"] = 4
    regenerated["tasks"] = generated_tasks
    apply_queue_summary(regenerated, summary)
    output_path.write_text(json.dumps(regenerated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
