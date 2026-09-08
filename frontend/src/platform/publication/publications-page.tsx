"use client";

import {useQuery} from "@tanstack/react-query";
import {ArrowRight, BookOpenText, CalendarDays, FileText} from "lucide-react";
import Link from "next/link";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {PublicPublication} from "@/lib/types";


export function PublicationsPage() {
  const publications = useQuery({
    queryKey: ["publications", "public"],
    queryFn: () => apiFetch<PublicPublication[]>("/publications"),
  });

  if (publications.isLoading) return <LoadingState label="Loading publications" rows={6} />;
  if (publications.isError) return <ErrorState title="Publications could not be loaded" description="The public research index is temporarily unavailable." onRetry={() => void publications.refetch()} />;

  const records = publications.data ?? [];
  return <main className="min-h-screen bg-[var(--background)] text-[var(--ink)]">
    <header className="border-b border-[var(--border)] bg-[var(--surface)]">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/publications" className="flex items-center gap-3"><span className="flex size-9 items-center justify-center rounded-lg border border-[var(--accent-border)] bg-[var(--accent-soft)] text-[var(--accent)]"><BookOpenText className="size-4" /></span><span><b className="block text-sm">CCSR</b><span className="block font-mono text-[8px] uppercase tracking-[0.18em] text-[var(--ink-muted)]">Public research</span></span></Link>
        <Link href="/login" className="text-xs font-medium text-[var(--accent)] hover:text-[var(--accent-hover)]">Member sign in</Link>
      </div>
    </header>
    <div className="mx-auto max-w-6xl px-6 py-12">
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--research-violet)]">Research portfolio</p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight">Published work</h1>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--ink-muted)]">Immutable, public-safe research snapshots. Private projects, draft findings, run inputs, and internal artifact locations are never shown here.</p>
      {records.length ? <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {records.map((publication) => <Link key={publication.slug} href={`/publications/${publication.slug}`} className="group rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 transition hover:border-[var(--accent-border)] hover:bg-[var(--surface-raised)]">
          <div className="flex items-start justify-between gap-4"><FileText className="size-5 text-[var(--research-violet)]" /><span className="rounded-full border border-[var(--border)] px-2 py-1 font-mono text-[8px] text-[var(--ink-muted)]">REV {publication.revision_number}</span></div>
          <h2 className="mt-5 text-base font-semibold group-hover:text-[var(--accent)]">{publication.title}</h2>
          <p className="mt-2 line-clamp-3 text-xs leading-5 text-[var(--ink-muted)]">{publication.summary ?? "Published research snapshot"}</p>
          <div className="mt-5 flex items-center justify-between border-t border-[var(--border)] pt-4 text-[10px] text-[var(--ink-muted)]"><span className="inline-flex items-center gap-1.5"><CalendarDays className="size-3" />{new Date(publication.published_at).toLocaleDateString()}</span><span className="inline-flex items-center gap-1 text-[var(--accent)]">Read publication<ArrowRight className="size-3" /></span></div>
        </Link>)}
      </section> : <div className="mt-8"><EmptyState icon={BookOpenText} title="No public research yet" description="Draft and private publications stay hidden until a project manager publishes a validated snapshot." /></div>}
    </div>
  </main>;
}
