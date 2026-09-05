"""Stable contracts between platform execution and workflow modules."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from pydantic import BaseModel


ExecutionEngine = Literal["airflow", "celery"]
WorkflowPublicationStatus = Literal["draft", "published", "retired"]
WorkflowHandler = Callable[[Mapping[str, Any]], Awaitable[str | None]]


@dataclass(frozen=True)
class RegisteredWorkflowDefinition:
    key: str
    version: str
    capability_key: str
    name: str
    description: str
    engine: ExecutionEngine
    input_model: type[BaseModel]
    output_schema: Mapping[str, Any]
    handler_reference: str
    resource_requirements: Mapping[str, Any]
    runtime_limit_seconds: int | None = None
    member_execution_allowed: bool = False
    artifact_types: tuple[str, ...] = ()
    publication_status: WorkflowPublicationStatus = "published"
    external_id_prefix: str | None = None


@dataclass(frozen=True)
class ExecutionReceipt:
    external_execution_id: str


class ExecutionAdapter(Protocol):
    engine: ExecutionEngine

    async def dispatch(
        self,
        workflow: RegisteredWorkflowDefinition,
        payload: Mapping[str, Any],
        handler: WorkflowHandler | None,
    ) -> ExecutionReceipt | None: ...
