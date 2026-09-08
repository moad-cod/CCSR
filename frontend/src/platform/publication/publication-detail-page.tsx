"use client";

import {useQuery} from "@tanstack/react-query";
import {ArrowLeft, BookOpenText, Box, FlaskConical, Lightbulb, ScrollText} from "lucide-react";
import Link from "next/link";
import {StatusBadge} from "@/components/status-badge";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {PublicPublication} from "@/lib/types";


export function PublicationDetailPage({slug}: {slug: string}) {
  const publication = useQuery({
    queryKey: ["publication", slug],
    queryFn: () => apiFetch<PublicPublication>(`/publications/${encodeURIComponent(slug)}`),
  });
  if (publication.isLoading) return <LoadingState label="Loading publication" rows={8} />;
  if (publication.isError || !publication.data) return <ErrorState title="Publication not found" description="This research snapshot is private, draft, unpublished, or does not exist." onRetry={() => void publication.refetch()} />;

  const record = publication.data;
  const snapshot = record.snapshot;
  const study = snapshot.research_study;
  return <main className="min-h-screen bg-[var(--background)] text-[var(--ink)]">
    <header className="border-b border-[var(--border)] bg-[var(--surface)]"><div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4"><Link href="/publications" className="inline-flex items-center gap-2 text-xs text-[var(--ink-muted)] hover:text-[var(--accent)]"><ArrowLeft className="size-3.5" />All publications</Link><span className="font-mono text-[9px] text-[var(--ink-muted)]">REVISION {record.revision_number}</span></div></header>
    <article className="mx-auto max-w-5xl px-6 py-12">
      <div className="flex items-center gap-2 text-[var(--research-violet)]"><BookOpenText className="size-4" /><span className="font-mono text-[10px] uppercase tracking-[0.18em]">{snapshot.project.name}</span></div>
      <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight">{record.title}</h1>
      {record.summary ? <p className="mt-5 max-w-3xl text-base leading-7 text-[var(--ink-secondary)]">{record.summary}</p> : null}
      {study ? <div className="mt-10 space-y-6">
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6"><div className="flex items-center justify-between gap-4"><div><p className="font-mono text-[9px] uppercase tracking-[0.16em] text-[var(--research-violet)]">Research study</p><h2 className="mt-2 text-xl font-semibold">{study.title}</h2></div><StatusBadge status={study.status} /></div>{study.abstract ? <p className="mt-4 text-sm leading-6 text-[var(--ink-secondary)]">{study.abstract}</p> : null}{study.methodology ? <div className="mt-5 border-t border-[var(--border)] pt-5"><h3 className="text-xs font-semibold">Methodology</h3><p className="mt-2 whitespace-pre-wrap text-xs leading-6 text-[var(--ink-muted)]">{study.methodology}</p></div> : null}</section>
        <div className="grid gap-4 lg:grid-cols-2"><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-2"><ScrollText className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Research questions</h2></div><div className="mt-4 space-y-3">{study.questions.map((item, index) => <div key={`${item.question}-${index}`} className="rounded-lg bg-[var(--surface-elevated)] p-3 text-xs leading-5">{item.question}</div>)}</div></section><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-2"><Lightbulb className="size-4 text-[var(--research-violet)]" /><h2 className="text-sm font-semibold">Hypotheses</h2></div><div className="mt-4 space-y-3">{study.hypotheses.map((item, index) => <div key={`${item.statement}-${index}`} className="rounded-lg bg-[var(--surface-elevated)] p-3"><p className="text-xs leading-5">{item.statement}</p><div className="mt-2"><StatusBadge status={item.status} /></div></div>)}</div></section></div>
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-2"><FlaskConical className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Experiments</h2></div><div className="mt-4 grid gap-3 md:grid-cols-2">{study.experiments.map((item) => <div key={item.id} className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4"><div className="flex items-center justify-between gap-3"><b className="text-xs">{item.name}</b><StatusBadge status={item.status} /></div>{item.objective ? <p className="mt-2 text-[10px] leading-5 text-[var(--ink-muted)]">{item.objective}</p> : null}</div>)}</div></section>
      </div> : null}
      <div className="mt-6 grid gap-4 lg:grid-cols-2"><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-2"><Lightbulb className="size-4 text-[var(--research-violet)]" /><h2 className="text-sm font-semibold">Validated findings</h2></div><div className="mt-4 space-y-3">{snapshot.findings.map((item) => <div key={item.id} className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4"><b className="text-xs">{item.title}</b><p className="mt-2 text-xs leading-5 text-[var(--ink-secondary)]">{item.statement}</p></div>)}</div></section><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-2"><Box className="size-4 text-[var(--accent)]" /><h2 className="text-sm font-semibold">Public artifacts</h2></div><div className="mt-4 space-y-3">{snapshot.artifacts.map((item) => <div key={item.id} className="flex items-center justify-between gap-4 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4"><span><b className="block text-xs">{item.type}</b><span className="mt-1 block font-mono text-[9px] text-[var(--ink-muted)]">VERSION {item.version}</span></span>{item.size_bytes !== null ? <span className="text-[10px] text-[var(--ink-muted)]">{item.size_bytes.toLocaleString()} bytes</span> : null}</div>)}</div></section></div>
    </article>
  </main>;
}
