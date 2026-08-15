"use client";

import {useQuery} from "@tanstack/react-query";
import {ArrowRight, BookOpenText, CalendarClock, Database, FileStack, Hash, Microscope, ScrollText, Workflow} from "lucide-react";
import type {LucideIcon} from "lucide-react";
import Link from "next/link";
import {useMemo, useState} from "react";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Document, DocumentVersion, IngestionRun, Project} from "@/lib/types";
import {relativeTime} from "@/lib/utils";

export function LabResearchPage({projectId}: {projectId: string}) {
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`)});
  const runs = useQuery({queryKey: ["ingestion-runs", projectId], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${projectId}&limit=20`)});
  const docs = documents.data ?? [];
  const indexed = docs.filter((document) => document.status === "indexed");
  const latestRun = runs.data?.[0];
  const selectedDocument = docs.find((document) => document.document_id === selectedDocumentId) ?? docs[0] ?? null;
  const versions = useQuery({
    queryKey: ["document-versions", selectedDocument?.document_id],
    queryFn: () => apiFetch<DocumentVersion[]>(`/documents/${selectedDocument?.document_id}/versions`),
    enabled: Boolean(selectedDocument?.document_id),
  });
  const latestVersion = versions.data?.[0] ?? null;
  const methodology = useMemo(() => [
    ["Corpus", `${docs.length} source records define the current research corpus.`],
    ["Ingestion", latestRun ? `Latest pipeline run is ${latestRun.status.replaceAll("_", " ")}.` : "No pipeline run has been recorded yet."],
    ["Indexing", `${indexed.length} sources are indexed and available for retrieval-backed tests.`],
    ["Testing", "Use the Lab Test tab to produce grounded answers, citations, and retrieval traces."],
  ], [docs.length, indexed.length, latestRun]);
  const metadataRows: {label: string; value: string; icon: LucideIcon}[] = [
    {label: "Title", value: selectedDocument?.filename ?? selectedDocument?.document_id ?? "No source", icon: FileStack},
    {label: "Status", value: selectedDocument?.status ?? "Unavailable", icon: Database},
    {label: "Version", value: selectedDocument?.current_version_id ?? "No active version", icon: Hash},
    {label: "Updated", value: selectedDocument ? relativeTime(selectedDocument.updated_at) : "Unavailable", icon: CalendarClock},
    {label: "Chunker", value: latestVersion?.chunker_id ?? "Unavailable", icon: Workflow},
    {label: "Embedding", value: latestVersion?.embedding_model ?? "Unavailable", icon: Database},
  ];
  const loading = project.isLoading || documents.isLoading || runs.isLoading;
  const error = project.isError || documents.isError || runs.isError;
  if (loading) return <LoadingState label="Loading lab research" rows={5} />;
  if (error) return <ErrorState title="Research context could not be loaded" description="One or more project endpoints returned an error." onRetry={() => void Promise.all([project.refetch(), documents.refetch(), runs.refetch()])} />;

  return <div className="space-y-6">
    <PageHeader eyebrow={project.data?.name ?? "Research"} title="Research" description="Source corpus, methodology evidence, and the current implemented RAG research foundation for this Lab." actions={<Link href={`/projects/${projectId}/sources`}><Button><FileStack className="size-4" />Manage sources</Button></Link>} />
    <section className="grid gap-4 lg:grid-cols-[1fr_0.95fr]">
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-center gap-2">
          <ScrollText className="size-4 text-[var(--research-violet)]" />
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-[var(--research-violet)]">Research question</p>
        </div>
        <h2 className="mt-3 text-xl font-semibold leading-7">How can {project.data?.name ?? "this Lab"} produce grounded answers with inspectable evidence?</h2>
        <p className="mt-3 text-sm leading-6 text-[var(--ink-secondary)]">Abstract: this Lab currently studies a project-backed RAG workflow over {docs.length} source records, with {indexed.length} indexed sources, {runs.data?.length ?? 0} ingestion runs, and source-level metadata for reproducibility.</p>
        <div className="mt-5 rounded-lg border border-[var(--tertiary-border)] bg-[var(--tertiary-soft)] p-4">
          <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--research-violet)]">Hypothesis</p>
          <p className="mt-2 text-xs leading-5 text-[var(--ink-secondary)]">If the source corpus is indexed and tests preserve citations, then answer quality can be inspected through retrieved evidence rather than judged only from final text.</p>
        </div>
      </div>
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
        <div className="flex items-center gap-2">
          <Microscope className="size-4 text-[var(--accent)]" />
          <h2 className="text-sm font-semibold">Methodology</h2>
        </div>
        <ol className="mt-4 space-y-3">
          {methodology.map(([label, detail], index) => <li key={label} className="flex gap-3">
            <span className="flex size-6 shrink-0 items-center justify-center rounded-md border border-[var(--border)] bg-[var(--surface-elevated)] font-mono text-[9px] text-[var(--accent)]">{index + 1}</span>
            <span><span className="block text-xs font-semibold text-[var(--ink)]">{label}</span><span className="mt-1 block text-xs leading-5 text-[var(--ink-muted)]">{detail}</span></span>
          </li>)}
        </ol>
      </div>
    </section>
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
