"use client";

import {Check, Circle, Copy, LoaderCircle, RefreshCw, TriangleAlert} from "lucide-react";
import {useMutation, useQueryClient} from "@tanstack/react-query";
import Link from "next/link";
import {toast} from "sonner";
import {Button} from "@/components/ui/button";
import {StatusBadge} from "@/components/status-badge";
import {apiFetch} from "@/lib/api";
import type {Document, IngestionRun} from "@/lib/types";
import {cn, relativeTime} from "@/lib/utils";

const stages = [
  {label: "Uploaded", complete: (run: IngestionRun) => Boolean(run.created_at)},
  {label: "Bronze landed", complete: (run: IngestionRun) => run.progress.bronze},
  {label: "Parsing", complete: (run: IngestionRun) => run.progress.silver},
  {label: "Chunking", complete: (run: IngestionRun) => run.progress.silver},
  {label: "Silver completed", complete: (run: IngestionRun) => run.progress.silver},
  {label: "Embedding", complete: (run: IngestionRun) => run.progress.gold},
  {label: "Gold completed", complete: (run: IngestionRun) => run.progress.gold},
  {label: "Qdrant indexing", complete: (run: IngestionRun) => run.progress.qdrant},
  {label: "Indexed", complete: (run: IngestionRun) => run.status === "indexed"},
];

export function IngestionPipeline({run, document, projectId, compact = false}: {run: IngestionRun; document?: Document; projectId: string; compact?: boolean}) {
  const queryClient = useQueryClient();
  const failed = run.status === "failed" || run.status === "cancelled";
  const completed = stages.map((stage) => stage.complete(run));
  const current = completed.findIndex((value) => !value);
  const embedding = run.embedding_progress;
  const retry = useMutation({mutationFn: () => apiFetch<IngestionRun>(`/ingest/runs/${run.ingestion_run_id}/retry`, {method: "POST"}), onSuccess: async () => {await Promise.all([queryClient.invalidateQueries({queryKey: ["ingestion-runs", projectId]}), queryClient.invalidateQueries({queryKey: ["ingestion-run", run.ingestion_run_id]})]); toast.success("Retry queued from the durable Bronze artifact");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to retry ingestion")});
  return <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-live="polite">
    <div className="flex flex-wrap items-start justify-between gap-3"><div className="min-w-0"><h3 className="truncate text-xs font-semibold">{document?.filename ?? "Document ingestion"}</h3><p className="mono mt-1 truncate text-[8px] text-[var(--ink-disabled)]">{run.ingestion_run_id}</p></div><StatusBadge status={run.status} /></div>
    <div className={cn("mt-4 grid gap-2", compact ? "grid-cols-3 sm:grid-cols-5" : "sm:grid-cols-3 lg:grid-cols-9")}>
      {stages.map((stage, index) => {const done = completed[index]; const active = !failed && current === index; return <div key={stage.label} className="relative flex items-center gap-2 lg:flex-col lg:text-center"><span className={cn("flex size-6 shrink-0 items-center justify-center rounded-full border", done ? "border-[var(--accent)] bg-[var(--accent)] text-[var(--ink-inverse)]" : active ? "border-[var(--info)] bg-[var(--info-soft)] text-[var(--info)]" : failed && current === index ? "border-[var(--danger-border)] bg-[var(--danger-soft)] text-[var(--danger)]" : "border-[var(--border)] text-[var(--border-strong)]")}>{done ? <Check className="size-3.5" /> : active ? <LoaderCircle className="size-3.5 animate-spin" /> : <Circle className="size-2.5" />}</span><span className={cn("text-[9px] leading-4", done ? "text-[var(--ink-secondary)]" : active ? "text-[var(--info)]" : "text-[var(--ink-disabled)]")}>{stage.label}</span></div>;})}
    </div>
    {!compact && embedding ? <div className="mt-4 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3 text-[9px] text-[var(--ink-secondary)]"><div className="flex flex-wrap items-center gap-x-4 gap-y-1"><span className="font-medium text-[var(--ink-secondary)]">Embedding {embedding.stage.replaceAll("_", " ")}</span><span>{embedding.embedded_chunks}/{embedding.total_chunks} chunks</span>{typeof embedding.embedded_batches === "number" && typeof embedding.total_batches === "number" ? <span>{embedding.embedded_batches}/{embedding.total_batches} batches</span> : null}<span className="mono break-all">{embedding.embedding_model}</span></div><div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[var(--ink-muted)]">{embedding.embedding_backend ? <span>{embedding.embedding_backend}</span> : null}{embedding.embedding_device ? <span>Device {embedding.embedding_device}</span> : null}{embedding.embedding_dimension ? <span>{embedding.embedding_dimension} dimensions</span> : null}{embedding.last_heartbeat_at ? <span>Heartbeat {relativeTime(embedding.last_heartbeat_at)}</span> : null}</div>{embedding.error_message ? <p className="mt-2 text-[var(--danger-soft-text)]">{embedding.error_message}</p> : null}</div> : null}
    {!compact ? <div className="mt-4 grid gap-2 border-t border-[var(--border)] pt-3 text-[9px] text-[var(--ink-muted)] sm:grid-cols-3"><span>Created {relativeTime(run.created_at)}</span><span>Started {run.started_at ? relativeTime(run.started_at) : "not reported"}</span><span>Finished {run.finished_at ? relativeTime(run.finished_at) : "not yet"}</span></div> : null}
    {failed ? <div className="mt-4 rounded-lg border border-[var(--danger-border)] bg-[var(--danger-soft)] p-3"><div className="flex gap-2.5"><TriangleAlert className="mt-0.5 size-4 shrink-0 text-[var(--danger)]" /><div className="min-w-0 flex-1"><p className="text-[11px] font-semibold text-[var(--danger-soft-text)]">Document processing failed</p><p className="mt-1 text-[10px] leading-5 text-[var(--danger-soft-text)]">{run.error_message || "The pipeline stopped before indexing completed."}</p><details className="mt-2"><summary className="cursor-pointer text-[9px] text-[var(--ink-secondary)]">Technical details</summary><div className="mono mt-2 rounded-md bg-[var(--background-code)] p-2 text-[8px] leading-4 text-[var(--ink-secondary)]">Run: {run.ingestion_run_id}<br />DAG: {run.airflow_dag_run_id || "not assigned"}<br />Retry reuses the landed Bronze artifact and does not create a new version.</div></details><div className="mt-3 flex flex-wrap gap-2"><Button size="sm" variant="secondary" disabled={retry.isPending || run.status !== "failed"} onClick={() => retry.mutate()}><RefreshCw className={cn("size-3.5", retry.isPending && "animate-spin")} />Retry from Bronze</Button><Button size="sm" variant="ghost" onClick={() => {void navigator.clipboard?.writeText(`Run: ${run.ingestion_run_id}\nStatus: ${run.status}\nDocument: ${run.document_id}\nError: ${run.error_message || "none"}`); toast.success("Diagnostics copied");}}><Copy className="size-3.5" />Copy diagnostics</Button><Link href={`/projects/${projectId}/documents/${run.document_id}`} className="flex h-9 items-center px-3 text-[10px] text-[var(--accent)] hover:text-[var(--accent-hover)]">Open document</Link></div></div></div></div> : null}
  </section>;
}
