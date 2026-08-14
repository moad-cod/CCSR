"use client";

import {useQuery} from "@tanstack/react-query";
import {ArrowRight, BookOpenText, FileStack, Workflow} from "lucide-react";
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

export function LabResearchPage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=20`)});
  const loading = project.isLoading || documents.isLoading || runs.isLoading;
  const error = project.isError || documents.isError || runs.isError;
  if (loading) return <LoadingState label="Loading lab research" rows={5} />;
  if (error) return <ErrorState title="Research context could not be loaded" description="One or more project endpoints returned an error." onRetry={() => void Promise.all([project.refetch(), documents.refetch(), runs.refetch()])} />;

  const docs = documents.data ?? [];
  const indexed = docs.filter((document) => document.status === "indexed");
  const latestRun = runs.data?.[0];

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Research"} title="Research" description="Source corpus, methodology evidence, and the current implemented RAG research foundation for this Lab." actions={<Link href={`/projects/${projectId}/sources`}><Button><FileStack className="size-4" />Manage sources</Button></Link>} />
    <div className="grid gap-4 lg:grid-cols-3">
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <BookOpenText className="size-4 text-[var(--research-violet)]" />
        <h2 className="mt-3 text-sm font-semibold">Research corpus</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">{docs.length} source objects are registered for this Lab. {indexed.length} are indexed and ready for retrieval-backed testing.</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <Workflow className="size-4 text-[var(--accent)]" />
        <h2 className="mt-3 text-sm font-semibold">Methodology path</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">Current methodology is source ingestion, chunking, hybrid retrieval, playground testing, citations, and persisted retrieval traces.</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <FileStack className="size-4 text-[var(--info)]" />
        <h2 className="mt-3 text-sm font-semibold">Latest pipeline evidence</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">{latestRun ? `Latest run ${latestRun.status.replaceAll("_", " ")} ${relativeTime(latestRun.created_at)}.` : "No ingestion run evidence exists yet."}</p>
      </section>
    </div>
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="flex items-center justify-between border-b border-[var(--border)] p-4"><div><h2 className="text-sm font-semibold">Sources and papers</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Real source records from the current backend</p></div><Link href={`/projects/${projectId}/sources`} className="text-[10px] text-[var(--accent)] hover:text-[var(--accent-hover)]">Open source manager</Link></div>
      {docs.length ? <div className="divide-y divide-[var(--border)]">{docs.slice(0, 10).map((document) => <Link key={document.document_id} href={`/projects/${projectId}/documents/${document.document_id}`} className="grid gap-3 p-4 hover:bg-[var(--surface-elevated)] sm:grid-cols-[1fr_auto_auto] sm:items-center"><span className="min-w-0"><span className="block truncate text-xs font-medium">{document.filename ?? document.document_id}</span><span className="mono mt-1 block truncate text-[8px] text-[var(--ink-disabled)]">{document.document_id}</span></span><StatusBadge status={document.status} /><span className="inline-flex items-center gap-1 text-[10px] text-[var(--accent)]">Inspect<ArrowRight className="size-3" /></span></Link>)}</div> : <EmptyState icon={FileStack} title="No research sources yet" description="Add papers, datasets, notes, or source documents before defining experiments." action="Add sources" onAction={() => location.assign(`/projects/${projectId}/sources`)} />}
    </section>
  </div>;
}
