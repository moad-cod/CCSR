"use client";

import {Activity, ArrowRight, FileStack, MoreHorizontal, Pencil, Trash2} from "lucide-react";
import Link from "next/link";
import {useState} from "react";
import {StatusBadge} from "@/components/status-badge";
import type {Project} from "@/lib/types";
import {relativeTime} from "@/lib/utils";
import type {LabDomain, LabStats} from "./lab-domain";
import {readiness} from "./lab-domain";

type LabCardProps = {
  project: Project;
  stats: LabStats;
  domain: LabDomain;
  onRename: () => void;
  onDelete: () => void;
};

export function LabCard({project, stats, domain, onRename, onDelete}: LabCardProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const Icon = domain.icon;
  const status = readiness(stats);

  return <article className="group relative flex min-h-[286px] flex-col rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5 transition hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]">
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0">
        <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.12em] text-[var(--ink-muted)]">
          <span className="size-2 rounded-full" style={{backgroundColor: domain.color}} />
          <span>{domain.label}</span>
        </div>
        <h2 className="mt-4 line-clamp-2 text-lg font-semibold leading-6 text-[var(--ink)]">{project.name}</h2>
      </div>
      <div className="relative shrink-0">
        <button className="icon-button size-8" onClick={() => setMenuOpen((value) => !value)} aria-label={`Actions for ${project.name}`} aria-expanded={menuOpen}><MoreHorizontal className="size-4" /></button>
        {menuOpen ? <div className="popover right-0 top-9 w-40 p-1"><button className="menu-item w-full" onClick={() => {setMenuOpen(false); onRename();}}><Pencil className="size-3.5" />Rename</button><button className="menu-item w-full text-[var(--danger)]" onClick={() => {setMenuOpen(false); onDelete();}}><Trash2 className="size-3.5" />Delete</button></div> : null}
      </div>
    </div>

    <p className="mt-3 line-clamp-2 text-sm leading-6 text-[var(--ink-secondary)]">
      A local-first research lab for sources, pipeline runs, playground testing, retrieval traces, and reproducibility evidence.
    </p>

    <div className="mt-5 grid grid-cols-3 gap-2">
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3">
        <span className="block text-[8px] uppercase tracking-[0.12em] text-[var(--ink-disabled)]">Sources</span>
        <b className="mt-1 block text-lg font-semibold text-[var(--ink)]">{stats.documents ?? "..."}</b>
      </div>
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3">
        <span className="block text-[8px] uppercase tracking-[0.12em] text-[var(--ink-disabled)]">Indexed</span>
        <b className="mt-1 block text-lg font-semibold text-[var(--ink)]">{stats.indexed ?? "..."}</b>
      </div>
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3">
        <span className="block text-[8px] uppercase tracking-[0.12em] text-[var(--ink-disabled)]">Runs</span>
        <b className="mt-1 block text-lg font-semibold text-[var(--ink)]">{stats.active ?? "..."}</b>
      </div>
    </div>

    <div className="mt-5 flex flex-wrap items-center gap-2 text-xs text-[var(--ink-muted)]">
      <StatusBadge status={status} />
      <span className="inline-flex items-center gap-1"><Activity className="size-3" />Updated {relativeTime(project.updated_at)}</span>
      {stats.latestRun ? <span className="inline-flex items-center gap-1"><FileStack className="size-3" />Latest {stats.latestRun.status.replaceAll("_", " ")}</span> : null}
    </div>

    <div className="mt-auto flex items-center justify-between gap-3 border-t border-[var(--border)] pt-4">
      <span className="flex size-9 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)]" style={{color: domain.color}}><Icon className="size-4" /></span>
      <Link href={`/projects/${project.project_id}/overview`} className="inline-flex h-9 items-center gap-2 rounded-lg bg-[var(--accent)] px-3 text-xs font-semibold text-[var(--ink-inverse)] hover:bg-[var(--accent-hover)]">Explore lab<ArrowRight className="size-3.5 transition group-hover:translate-x-0.5" /></Link>
    </div>
  </article>;
}
