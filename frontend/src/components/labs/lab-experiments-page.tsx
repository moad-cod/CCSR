"use client";

import {useQuery} from "@tanstack/react-query";
import {ArrowRight, BarChart3, Beaker, FileStack, FlaskConical, Gauge, Workflow} from "lucide-react";
import Link from "next/link";
import {MetricCard} from "@/components/metric-card";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Document, IngestionRun, Project, QueryHistoryItem, ResearchExperiment} from "@/lib/types";
import {formatLatency, relativeTime} from "@/lib/utils";

function averageLatency(items: QueryHistoryItem[]) {
  const latencies = items.map((item) => item.latency_ms).filter((value): value is number => typeof value === "number");
  if (!latencies.length) return null;
  return Math.round(latencies.reduce((sum, value) => sum + value, 0) / latencies.length);
}

function percent(part: number, total: number) {
  if (!total) return 0;
  return Math.round((part / total) * 100);
}

function ConfigCard({label, title, detail, status, accent}: {label: string; title: string; detail: string; status: string; accent: string}) {
  return <article className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-4">
    <div className="flex items-start justify-between gap-3">
      <div>
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--ink-muted)]">{label}</p>
        <h2 className="mt-3 text-sm font-semibold text-[var(--ink)]">{title}</h2>
      </div>
      <span className="size-2 rounded-full" style={{backgroundColor: accent}} />
    </div>
    <p className="mt-3 text-xs leading-5 text-[var(--ink-muted)]">{detail}</p>
    <div className="mt-4"><StatusBadge status={status} /></div>
  </article>;
}

