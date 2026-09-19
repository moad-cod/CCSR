"use client";

import {useQuery} from "@tanstack/react-query";
import {Box, Database, FileStack, Settings2, Workflow} from "lucide-react";
import Link from "next/link";
import {IngestionRunsPage} from "@/modules/ragforge/ingestion-runs-page";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {apiFetch} from "@/lib/api";
import type {Chunker, GenericRun, Project, WorkflowDefinition} from "@/lib/types";
import {relativeTime} from "@/lib/utils";

export function ProjectPipelinesPage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const chunkers = useQuery({queryKey: ["chunkers"], queryFn: () => apiFetch<Chunker[]>("/chunkers")});
  const workflows = useQuery({queryKey: ["workflows", projectId], queryFn: () => apiFetch<WorkflowDefinition[]>(`/workflows?project_id=${projectId}`)});
  const genericRuns = useQuery({queryKey: ["generic-runs", projectId], queryFn: () => apiFetch<GenericRun[]>(`/runs?project_id=${projectId}&limit=100`)});
  const recommended = chunkers.data?.find((chunker) => chunker.default) ?? chunkers.data?.find((chunker) => chunker.id === "paragraph");

  return <div className="space-y-8">
    <div className="mx-auto max-w-7xl space-y-6">
      <PageHeader
        eyebrow={project.data?.name ?? "Project pipelines"}
        title="Pipelines"
        description="Configure source ingestion defaults, review backend-supported processing behavior, and inspect project runs without mixing them into global monitoring."
        actions={<Link href={`/projects/${projectId}/sources`}><Button><FileStack className="size-4" />Add sources</Button></Link>}
      />
      <div className="grid gap-4 lg:grid-cols-3">
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <div className="flex items-center gap-2"><Workflow className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Execution model</h2></div>
          <p className="mt-3 text-xs leading-5 text-[var(--ink-muted)]">File sources run through the durable backend ingestion pipeline. The frontend follows status through run records and SSE recovery.</p>
          <div className="mt-4"><StatusBadge status="available" /></div>
        </section>
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <div className="flex items-center gap-2"><Settings2 className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Chunking default</h2></div>
          <p className="mt-3 text-xs leading-5 text-[var(--ink-muted)]">{recommended ? `${recommended.name}: ${recommended.short_description}` : "Chunker catalog is loading or unavailable."}</p>
          <p className="mt-3 text-[9px] leading-4 text-[var(--ink-muted)]">Project-level pipeline configuration is not persisted by the current backend; selected chunkers are stored on document versions.</p>
        </section>
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <div className="flex items-center gap-2"><Database className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Artifacts</h2></div>
          <p className="mt-3 text-xs leading-5 text-[var(--ink-muted)]">The run detail view exposes Bronze, Silver, Gold, and Qdrant completion state as reported by the backend.</p>
          <Link href={`/projects/${projectId}/sources`} className="mt-4 inline-flex text-[10px] text-[var(--accent)] hover:text-[var(--accent-hover)]">Open source manager</Link>
        </section>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)]"><div className="border-b border-[var(--border)] p-4"><div className="flex items-center gap-2"><Box className="size-4 text-[var(--research-violet)]" /><h2 className="text-sm font-semibold">Registered workflows</h2></div><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Versioned definitions enabled by this project&apos;s capabilities.</p></div><div className="divide-y divide-[var(--border)]">{workflows.data?.map((workflow) => <article key={workflow.id} className="p-4"><div className="flex items-start justify-between gap-3"><div><h3 className="text-xs font-semibold">{workflow.name}</h3><p className="mt-1 font-mono text-[8px] text-[var(--ink-muted)]">{workflow.workflow_key}@{workflow.version} · {workflow.engine}</p></div><StatusBadge status={workflow.publication_status} /></div><p className="mt-3 text-[10px] leading-5 text-[var(--ink-muted)]">{workflow.description}</p><div className="mt-3 flex flex-wrap gap-1.5">{workflow.artifact_types.map((type) => <span key={type} className="rounded-md border border-[var(--border)] px-2 py-1 text-[8px] text-[var(--ink-secondary)]">{type}</span>)}</div></article>)}{!workflows.isLoading && !workflows.data?.length ? <p className="p-6 text-center text-xs text-[var(--ink-muted)]">No published workflows are enabled.</p> : null}</div></section>
        <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)]"><div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Generic workflow runs</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Engine-neutral execution records linked to detailed capability runs.</p></div><div className="divide-y divide-[var(--border)]">{genericRuns.data?.map((run) => <article key={run.id} className="flex items-center gap-3 p-4"><div className="min-w-0 flex-1"><p className="truncate font-mono text-[9px] text-[var(--ink-secondary)]">{run.id}</p><p className="mt-1 text-[9px] text-[var(--ink-muted)]">{run.engine} · {relativeTime(run.created_at)} · quota {String(run.quota_cost)}</p>{run.error_message ? <p className="mt-2 text-[9px] text-[var(--danger-soft-text)]">{run.error_message}</p> : null}</div><StatusBadge status={run.status} /></article>)}{!genericRuns.isLoading && !genericRuns.data?.length ? <p className="p-6 text-center text-xs text-[var(--ink-muted)]">No generic workflow runs yet.</p> : null}</div></section>
      </div>
    </div>
    <IngestionRunsPage projectId={projectId} />
  </div>;
}
