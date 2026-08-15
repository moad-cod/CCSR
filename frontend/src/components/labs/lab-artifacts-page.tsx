"use client";

import {useQueries, useQuery} from "@tanstack/react-query";
import type {LucideIcon} from "lucide-react";
import {Archive, BarChart3, BookOpenText, Boxes, Code2, Database, FileCode2, FileJson, NotebookTabs, Package, Settings2, Workflow} from "lucide-react";
import Link from "next/link";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Badge} from "@/components/ui/badge";
import {Button} from "@/components/ui/button";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Document, DocumentVersion, IngestionRun, Project, QueryHistoryItem} from "@/lib/types";
import {relativeTime} from "@/lib/utils";

type ArtifactTone = "neutral" | "success" | "warning" | "info";
type ArtifactCardProps = {
  type: string;
  title: string;
  detail: string;
  icon: LucideIcon;
  meta?: string;
  status?: string;
  href?: string;
  tone?: ArtifactTone;
};

function ArtifactCard({type, title, detail, icon: Icon, meta, status, href, tone = "neutral"}: ArtifactCardProps) {
  const body = <article className="h-full rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4 transition hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]">
    <div className="flex items-start justify-between gap-3">
      <div className="flex min-w-0 items-center gap-2">
        <Icon className="size-4 shrink-0 text-[var(--accent)]" />
        <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--ink-muted)]">{type}</span>
      </div>
      {status ? <StatusBadge status={status} /> : <Badge tone={tone} className="text-[9px]">{tone === "warning" ? "planned" : "available"}</Badge>}
    </div>
    <h3 className="mt-3 line-clamp-2 text-sm font-semibold leading-5 text-[var(--ink)]">{title}</h3>
    <p className="mt-2 line-clamp-3 text-xs leading-5 text-[var(--ink-muted)]">{detail}</p>
    {meta ? <p className="mono mt-4 truncate text-[9px] text-[var(--ink-disabled)]" title={meta}>{meta}</p> : null}
  </article>;
  return href ? <Link href={href}>{body}</Link> : body;
}

function StagePlot({label, value, total, color}: {label: string; value: number; total: number; color: string}) {
  const progress = total ? Math.round((value / total) * 100) : 0;
  return <div>
    <div className="mb-1 flex items-center justify-between text-[10px]"><span className="text-[var(--ink-muted)]">{label}</span><span className="font-mono text-[var(--ink-secondary)]">{value}/{total}</span></div>
    <div className="h-2 rounded-full bg-[var(--surface-elevated)]"><div className="h-full rounded-full" style={{width: `${progress}%`, backgroundColor: color}} /></div>
  </div>;
}

function unique(values: (string | null | undefined)[]) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