export function LabExperimentsPage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const experiments = useQuery({queryKey: ["research-experiments", projectId], queryFn: () => apiFetch<ResearchExperiment[]>(`/projects/${projectId}/research/experiments`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=100`)});
  const history = useQuery({queryKey: ["query-history", projectId], queryFn: () => apiFetch<QueryHistoryItem[]>(`/rag/projects/${projectId}/history?limit=100`)});
  const loading = project.isLoading || experiments.isLoading || documents.isLoading || runs.isLoading || history.isLoading;
  const error = project.isError || experiments.isError || documents.isError || runs.isError || history.isError;
  if (loading) return <LoadingState label="Loading experiments" rows={6} />;
  if (error) return <ErrorState title="Experiments could not be loaded" description="The project evidence endpoints did not return usable responses." onRetry={() => void Promise.all([project.refetch(), experiments.refetch(), documents.refetch(), runs.refetch(), history.refetch()])} />;

  const docs = documents.data ?? [];
  const runItems = runs.data ?? [];
  const queries = history.data ?? [];
  const formalExperiments = experiments.data ?? [];
  const indexed = docs.filter((document) => document.status === "indexed");
  const completedRuns = runItems.filter((run) => run.status === "indexed");
  const failedRuns = runItems.filter((run) => run.status === "failed");
  const avgLatency = averageLatency(queries);
  const cacheHits = queries.filter((query) => query.cache_hit).length;
  const pipelineSuccess = percent(completedRuns.length, runItems.length);
  const retrievalCoverage = percent(indexed.length, docs.length);
  const cacheHitRate = percent(cacheHits, queries.length);
  const readyForComparison = indexed.length > 0 && queries.length > 0;

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Experiments"} title="Experiments" description="Durable experiment definitions alongside current pipeline and query evidence." actions={<Link href={`/projects/${projectId}/test`}><Button><Beaker className="size-4" />Run test</Button></Link>} />
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Experiments" value={formalExperiments.length} detail={`${formalExperiments.filter((item) => item.status === "completed").length} completed`} icon={FlaskConical} />
      <MetricCard label="Corpus coverage" value={`${retrievalCoverage}%`} detail={`${indexed.length}/${docs.length} sources indexed`} icon={FileStack} />
      <MetricCard label="Pipeline success" value={`${pipelineSuccess}%`} detail={`${completedRuns.length}/${runItems.length} indexed runs`} icon={Workflow} />
      <MetricCard label="Mean test latency" value={avgLatency === null ? "n/a" : formatLatency(avgLatency)} detail="From persisted query history" icon={Gauge} />
    </div>
    <section className="grid gap-3 xl:grid-cols-4">
      <ConfigCard label="A · Baseline" title="Ungrounded reference" detail="A baseline model run is not exposed by the current backend. Keep this comparison arm unavailable until a model-only endpoint exists." status="planned" accent="var(--domain-baseline)" />
      <ConfigCard label="B · Retrieval" title="Hybrid retrieval corpus" detail={`${indexed.length} indexed sources are available for grounded tests through the implemented RAG path.`} status={indexed.length ? "ready" : "draft"} accent="var(--domain-cv)" />
      <ConfigCard label="C · Pipeline" title="Durable ingestion evidence" detail={`${runItems.length} pipeline runs record source landing, chunking, embedding, and Qdrant indexing state.`} status={runItems.length ? "available" : "draft"} accent="var(--research-violet)" />
      <ConfigCard label="D · Final" title="Tested research system" detail={`${queries.length} persisted tests can support findings with questions, answers, model metadata, and latency.`} status={readyForComparison ? "ready" : "processing"} accent="var(--domain-final)" />
    </section>
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4">
        <h2 className="text-sm font-semibold">Comparison matrix</h2>
        <p className="mt-1 text-[9px] text-[var(--ink-muted)]">Current system values are real; unavailable baseline cells are intentionally blank.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-xs">
          <thead className="border-b border-[var(--border)] text-[9px] uppercase tracking-[0.12em] text-[var(--ink-muted)]"><tr><th className="px-4 py-3">Metric</th><th className="px-4 py-3">Baseline</th><th className="px-4 py-3">Current Lab</th><th className="px-4 py-3">Finding</th></tr></thead>
          <tbody className="divide-y divide-[var(--border)]">
            {[
              ["Indexed corpus", "Unavailable", `${indexed.length}/${docs.length}`, indexed.length ? "Retrieval tests can cite indexed sources." : "Index sources before comparing."],
              ["Pipeline success", "Unavailable", `${pipelineSuccess}%`, failedRuns.length ? `${failedRuns.length} failed runs need review.` : "No failed runs in current evidence."],
              ["Mean latency", "Unavailable", avgLatency === null ? "n/a" : formatLatency(avgLatency), avgLatency === null ? "Run tests to measure latency." : "Latency is measurable from persisted tests."],
              ["Cache hit rate", "Unavailable", `${cacheHitRate}%`, cacheHits ? "Some answers reuse cached results." : "Current tests were generated fresh or not run."],
            ].map(([metric, baseline, current, finding]) => <tr key={metric} className="hover:bg-[var(--surface-elevated)]"><td className="px-4 py-3 font-medium text-[var(--ink)]">{metric}</td><td className="px-4 py-3 text-[var(--ink-disabled)]">{baseline}</td><td className="px-4 py-3 text-[var(--ink-secondary)]">{current}</td><td className="px-4 py-3 text-[var(--ink-muted)]">{finding}</td></tr>)}
          </tbody>
        </table>
      </div>
    </section>
    <div className="grid gap-4 xl:grid-cols-2">
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
        <div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Recent experiment evidence</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Pipeline runs and interactive tests that can become formal experiment runs later</p></div>
        {formalExperiments.length || runItems.length || queries.length ? <div className="divide-y divide-[var(--border)]">
          {formalExperiments.slice(0, 4).map((experiment) => <Link key={experiment.id} href={`/projects/${projectId}/experiments/${experiment.id}`} className="grid gap-3 p-4 hover:bg-[var(--surface-elevated)] sm:grid-cols-[1fr_auto_auto] sm:items-center"><span className="min-w-0"><span className="block truncate text-xs font-medium">{experiment.name}</span><span className="mt-1 block text-[9px] text-[var(--ink-muted)]">Durable experiment · {relativeTime(experiment.created_at)}</span></span><StatusBadge status={experiment.status} /><span className="text-[10px] text-[var(--accent)]">Inspect<ArrowRight className="inline size-3" /></span></Link>)}
          {runItems.slice(0, 4).map((run) => <Link key={run.ingestion_run_id} href={`/projects/${projectId}/runs/${run.ingestion_run_id}`} className="grid gap-3 p-4 hover:bg-[var(--surface-elevated)] sm:grid-cols-[1fr_auto_auto] sm:items-center"><span className="min-w-0"><span className="mono block truncate text-[10px] text-[var(--ink-secondary)]">{run.ingestion_run_id}</span><span className="mt-1 block text-[9px] text-[var(--ink-muted)]">Pipeline run · {relativeTime(run.created_at)}</span></span><StatusBadge status={run.status} /><span className="text-[10px] text-[var(--accent)]">Inspect<ArrowRight className="inline size-3" /></span></Link>)}
          {queries.slice(0, 4).map((query) => <Link key={query.query_log_id} href={`/projects/${projectId}/history/${query.query_log_id}`} className="grid gap-3 p-4 hover:bg-[var(--surface-elevated)] sm:grid-cols-[1fr_auto_auto] sm:items-center"><span className="min-w-0"><span className="line-clamp-1 text-xs font-medium">{query.question}</span><span className="mt-1 block text-[9px] text-[var(--ink-muted)]">Test result · {relativeTime(query.created_at)}</span></span><span className="text-[10px] text-[var(--ink-secondary)]">{formatLatency(query.latency_ms)}</span><span className="text-[10px] text-[var(--accent)]">Open<ArrowRight className="inline size-3" /></span></Link>)}
        </div> : <EmptyState icon={FlaskConical} title="No experiment evidence yet" description="Index sources and run tests to create comparable evidence." action="Open test" onAction={() => location.assign(`/projects/${projectId}/test`)} />}
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-center gap-2"><BarChart3 className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Configuration readiness plot</h2></div>
        <div className="mt-5 space-y-4">
          {[
            ["Corpus indexed", retrievalCoverage, "var(--domain-cv)"],
            ["Pipeline success", pipelineSuccess, "var(--research-violet)"],
            ["Tests recorded", Math.min(100, queries.length * 20), "var(--accent)"],
            ["Cache reuse", cacheHitRate, "var(--info)"],
          ].map(([label, value, color]) => <div key={label as string}>
            <div className="mb-1 flex items-center justify-between text-[10px]"><span className="text-[var(--ink-muted)]">{label}</span><span className="font-mono text-[var(--ink-secondary)]">{value}%</span></div>
            <div className="h-2 rounded-full bg-[var(--surface-elevated)]"><div className="h-full rounded-full" style={{width: `${value}%`, backgroundColor: color as string}} /></div>
          </div>)}
        </div>
        <div className="mt-5 rounded-lg border border-[var(--warning-border)] bg-[var(--warning-soft)] p-3 text-[10px] leading-5 text-[var(--warning-soft-text)]">Experiment records are now durable. Quality, cost, and model-vs-model plots remain unavailable until workflows write standardized metrics.</div>
      </section>
    </div>
  </div>;
}
