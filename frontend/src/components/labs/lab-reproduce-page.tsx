"use client";

import {useQuery} from "@tanstack/react-query";
import {CheckCircle2, CircleDashed, FileStack, RotateCcw, Workflow} from "lucide-react";
import Link from "next/link";
import {PageHeader} from "@/components/page-header";
import {Button} from "@/components/ui/button";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Document, IngestionRun, Project, QueryHistoryItem} from "@/lib/types";

function ReproStep({complete, label, detail, href}: {complete: boolean; label: string; detail: string; href: string}) {
  const Icon = complete ? CheckCircle2 : CircleDashed;
  return <Link href={href} className="flex gap-3 rounded-lg border border-[var(--border)] bg-[var(--surface)] p-4 hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]">
    <Icon className={complete ? "mt-0.5 size-4 shrink-0 text-[var(--success)]" : "mt-0.5 size-4 shrink-0 text-[var(--ink-disabled)]"} />
    <span className="min-w-0">
      <span className="block text-sm font-semibold text-[var(--ink)]">{label}</span>
      <span className="mt-1 block text-xs leading-5 text-[var(--ink-muted)]">{detail}</span>
    </span>
  </Link>;
}

export function LabReproducePage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=100`)});
  const history = useQuery({queryKey: ["query-history", projectId], queryFn: () => apiFetch<QueryHistoryItem[]>(`/rag/projects/${projectId}/history?limit=100`)});
  const loading = project.isLoading || documents.isLoading || runs.isLoading || history.isLoading;
  const error = project.isError || documents.isError || runs.isError || history.isError;
  if (loading) return <LoadingState label="Loading reproducibility state" rows={5} />;
  if (error) return <ErrorState title="Reproducibility state could not be loaded" description="One or more evidence endpoints returned an error." onRetry={() => void Promise.all([project.refetch(), documents.refetch(), runs.refetch(), history.refetch()])} />;

  const docs = documents.data ?? [];
  const indexed = docs.filter((document) => document.status === "indexed");
  const completedRuns = (runs.data ?? []).filter((run) => run.status === "indexed");
  const queries = history.data ?? [];

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Reproduce"} title="Reproduce" description="Reproducibility checklist from existing source, ingestion, vector, and query evidence. Exportable manifests require future backend support." actions={<Link href={`/projects/${projectId}/artifacts`}><Button><FileStack className="size-4" />View artifacts</Button></Link>} />
    <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <RotateCcw className="size-4 text-[var(--accent)]" />
        <h2 className="mt-3 text-sm font-semibold">Reproduction readiness</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">A Lab is reproducible when its source corpus, ingestion lineage, vector artifacts, and test evidence are inspectable from durable records.</p>
        <div className="mt-5 grid grid-cols-3 gap-2 text-center">
          <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3"><b className="block text-lg">{docs.length}</b><span className="text-[9px] text-[var(--ink-muted)]">Sources</span></div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3"><b className="block text-lg">{completedRuns.length}</b><span className="text-[9px] text-[var(--ink-muted)]">Runs</span></div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3"><b className="block text-lg">{queries.length}</b><span className="text-[9px] text-[var(--ink-muted)]">Tests</span></div>
        </div>
      </section>
      <section className="space-y-3">
        <ReproStep complete={docs.length > 0} label="Source corpus exists" detail={`${docs.length} source records are registered for this Lab.`} href={`/projects/${projectId}/research`} />
        <ReproStep complete={indexed.length > 0} label="Indexed evidence exists" detail={`${indexed.length} sources are indexed and queryable through retrieval.`} href={`/projects/${projectId}/sources`} />
        <ReproStep complete={completedRuns.length > 0} label="Pipeline lineage exists" detail={`${completedRuns.length} completed ingestion runs are available for inspection.`} href={`/projects/${projectId}/artifacts`} />
        <ReproStep complete={queries.length > 0} label="Test evidence exists" detail={`${queries.length} persisted playground tests are available as result evidence.`} href={`/projects/${projectId}/results`} />
      </section>
    </div>
    <section className="rounded-lg border border-[var(--warning-border)] bg-[var(--warning-soft)] p-5">
      <div className="flex items-start gap-3">
        <Workflow className="mt-0.5 size-4 shrink-0 text-[var(--warning)]" />
        <div>
          <h2 className="text-sm font-semibold text-[var(--warning-soft-text)]">Reproduction manifests are planned</h2>
          <p className="mt-2 text-xs leading-5 text-[var(--ink-secondary)]">The current frontend exposes durable evidence, but signed reproduction manifests, environment locks, dataset snapshots, and report exports need matching backend contracts before they can be generated truthfully.</p>
        </div>
      </div>
    </section>
  </div>;
}
