"use client";

import {Activity, ArrowRight, FileStack, FolderKanban, MoreHorizontal, Pencil, Trash2} from "lucide-react";
import Link from "next/link";
import {StatusBadge} from "@/components/status-badge";
import {DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger} from "@/components/ui/dropdown-menu";
import {Tooltip, TooltipContent, TooltipTrigger} from "@/components/ui/tooltip";
import type {Project} from "@/lib/types";
import {cn, relativeTime} from "@/lib/utils";

export function ProjectCard({project, documentCount, activeRuns, view, onRename, onDelete}: {
  project: Project;
  documentCount: number | null;
  activeRuns: number | null;
  view: "grid" | "list";
  onRename: () => void;
  onDelete: () => void;
}) {
  const status = activeRuns ? "processing" : "ready";
  return <article className={cn("group relative rounded-xl border border-[var(--border)] bg-[var(--surface)] transition hover:border-[var(--accent-border)]", view === "grid" ? "p-5" : "flex items-center gap-4 p-4")}>
    <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]"><FolderKanban className="size-5" /></span>
    <div className={cn("min-w-0 flex-1", view === "grid" && "mt-4")}>
      <div className="flex items-start justify-between gap-3"><div className="min-w-0"><h2 className="truncate text-sm font-semibold">{project.name}</h2><p className="mt-1 text-[10px] text-[var(--ink-muted)]">Updated {relativeTime(project.updated_at)}</p></div><StatusBadge status={status} /></div>
      <p className={cn("text-[11px] leading-5 text-[var(--ink-secondary)]", view === "grid" ? "mt-3 line-clamp-2 min-h-10" : "mt-1 line-clamp-1")}>An isolated research workspace for sources, playground queries, pipeline runs, traces, and reproducible evaluations.</p>
      <div className="mt-4 flex flex-wrap items-center gap-4 text-[10px] text-[var(--ink-muted)]"><span className="flex items-center gap-1.5"><FileStack className="size-3" />{documentCount === null ? "…" : documentCount} sources</span><span className="flex items-center gap-1.5"><Activity className="size-3" />{activeRuns === null ? "…" : activeRuns ? `${activeRuns} active` : "No active runs"}</span></div>
    </div>
      <div className={cn("flex items-center gap-2", view === "grid" ? "mt-5 border-t border-[var(--border)] pt-4" : "shrink-0")}>
      <Link href={`/projects/${project.project_id}/overview`} className="flex h-9 flex-1 items-center justify-center gap-2 rounded-lg bg-[var(--accent-soft)] px-3 text-[11px] font-medium text-[var(--accent-hover)] hover:bg-[var(--accent-muted)]">Open project<ArrowRight className="size-3.5" /></Link>
      <DropdownMenu><Tooltip><TooltipTrigger asChild><DropdownMenuTrigger asChild><button className="icon-button" aria-label={`Actions for ${project.name}`}><MoreHorizontal className="size-4" /></button></DropdownMenuTrigger></TooltipTrigger><TooltipContent>Project actions</TooltipContent></Tooltip><DropdownMenuContent align="end"><DropdownMenuItem onSelect={onRename}><Pencil className="size-3.5" />Rename</DropdownMenuItem><DropdownMenuItem className="text-[var(--danger)] data-[highlighted]:text-[var(--danger)]" onSelect={onDelete}><Trash2 className="size-3.5" />Delete</DropdownMenuItem></DropdownMenuContent></DropdownMenu>
    </div>
  </article>;
}
