"use client";

import {useQuery} from "@tanstack/react-query";
import {BarChart3, CheckCircle2, CircleDot, MessageSquareText, Timer, Workflow} from "lucide-react";
import Link from "next/link";
import {MetricCard} from "@/components/metric-card";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {IngestionRun, Project, QueryHistoryItem} from "@/lib/types";
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

function PlotBar({label, value, color, detail}: {label: string; value: number; color: string; detail: string}) {
  return <div>
    <div className="mb-1 flex items-center justify-between gap-3 text-[10px]"><span className="text-[var(--ink-muted)]">{label}</span><span className="text-[var(--ink-secondary)]">{detail}</span></div>
    <div className="h-2 rounded-full bg-[var(--surface-elevated)]"><div className="h-full rounded-full" style={{width: `${value}%`, backgroundColor: color}} /></div>
  </div>;
}

export function LabResultsPage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const history = useQuery({queryKey: ["query-history", projectId], queryFn: () => apiFetch<QueryHistoryItem[]>(`/rag/projects/${projectId}/history?limit=100`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=100`)});
  const loading = project.isLoading || history.isLoading || runs.isLoading;
  const error = project.isError || history.isError || runs.isError;
  if (loading) return <LoadingState label="Loading lab results" rows={5} />;
  if (error) return <ErrorState title="Results could not be loaded" description="The current project evidence endpoints did not return usable responses." onRetry={() => void Promise.all([project.refetch(), history.refetch(), runs.refetch()])} />;

  const queries = history.data ?? [];
  const runItems = runs.data ?? [];
  const completedRuns = runItems.filter((run) => run.status === "indexed");
  const failedRuns = runItems.filter((run) => run.status === "failed");
  const avgLatency = averageLatency(queries);
  const cached = queries.filter((query) => query.cache_hit).length;
  const answered = queries.filter((query) => query.answer).length;
  const generated = queries.length - cached;
  const pipelineSuccess = percent(completedRuns.length, runItems.length);
  const answerCoverage = percent(answered, queries.length);
  const cacheHitRate = percent(cached, queries.length);
  const generatedRate = percent(generated, queries.length);
  const latestQuery = queries[0];

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Results"} title="Results" description="Current result evidence from playground queries and completed ingestion runs. Formal experiment metrics will appear when backend evaluation contracts exist." actions={<Link href={`/projects/${projectId}/test`}><Button><MessageSquareText className="size-4" />Run test</Button></Link>} />
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Playground results" value={queries.length} detail="Persisted query records" icon={MessageSquareText} />
      <MetricCard label="Average latency" value={avgLatency === null ? "n/a" : formatLatency(avgLatency)} detail="From recorded query latency" icon={Timer} />
      <MetricCard label="Cached answers" value={cached} detail={`${cacheHitRate}% cache hit rate`} icon={BarChart3} />
      <MetricCard label="Indexed runs" value={completedRuns.length} detail="Completed pipeline executions" icon={Workflow} />
    </div>
    <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-center gap-2"><BarChart3 className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Result plots</h2></div>
        <div className="mt-5 space-y-4">
          <PlotBar label="Answered tests" value={answerCoverage} color="var(--success)" detail={`${answered}/${queries.length}`} />
          <PlotBar label="Generated answers" value={generatedRate} color="var(--accent)" detail={`${generated}/${queries.length}`} />
          <PlotBar label="Cache hits" value={cacheHitRate} color="var(--info)" detail={`${cached}/${queries.length}`} />
          <PlotBar label="Indexed runs" value={pipelineSuccess} color="var(--research-violet)" detail={`${completedRuns.length}/${runItems.length}`} />
        </div>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-center gap-2"><CheckCircle2 className="size-4 text-[var(--success)]" /><h2 className="text-sm font-semibold">Findings</h2></div>
        <ul className="mt-5 space-y-3">
          <li className="flex gap-2 text-xs leading-5 text-[var(--ink-muted)]"><CircleDot className="mt-0.5 size-3.5 shrink-0 text-[var(--accent)]" />{queries.length ? `${queries.length} persisted tests are available for result inspection.` : "No persisted tests exist yet; run the Lab Test workflow first."}</li>
          <li className="flex gap-2 text-xs leading-5 text-[var(--ink-muted)]"><CircleDot className="mt-0.5 size-3.5 shrink-0 text-[var(--research-violet)]" />{avgLatency === null ? "Latency findings are unavailable until queries record latency." : `Mean observed latency is ${formatLatency(avgLatency)} across measurable tests.`}</li>
          <li className="flex gap-2 text-xs leading-5 text-[var(--ink-muted)]"><CircleDot className="mt-0.5 size-3.5 shrink-0 text-[var(--info)]" />{failedRuns.length ? `${failedRuns.length} failed pipeline runs may limit result reproducibility.` : "No failed pipeline runs appear in the current result evidence."}</li>
          <li className="flex gap-2 text-xs leading-5 text-[var(--ink-muted)]"><CircleDot className="mt-0.5 size-3.5 shrink-0 text-[var(--success)]" />{latestQuery ? `Latest finding candidate: ${latestQuery.question}` : "A latest finding will appear after the first test query."}</li>
        </ul>
      </section>
    </div>
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Comparison summary</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Implemented RAG evidence compared against unsupported baseline slots</p></div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-xs">
          <thead className="border-b border-[var(--border)] text-[9px] uppercase tracking-[0.12em] text-[var(--ink-muted)]"><tr><th className="px-4 py-3">Dimension</th><th className="px-4 py-3">Baseline</th><th className="px-4 py-3">Current Lab</th><th className="px-4 py-3">State</th></tr></thead>
          <tbody className="divide-y divide-[var(--border)]">
            <tr className="hover:bg-[var(--surface-elevated)]"><td className="px-4 py-3 font-medium text-[var(--ink)]">Answer generation</td><td className="px-4 py-3 text-[var(--ink-disabled)]">Unavailable</td><td className="px-4 py-3 text-[var(--ink-secondary)]">{queries.length} persisted tests</td><td className="px-4 py-3"><StatusBadge status={queries.length ? "available" : "draft"} /></td></tr>
            <tr className="hover:bg-[var(--surface-elevated)]"><td className="px-4 py-3 font-medium text-[var(--ink)]">Retrieval evidence</td><td className="px-4 py-3 text-[var(--ink-disabled)]">Unavailable</td><td className="px-4 py-3 text-[var(--ink-secondary)]">History detail links expose citations and traces</td><td className="px-4 py-3"><StatusBadge status={queries.length ? "ready" : "draft"} /></td></tr>
            <tr className="hover:bg-[var(--surface-elevated)]"><td className="px-4 py-3 font-medium text-[var(--ink)]">Pipeline reliability</td><td className="px-4 py-3 text-[var(--ink-disabled)]">Unavailable</td><td className="px-4 py-3 text-[var(--ink-secondary)]">{pipelineSuccess}% indexed completion</td><td className="px-4 py-3"><StatusBadge status={failedRuns.length ? "experimental" : "ready"} /></td></tr>
            <tr className="hover:bg-[var(--surface-elevated)]"><td className="px-4 py-3 font-medium text-[var(--ink)]">Quality score</td><td className="px-4 py-3 text-[var(--ink-disabled)]">Unavailable</td><td className="px-4 py-3 text-[var(--ink-secondary)]">No evaluator contract yet</td><td className="px-4 py-3"><StatusBadge status="planned" /></td></tr>
          </tbody>
        </table>
      </div>
    </section>
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Recent result evidence</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Questions, answers, latency, and model metadata from the implemented RAG path</p></div>
      {queries.length ? <div className="divide-y divide-[var(--border)]">{queries.slice(0, 8).map((query) => <Link key={query.query_log_id} href={`/projects/${projectId}/history/${query.query_log_id}`} className="block p-4 hover:bg-[var(--surface-elevated)]"><p className="line-clamp-2 text-xs font-medium leading-5">{query.question}</p><p className="mt-2 line-clamp-2 text-[10px] leading-5 text-[var(--ink-muted)]">{query.answer ?? "No persisted answer."}</p><div className="mt-3 flex flex-wrap gap-2 text-[9px] text-[var(--ink-disabled)]"><span>{formatLatency(query.latency_ms)}</span><span>{query.cache_hit ? "cached" : "generated"}</span><span>{query.model ?? "model unavailable"}</span><span>{relativeTime(query.created_at)}</span></div></Link>)}</div> : <EmptyState icon={BarChart3} title="No results yet" description="Run a playground test after indexing sources to create persisted result evidence." action="Open test" onAction={() => location.assign(`/projects/${projectId}/test`)} />}
    </section>
  </div>;
}
