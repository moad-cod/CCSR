"use client";

import {useQuery} from "@tanstack/react-query";
import {Activity, ArrowRight, Beaker, Boxes, CircleDot, Database, FlaskConical, MessageSquareText, TimerReset} from "lucide-react";
import Link from "next/link";
import {useState} from "react";
import {MetricCard} from "@/components/metric-card";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {WorkspaceEntry} from "@/components/workspace/workspace-entry";
import {apiFetch} from "@/lib/api";
import type {Document, IngestionRun, Project, QueryHistoryItem} from "@/lib/types";
import {cn, relativeTime} from "@/lib/utils";

type VariantId = "baseline" | "retrieval" | "adaptation" | "final";

type TestVariant = {
  id: VariantId;
  label: string;
  title: string;
  system: string;
  status: string;
  executable: boolean;
  accent: string;
  detail: string;
};

function percent(part: number, total: number) {
  if (!total) return 0;
  return Math.round((part / total) * 100);
}

function ReadinessBar({label, value, total, color}: {label: string; value: number; total: number; color: string}) {
  const progress = percent(value, total);
  return <div>
    <div className="mb-1 flex items-center justify-between gap-3 text-[10px]"><span className="text-[var(--ink-muted)]">{label}</span><span className="font-mono text-[var(--ink-secondary)]">{value}/{total}</span></div>
    <div className="h-2 rounded-full bg-[var(--surface-elevated)]" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}><div className="h-full rounded-full" style={{width: `${progress}%`, backgroundColor: color}} /></div>
  </div>;
}

function VariantCard({variant, selected, onSelect}: {variant: TestVariant; selected: boolean; onSelect: () => void}) {
  return <button
    type="button"
    onClick={onSelect}
    aria-pressed={selected}
    aria-label={`Select ${variant.title} configuration: ${variant.system}`}
    className={cn(
      "group rounded-lg border bg-[var(--surface-elevated)] p-4 text-left transition hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]",
      selected ? "border-[var(--accent-border)] bg-[var(--surface-hover)]" : "border-[var(--border)]",
    )}
  >
    <div className="flex items-start justify-between gap-3">
      <div className="flex min-w-0 items-center gap-2">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-md border font-mono text-[11px] font-semibold" style={{borderColor: variant.accent, color: variant.accent}}>{variant.label}</span>
        <div className="min-w-0">
          <p className="font-mono text-[9px] uppercase tracking-[0.14em]" style={{color: variant.accent}}>{variant.title}</p>
          <h3 className="mt-1 truncate text-sm font-semibold text-[var(--ink)]">{variant.system}</h3>
        </div>
      </div>
      <StatusBadge status={variant.status} />
    </div>
    <p className="mt-3 line-clamp-3 text-xs leading-5 text-[var(--ink-muted)]">{variant.detail}</p>
    <div className="mt-4 flex items-center gap-2 text-[9px] text-[var(--ink-disabled)]">
      <CircleDot className="size-3" style={{color: variant.accent}} />
      {variant.executable ? "Uses the implemented interactive playground" : "Comparison slot is not executable yet"}
    </div>
  </button>;
}

