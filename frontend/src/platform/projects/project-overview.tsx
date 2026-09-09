"use client";

import {useQuery} from "@tanstack/react-query";
import {Archive, ArrowRight, BookOpenText, Database, FlaskConical, MessageSquareText, ScrollText, Workflow} from "lucide-react";
import Link from "next/link";
import {MetricCard} from "@/components/metric-card";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {ProjectOverviewContract, RAGProjectOverview} from "@/lib/types";
import {formatLatency, relativeTime} from "@/lib/utils";
import {hasProjectCapability} from "@/platform/navigation/navigation";

export function ProjectOverview({projectId}: {projectId: string}) {
  const platform = useQuery({
    queryKey: ["project-overview", projectId],
    queryFn: () => apiFetch<ProjectOverviewContract>(`/projects/${projectId}/overview`),
  });
  const hasRAGForge = hasProjectCapability(platform.data?.project, "ragforge");
  const rag = useQuery({
    queryKey: ["ragforge", "project-overview", projectId],
    queryFn: () => apiFetch<RAGProjectOverview>(`/rag/projects/${projectId}/overview`),
    enabled: Boolean(platform.data && hasRAGForge),
  });
  const loading = platform.isLoading || (hasRAGForge && rag.isLoading);
  const error = platform.isError || !platform.data || (hasRAGForge && rag.isError);
  if (loading) return <LoadingState label="Loading project overview" rows={6} />;
  if (error || !platform.data) return <ErrorState title="Project overview could not be loaded" description="The platform or an enabled capability summary returned an error." onRetry={() => void Promise.all([platform.refetch(), ...(hasRAGForge ? [rag.refetch()] : [])])} />;

  const {project, counts} = platform.data;
  const ragSummary = rag.data?.summary;
  const nextAction = counts.studies === 0
    ? {label: "Define research", href: `/projects/${projectId}/research`, Icon: BookOpenText, description: "Create a durable study, question, and hypothesis for this project."}
    : hasRAGForge && !ragSummary?.document_count
      ? {label: "Add RAG sources", href: `/projects/${projectId}/sources`, Icon: Database, description: "Add papers or datasets to the enabled RAGForge workspace."}
      : hasRAGForge && !ragSummary?.indexed_document_count
        ? {label: "Review pipelines", href: `/projects/${projectId}/pipelines`, Icon: Workflow, description: "Sources exist but none are ready for retrieval yet."}
        : hasRAGForge
          ? {label: "Open playground", href: `/projects/${projectId}/playground`, Icon: MessageSquareText, description: "Test grounded answers against indexed research evidence."}
          : {label: "Plan experiment", href: `/projects/${projectId}/experiments`, Icon: FlaskConical, description: "Add an experiment to the durable research hierarchy."};
  const NextIcon = nextAction.Icon;

  return <div className="space-y-6">
    <PageHeader eyebrow="Project overview" title={project.name} description="Capability-neutral research state with separate summaries for each enabled product module." actions={<Link href={nextAction.href}><Button><ArrowRight className="size-4" />{nextAction.label}</Button></Link>} />
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      <MetricCard label="Studies" value={counts.studies} detail="Durable research programs" icon={BookOpenText} />
      <MetricCard label="Experiments" value={counts.experiments} detail="Research executions" icon={FlaskConical} />
      <MetricCard label="Runs" value={counts.runs} detail="Generic workflow runs" icon={Workflow} />
      <MetricCard label="Artifacts" value={counts.artifacts} detail="Registered evidence" icon={Archive} />
      <MetricCard label="Publications" value={counts.publications} detail="Private, draft, or public" icon={ScrollText} />
    </div>

    <section className="rounded-xl border border-[var(--accent-border)] bg-[var(--surface)] p-5">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-start gap-3"><span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]"><NextIcon className="size-5" /></span><div><p className="text-[9px] font-semibold uppercase tracking-[.14em] text-[var(--ink-muted)]">Next action</p><h2 className="mt-1 text-sm font-semibold">{nextAction.label}</h2><p className="mt-1 text-xs leading-5 text-[var(--ink-muted)]">{nextAction.description}</p></div></div>
        <Link href={nextAction.href} className="inline-flex h-9 items-center justify-center gap-2 rounded-lg bg-[var(--accent-soft)] px-3 text-xs font-medium text-[var(--accent-hover)] hover:bg-[var(--accent-muted)]">Continue<ArrowRight className="size-3.5" /></Link>
      </div>
    </section>

    {hasRAGForge && rag.data ? <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4"><p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--accent)]">RAGForge capability</p><h2 className="mt-1 text-sm font-semibold">Retrieval workspace</h2></div>
      <div className="grid gap-3 p-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Indexed sources" value={`${rag.data.summary.indexed_document_count}/${rag.data.summary.document_count}`} detail="Ready for retrieval" icon={Database} />
        <MetricCard label="Active ingestion" value={rag.data.summary.active_run_count} detail="Non-terminal runs" icon={Workflow} />
        <MetricCard label="Failed ingestion" value={rag.data.summary.failed_run_count} detail="Runs requiring attention" icon={Archive} />
        <MetricCard label="Queries" value={rag.data.query_count} detail="Persisted playground history" icon={MessageSquareText} />
      </div>
      <div className="grid border-t border-[var(--border)] xl:grid-cols-2">
        <div className="border-b border-[var(--border)] xl:border-b-0 xl:border-r"><div className="flex items-center justify-between p-4"><div><h3 className="text-sm font-semibold">Recent ingestion</h3><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Module-owned pipeline activity</p></div><Link href={`/projects/${projectId}/pipelines`} className="text-[10px] text-[var(--accent)]">View pipelines</Link></div><div className="divide-y divide-[var(--border)]">{rag.data.recent_runs.map((run) => <Link key={run.ingestion_run_id} href={`/projects/${projectId}/runs/${run.ingestion_run_id}`} className="flex items-center gap-3 px-4 py-3 hover:bg-[var(--surface-elevated)]"><span className="min-w-0 flex-1"><span className="mono block truncate text-[9px] text-[var(--ink-secondary)]">{run.ingestion_run_id}</span><span className="mt-1 block text-[8px] text-[var(--ink-disabled)]">{relativeTime(run.created_at)}</span></span><StatusBadge status={run.status} /></Link>)}{!rag.data.recent_runs.length ? <p className="p-8 text-center text-[10px] text-[var(--ink-muted)]">No ingestion runs yet.</p> : null}</div></div>
        <div><div className="flex items-center justify-between p-4"><div><h3 className="text-sm font-semibold">Latest playground result</h3><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Module-owned retrieval evidence</p></div><Link href={`/projects/${projectId}/playground`} className="text-[10px] text-[var(--accent)]">Open playground</Link></div>{rag.data.latest_query ? <Link href={`/projects/${projectId}/history/${rag.data.latest_query.query_log_id}`} className="block border-t border-[var(--border)] p-4 hover:bg-[var(--surface-elevated)]"><p className="line-clamp-2 text-xs font-medium leading-5">{rag.data.latest_query.question}</p><div className="mt-3 flex flex-wrap gap-2 text-[9px] text-[var(--ink-disabled)]"><span>{formatLatency(rag.data.latest_query.latency_ms)}</span><span>{rag.data.latest_query.cache_hit ? "cached" : "generated"}</span><span>{rag.data.latest_query.model ?? "model unavailable"}</span></div></Link> : <p className="border-t border-[var(--border)] p-8 text-center text-[10px] text-[var(--ink-muted)]">No playground queries yet.</p>}</div>
      </div>
    </section> : <section className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-5"><p className="text-sm font-semibold">No product capability enabled</p><p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">This project remains available for platform research, experiments, artifacts, runs, and publications.</p></section>}
  </div>;
}
