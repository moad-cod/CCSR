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
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Recent result evidence</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Questions, answers, latency, and model metadata from the implemented RAG path</p></div>
      {queries.length ? <div className="divide-y divide-[var(--border)]">{queries.slice(0, 8).map((query) => <Link key={query.query_log_id} href={`/projects/${projectId}/history/${query.query_log_id}`} className="block p-4 hover:bg-[var(--surface-elevated)]"><p className="line-clamp-2 text-xs font-medium leading-5">{query.question}</p><p className="mt-2 line-clamp-2 text-[10px] leading-5 text-[var(--ink-muted)]">{query.answer ?? "No persisted answer."}</p><div className="mt-3 flex flex-wrap gap-2 text-[9px] text-[var(--ink-disabled)]"><span>{formatLatency(query.latency_ms)}</span><span>{query.cache_hit ? "cached" : "generated"}</span><span>{query.model ?? "model unavailable"}</span><span>{relativeTime(query.created_at)}</span></div></Link>)}</div> : <EmptyState icon={BarChart3} title="No results yet" description="Run a playground test after indexing sources to create persisted result evidence." action="Open test" onAction={() => location.assign(`/projects/${projectId}/test`)} />}
    </section>
  </div>;
}