export function LabArtifactsPage({projectId}: {projectId: string}) {
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=100`)});
  const history = useQuery({queryKey: ["query-history", projectId], queryFn: () => apiFetch<QueryHistoryItem[]>(`/rag/projects/${projectId}/history?limit=100`)});
  const docs = documents.data ?? [];
  const versionQueries = useQueries({
    queries: docs.slice(0, 12).map((document) => ({
      queryKey: ["document-versions", document.document_id],
      queryFn: () => apiFetch<DocumentVersion[]>(`/documents/${document.document_id}/versions`),
      staleTime: 30_000,
    })),
  });
  const loading = project.isLoading || documents.isLoading || runs.isLoading || history.isLoading;
  const error = project.isError || documents.isError || runs.isError || history.isError;
  if (loading) return <LoadingState label="Loading lab artifacts" rows={5} />;
  if (error) return <ErrorState title="Artifacts could not be loaded" description="Source, run, or query-history endpoints returned an error." onRetry={() => void Promise.all([project.refetch(), documents.refetch(), runs.refetch(), history.refetch()])} />;

  const runItems = runs.data ?? [];
  const queries = history.data ?? [];
  const versions = versionQueries.flatMap((query) => query.data ?? []);
  const indexed = docs.filter((document) => document.status === "indexed");
  const modelNames = unique([...versions.map((version) => version.embedding_model), ...queries.map((query) => query.model)]);
  const chunkers = unique(versions.map((version) => version.chunker_id));
  const providers = unique(queries.map((query) => query.provider));
  const bronze = runItems.filter((run) => run.progress.bronze).length;
  const silver = runItems.filter((run) => run.progress.silver).length;
  const gold = runItems.filter((run) => run.progress.gold).length;
  const qdrant = runItems.filter((run) => run.progress.qdrant).length;
  const hasArtifacts = docs.length || runItems.length || queries.length || versions.length;
  const codeReferences: {label: string; path: string; icon: LucideIcon}[] = [
    {label: "Query API", path: "backend/app/api/query.py", icon: FileCode2},
    {label: "Document API", path: "backend/app/api/documents.py", icon: FileCode2},
    {label: "Pipeline artifacts", path: "backend/app/services/pipeline_artifacts.py", icon: FileJson},
    {label: "Retriever", path: "backend/app/services/retriever.py", icon: FileCode2},
    {label: "Frontend workspace", path: "frontend/src/components/workspace/knowledge-workspace.tsx", icon: FileCode2},
  ];

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Artifacts"} title="Artifacts" description="Models, datasets, configurations, reports, plots, and code references tied to real CCSR control-plane evidence." actions={<Link href={`/projects/${projectId}/pipelines`}><Button><Workflow className="size-4" />View runs</Button></Link>} />

    <div className="grid gap-4 lg:grid-cols-4">
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--research-violet)]">Datasets</p>
        <h2 className="mt-3 text-sm font-semibold">{docs.length} source objects</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">{indexed.length} indexed sources are ready for retrieval-backed tests.</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--accent)]">Models</p>
        <h2 className="mt-3 text-sm font-semibold">{modelNames.length || "No"} model references</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">Embedding and generation model names from versions and query history.</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--info)]">Reports</p>
        <h2 className="mt-3 text-sm font-semibold">{queries.length + runItems.length} evidence records</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--ink-muted)]">Query results and pipeline runs act as current report evidence.</p>
      </section>
      <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--domain-ai-systems)]">Configs</p>
        <h2 className="mt-3 text-sm font-semibold">{chunkers.length + providers.length + 1} configuration signals</h2>
        <p className="mono mt-2 truncate text-[10px] leading-5 text-[var(--ink-muted)]">{project.data?.qdrant_collection}</p>
      </section>
    </div>

    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Artifact registry</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Typed research objects from implemented backend evidence; unavailable registries are labeled plainly.</p></div>
      {hasArtifacts ? <div className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
        {docs.slice(0, 6).map((document) => <ArtifactCard key={`dataset:${document.document_id}`} type="Dataset" title={document.filename ?? document.document_id} detail={`${document.source_type ?? "source"} document registered in the Lab corpus.`} icon={Boxes} status={document.status} href={`/projects/${projectId}/documents/${document.document_id}`} meta={document.document_id} />)}
        {modelNames.length ? modelNames.slice(0, 4).map((model) => <ArtifactCard key={`model:${model}`} type="Model" title={model} detail="Observed in document version metadata or persisted query history." icon={Package} tone="info" meta="Model registry is not first-class yet." />) : <ArtifactCard type="Model" title="No model artifact recorded yet" detail="Run ingestion or tests to expose embedding and generation model names." icon={Package} tone="warning" />}
        {chunkers.map((chunker) => <ArtifactCard key={`config:${chunker}`} type="Config" title={chunker} detail="Chunking configuration observed on a document version." icon={Settings2} tone="info" />)}
        {providers.map((provider) => <ArtifactCard key={`provider:${provider}`} type="Config" title={provider} detail="Generation provider observed in persisted query history." icon={Settings2} tone="info" />)}
        <ArtifactCard type="Config" title="Qdrant collection" detail="Project-scoped vector collection assigned by the backend." icon={Database} tone="info" meta={project.data?.qdrant_collection} />
        {queries.slice(0, 4).map((query) => <ArtifactCard key={`report:${query.query_log_id}`} type="Report" title={query.question} detail={query.answer ?? "No persisted answer text is available for this test."} icon={BookOpenText} href={`/projects/${projectId}/history/${query.query_log_id}`} meta={`${query.model ?? "model unavailable"} · ${relativeTime(query.created_at)}`} />)}
        {runItems.slice(0, 4).map((run) => <ArtifactCard key={`run:${run.ingestion_run_id}`} type="Report" title={run.ingestion_run_id} detail="Durable ingestion run with Bronze, Silver, Gold, and Qdrant stage progress." icon={Workflow} status={run.status} href={`/projects/${projectId}/runs/${run.ingestion_run_id}`} meta={relativeTime(run.created_at)} />)}
        <ArtifactCard type="Plot" title="Pipeline stage completion" detail="Computed from current ingestion run stage progress." icon={BarChart3} tone="info" meta={`${qdrant}/${runItems.length} runs indexed`} />
        <ArtifactCard type="Notebook" title="Notebook registry unavailable" detail="The current backend does not expose notebook artifacts yet." icon={NotebookTabs} tone="warning" />
      </div> : <EmptyState icon={Archive} title="No artifacts yet" description="Add and process sources to create source records, run evidence, model references, and vector artifacts." action="Add sources" onAction={() => location.assign(`/projects/${projectId}/sources`)} />}
    </section>
  </div>;
}
