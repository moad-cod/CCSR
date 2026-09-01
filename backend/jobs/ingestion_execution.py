"""Dependency-light helpers shared by the Airflow ingestion DAG."""

from __future__ import annotations

from collections.abc import Mapping
import os
import signal


def profile_environment_name(
    environment_name: str,
    plan: Mapping,
    *,
    environment: Mapping[str, str] | None = None,
) -> str:
    """Return a configured profile override or the generic command name."""
    values = os.environ if environment is None else environment
    command_suffix = str(plan.get("command_suffix") or "").strip().upper()
    if not command_suffix:
        return environment_name
    stem = environment_name.removesuffix("_CMD")
    candidate = f"{stem}_{command_suffix}_CMD"
    return candidate if str(values.get(candidate, "")).strip() else environment_name


def build_job_environment(
    plan: Mapping,
    *,
    base_environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Expose planner hints to local commands and external worker wrappers."""
    environment = dict(os.environ if base_environment is None else base_environment)
    environment.update(
        {
            "RAGFORGE_INGESTION_PROFILE": str(plan["profile"]),
            "RAGFORGE_INGESTION_TECHNIQUE": str(plan["technique_id"]),
            "RAGFORGE_INGESTION_RESOURCE_CLASS": str(plan["resource_class"]),
            "RAGFORGE_EMBEDDING_BATCH_SIZE": str(plan["embedding_batch_size"]),
            "RAGFORGE_EMBEDDING_MAX_BATCH_SIZE": str(
                environment.get("RAGFORGE_EMBEDDING_MAX_BATCH_SIZE")
                or environment.get("EMBEDDING_MAX_BATCH_SIZE", "64")
            ),
            "RAGFORGE_EMBEDDING_TIMEOUT_SECONDS": str(
                environment.get("EMBEDDING_TIMEOUT_SECONDS", "900")
            ),
            "RAGFORGE_INGESTION_MAX_PARALLELISM": str(plan["max_parallelism"]),
        }
    )
    return environment


def subprocess_failure_message(
    environment_name: str,
    returncode: int,
    *,
    stdout: str | None = None,
    stderr: str | None = None,
) -> str:
    """Describe command failures, including actionable Unix signal details."""
    detail = (stderr or stdout or "").strip()
    if returncode < 0:
        signal_number = -returncode
        try:
            signal_name = signal.Signals(signal_number).name
        except ValueError:
            signal_name = f"signal {signal_number}"
        message = f"{environment_name} was terminated by {signal_name}"
        if signal_number == signal.SIGKILL:
            message += " (the container may have exceeded its memory limit)"
    else:
        message = f"{environment_name} failed with exit code {returncode}"
    return f"{message}: {detail}" if detail else message
