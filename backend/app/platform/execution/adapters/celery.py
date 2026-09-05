"""Generic adapter for module-registered Celery workflow dispatchers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.platform.execution.contracts import (
    ExecutionReceipt,
    RegisteredWorkflowDefinition,
    WorkflowHandler,
)


class CeleryExecutionAdapter:
    engine = "celery"

    async def dispatch(
        self,
        _workflow: RegisteredWorkflowDefinition,
        payload: Mapping[str, Any],
        handler: WorkflowHandler | None,
    ) -> ExecutionReceipt | None:
        if handler is None:
            raise RuntimeError("No Celery handler is registered for this workflow")
        external_id = await handler(payload)
        if not external_id:
            return None
        return ExecutionReceipt(external_execution_id=str(external_id))
