"use client";

import {useQuery} from "@tanstack/react-query";
import {Archive, Database, FileStack, Workflow} from "lucide-react";
import Link from "next/link";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Document, IngestionRun, Project} from "@/lib/types";
import {relativeTime} from "@/lib/utils";

export function LabArtifactsPage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=100`)});
  const loading = project.isLoading || documents.isLoading || runs.isLoading;
  const error = project.isError || documents.isError || runs.isError;
  if (loading) return <LoadingState label="Loading lab artifacts" rows={5} />;
  if (error) return <ErrorState title="Artifacts could not be loaded" description="Source and run endpoints returned an error." onRetry={() => void Promise.all([project.refetch(), documents.refetch(), runs.refetch()])} />;

  const docs = documents.data ?? [];
  const runItems = runs.data ?? [];

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Artifacts"} title="Artifacts" description="Source, pipeline, and vector collection artifacts available through the current CCSR control plane." actions={<Link href={`/projects/${projectId}/pipelines`}><Button><Workflow className="size-4" />View runs</Button></Link>} />
    <div className="grid gap-4 lg:grid-cols-3">
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--research-violet)]">Collection</p>
        <h2 className="mt-3 text-sm font-semibold">Vector store</h2>
        <p className="mono mt-2 break-all text-[10px] leading-5 text-[var(--ink-muted)]">{project.data?.qdrant_collection}</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--accent)]">Sources</p>
        <h2 className="mt-3 text-sm font-semibold">{docs.length} source artifacts</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">Documents and source metadata registered for this Lab.</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--info)]">Runs</p>
        <h2 className="mt-3 text-sm font-semibold">{runItems.length} pipeline artifacts</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">Durable ingestion attempts and stage progress records.</p>
      </section>
    </div>
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Artifact registry</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Real source and run objects, not synthetic research assets</p></div>
      {docs.length || runItems.length ? <div className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
        {docs.slice(0, 9).map((document) => <Link key={document.document_id} href={`/projects/${projectId}/documents/${document.document_id}`} className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4 hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]"><div className="flex items-center gap-2"><FileStack className="size-4 text-[var(--accent)]" /><span className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--ink-muted)]">Source</span></div><h3 className="mt-3 line-clamp-2 text-sm font-semibold">{document.filename ?? document.document_id}</h3><div className="mt-3 flex items-center justify-between gap-2"><StatusBadge status={document.status} /><span className="text-[9px] text-[var(--ink-disabled)]">{relativeTime(document.updated_at)}</span></div></Link>)}
        {runItems.slice(0, 6).map((run) => <Link key={run.ingestion_run_id} href={`/projects/${projectId}/runs/${run.ingestion_run_id}`} className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4 hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]"><div className="flex items-center gap-2"><Database className="size-4 text-[var(--research-violet)]" /><span className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--ink-muted)]">Pipeline run</span></div><h3 className="mono mt-3 truncate text-sm font-semibold">{run.ingestion_run_id}</h3><div className="mt-3 flex items-center justify-between gap-2"><StatusBadge status={run.status} /><span className="text-[9px] text-[var(--ink-disabled)]">{relativeTime(run.created_at)}</span></div></Link>)}
      </div> : <EmptyState icon={Archive} title="No artifacts yet" description="Add and process sources to create source records, run evidence, and vector artifacts." action="Add sources" onAction={() => location.assign(`/projects/${projectId}/sources`)} />}
    </section>
  </div>;
}