export function LabTestPage({projectId}: {projectId: string}) {
  const [selectedVariantId, setSelectedVariantId] = useState<VariantId>("retrieval");
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=100`)});
  const history = useQuery({queryKey: ["query-history", projectId], queryFn: () => apiFetch<QueryHistoryItem[]>(`/rag/projects/${projectId}/history?limit=100`)});
  const loading = project.isLoading || documents.isLoading || runs.isLoading || history.isLoading;
  const error = project.isError || documents.isError || runs.isError || history.isError;

  if (loading) return <LoadingState label="Loading test lab" rows={5} />;
  if (error) return <ErrorState title="Test Lab could not be loaded" description="Project, source, run, or query-history endpoints returned an error." onRetry={() => void Promise.all([project.refetch(), documents.refetch(), runs.refetch(), history.refetch()])} />;

  const docs = documents.data ?? [];
  const runItems = runs.data ?? [];
  const queries = history.data ?? [];
  const indexedDocs = docs.filter((document) => document.status === "indexed");
  const activeRuns = runItems.filter((run) => run.status === "queued" || run.status === "running" || run.status === "landed");
  const completedRuns = runItems.filter((run) => run.status === "indexed");
  const latestQuery = queries[0];
  const retrievalReady = indexedDocs.length > 0;
  const finalReady = retrievalReady && queries.length > 0;

  const variants: TestVariant[] = [
    {id: "baseline", label: "A", title: "Baseline", system: "Ungrounded model", status: "planned", executable: false, accent: "var(--domain-baseline)", detail: "A model-only baseline endpoint is not exposed by the current backend, so this arm stays labeled as planned."},
    {id: "retrieval", label: "B", title: "Retrieval", system: "Current RAG", status: retrievalReady ? "ready" : "draft", executable: retrievalReady, accent: "var(--domain-cv)", detail: `${indexedDocs.length} indexed sources can be used by the implemented retrieval-backed playground.`},
    {id: "adaptation", label: "C", title: "Adaptation", system: "QLoRA adapter", status: "planned", executable: false, accent: "var(--research-violet)", detail: "Adapter and fine-tuning variants are represented as a comparison slot until an execution contract exists."},
    {id: "final", label: "D", title: "Final", system: "Tested RAG system", status: finalReady ? "ready" : "processing", executable: retrievalReady, accent: "var(--domain-final)", detail: `${queries.length} persisted tests can support the current final-system evidence path.`},
  ];
  const selectedVariant = variants.find((variant) => variant.id === selectedVariantId) ?? variants[1];

  return <div className="space-y-6">
    <PageHeader
      eyebrow={project.data?.name ?? "Interactive test"}
      title="Test"
      description="Interactive testing for implemented RAG systems and research variants, with unsupported comparison arms labeled plainly."
      actions={<Link href={`/projects/${projectId}/results`}><Button variant="secondary"><MessageSquareText className="size-4" />View results</Button></Link>}
    />

    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Indexed sources" value={indexedDocs.length} detail={`${percent(indexedDocs.length, docs.length)}% of source records`} icon={Database} />
      <MetricCard label="Active runs" value={activeRuns.length} detail="Ingestion work affecting readiness" icon={Activity} />
      <MetricCard label="Persisted tests" value={queries.length} detail="Saved playground evidence" icon={MessageSquareText} />
      <MetricCard label="Executable variant" value={selectedVariant.executable ? selectedVariant.label : "n/a"} detail={selectedVariant.system} icon={Beaker} />
    </div>

    <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-center gap-2"><FlaskConical className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Experimental variants</h2></div>
        <p className="mt-1 text-[9px] text-[var(--ink-muted)]">Select a research configuration and run the implemented path when it is available.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {variants.map((variant) => <VariantCard key={variant.id} variant={variant} selected={variant.id === selectedVariant.id} onSelect={() => setSelectedVariantId(variant.id)} />)}
        </div>
      </div>

      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="font-mono text-[9px] uppercase tracking-[0.14em]" style={{color: selectedVariant.accent}}>Selected configuration</p>
            <h2 className="mt-2 text-base font-semibold text-[var(--ink)]">{selectedVariant.label} - {selectedVariant.system}</h2>
          </div>
          <StatusBadge status={selectedVariant.status} />
        </div>
        <p className="mt-3 text-xs leading-5 text-[var(--ink-muted)]">{selectedVariant.detail}</p>
        <div className="mt-5 space-y-4">
          <ReadinessBar label="Corpus indexed" value={indexedDocs.length} total={docs.length} color="var(--domain-cv)" />
          <ReadinessBar label="Runs completed" value={completedRuns.length} total={runItems.length} color="var(--research-violet)" />
          <ReadinessBar label="Tests recorded" value={Math.min(queries.length, 10)} total={10} color="var(--domain-final)" />
        </div>
        <div className="mt-5 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-[var(--ink)]"><TimerReset className="size-3.5 text-[var(--accent)]" />Latest evidence</div>
          <p className="mt-2 line-clamp-2 text-xs leading-5 text-[var(--ink-muted)]">{latestQuery ? latestQuery.question : "No persisted test question exists yet."}</p>
          <p className="mt-2 text-[9px] text-[var(--ink-disabled)]">{latestQuery ? relativeTime(latestQuery.created_at) : "Run the playground to create evidence."}</p>
          {latestQuery ? <Link href={`/projects/${projectId}/history/${latestQuery.query_log_id}`} className="mt-3 inline-flex items-center gap-1 text-[10px] font-medium text-[var(--accent)] hover:text-[var(--accent-hover)]">Open evidence<ArrowRight className="size-3" /></Link> : null}
        </div>
        {retrievalReady ? <Link href={`/projects/${projectId}/sources`} className="mt-4 inline-flex text-[10px] font-medium text-[var(--accent)] hover:text-[var(--accent-hover)]">Inspect indexed sources</Link> : <Link href={`/projects/${projectId}/sources`} className="mt-4 inline-flex text-[10px] font-medium text-[var(--accent)] hover:text-[var(--accent-hover)]">Add or index sources</Link>}
      </div>
    </section>

    <section className="overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--background)]">
      <div className="flex flex-col gap-3 border-b border-[var(--border)] bg-[var(--surface)] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold">Interactive test environment</h2>
          <p className="mt-1 text-[9px] text-[var(--ink-muted)]">The executable surface below runs the current retrieval-backed system, preserves query history, and exposes citations.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={retrievalReady ? "ready" : "draft"} />
          <span className="inline-flex items-center gap-1.5 rounded-md border border-[var(--border)] bg-[var(--surface-elevated)] px-2 py-1 text-[9px] text-[var(--ink-muted)]"><Boxes className="size-3" />{indexedDocs.length} indexed</span>
        </div>
      </div>
      <div className="h-[calc(100dvh-26rem)] min-h-[640px]">
        <WorkspaceEntry projectId={projectId} />
      </div>
    </section>
  </div>;
}
