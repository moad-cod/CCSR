"""In-process registry for approved workflow versions and engine adapters."""

from __future__ import annotations

from app.platform.execution.contracts import (
    ExecutionAdapter,
    RegisteredWorkflowDefinition,
    WorkflowHandler,
)


class ExecutionRegistry:
    def __init__(self) -> None:
        self._definitions: dict[tuple[str, str], RegisteredWorkflowDefinition] = {}
        self._adapters: dict[str, ExecutionAdapter] = {}
        self._handlers: dict[tuple[str, str], WorkflowHandler] = {}

    def register_workflow(
        self,
        definition: RegisteredWorkflowDefinition,
        *,
        replace: bool = False,
    ) -> None:
        key = (definition.key.strip(), definition.version.strip())
        if not all(key):
            raise ValueError("Workflow key and version must not be empty")
        if key in self._definitions and not replace:
            raise ValueError(f"Workflow {key[0]}@{key[1]} is already registered")
        self._definitions[key] = definition

    def register_adapter(self, adapter: ExecutionAdapter) -> None:
        self._adapters[adapter.engine] = adapter

    def register_handler(
        self,
        engine: str,
        reference: str,
        handler: WorkflowHandler,
    ) -> None:
        self._handlers[(engine, reference)] = handler

    def get_workflow(
        self,
        key: str,
        version: str | None = None,
    ) -> RegisteredWorkflowDefinition | None:
        if version is not None:
            return self._definitions.get((key, version))
        candidates = [
            definition
            for (workflow_key, _), definition in self._definitions.items()
            if workflow_key == key and definition.publication_status == "published"
        ]
        return max(candidates, key=lambda item: item.version, default=None)

    def definitions(self) -> tuple[RegisteredWorkflowDefinition, ...]:
        return tuple(self._definitions.values())

    def adapter_for(self, engine: str) -> ExecutionAdapter | None:
        return self._adapters.get(engine)

    def handler_for(self, engine: str, reference: str) -> WorkflowHandler | None:
        return self._handlers.get((engine, reference))


execution_registry = ExecutionRegistry()
