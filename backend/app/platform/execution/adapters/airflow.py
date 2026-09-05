"""Generic Airflow REST adapter."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.platform.execution.contracts import (
    ExecutionReceipt,
    RegisteredWorkflowDefinition,
    WorkflowHandler,
)


class AirflowExecutionAdapter:
    engine = "airflow"

    def __init__(self, client_factory=None) -> None:
        self._client_factory = client_factory or httpx.AsyncClient

    async def dispatch(
        self,
        workflow: RegisteredWorkflowDefinition,
        payload: Mapping[str, Any],
        _handler: WorkflowHandler | None,
    ) -> ExecutionReceipt | None:
        if not settings.AIRFLOW_API_URL:
            return None
        attempt_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        identity = str(payload.get("ingestion_run_id") or payload.get("run_id") or "run")
        prefix = workflow.external_id_prefix or workflow.key.replace(".", "_")
        external_id = f"{prefix}__{identity}__{attempt_id}"
        base_url = settings.AIRFLOW_API_URL.rstrip("/")
        async with self._client_factory(timeout=10.0) as client:
            token_response = await client.post(
                f"{base_url}/auth/token",
                json={
                    "username": settings.AIRFLOW_USERNAME,
                    "password": settings.AIRFLOW_PASSWORD,
                },
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]
            response = await client.post(
                f"{base_url}/api/v2/dags/{workflow.handler_reference}/dagRuns",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "dag_run_id": external_id,
                    "conf": dict(payload),
                    "logical_date": None,
                },
            )
            response.raise_for_status()
        return ExecutionReceipt(external_execution_id=external_id)
