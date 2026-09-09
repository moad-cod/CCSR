"use client";

import {useQuery} from "@tanstack/react-query";
import {CheckCheck, Layers3, ScrollText} from "lucide-react";
import Link from "next/link";
import {usePathname} from "next/navigation";
import type {ReactNode} from "react";
import {apiFetch} from "@/lib/api";
import type {ProjectOverviewContract} from "@/lib/types";
import {cn} from "@/lib/utils";
import {hasProjectCapability, projectNavigation} from "@/platform/navigation/navigation";

export function ProjectShell({projectId, children}: {projectId: string; children: ReactNode}) {
  const pathname = usePathname();
  const overview = useQuery({
    queryKey: ["project-overview", projectId],
    queryFn: () => apiFetch<ProjectOverviewContract>(`/projects/${projectId}/overview`),
  });
  const project = overview.data?.project;
  const groups = project ? projectNavigation(project).filter((group) => group.label !== "Manage") : [];
  const canConfigure = project?.permissions?.write ?? false;

  return <div className="mx-auto max-w-7xl space-y-6">
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="flex flex-col gap-4 border-b border-[var(--border)] p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-md border border-[var(--accent-border)] bg-[var(--accent-soft)] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--accent-hover)]"><CheckCheck className="size-3" />Project</span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-[var(--tertiary-border)] bg-[var(--tertiary-soft)] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--research-violet)]"><ScrollText className="size-3" />Research platform</span>
            {project && hasProjectCapability(project, "ragforge") ? <span className="inline-flex items-center gap-1.5 rounded-md border border-[var(--border)] bg-[var(--surface-elevated)] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--ink-secondary)]"><Layers3 className="size-3" />RAGForge</span> : null}
          </div>
          <h1 className="mt-3 truncate text-xl font-semibold leading-7 text-[var(--ink)]">{project?.name ?? "Research project"}</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[var(--ink-secondary)]">Platform research records and enabled capability workspaces share this project boundary.</p>
        </div>
        {project && hasProjectCapability(project, "ragforge") ? <div className="min-w-0 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] px-3 py-2">
          <p className="font-mono text-[8px] uppercase tracking-[0.14em] text-[var(--ink-disabled)]">RAG collection</p>
          <p className="mono mt-1 max-w-72 truncate text-[10px] text-[var(--ink-secondary)]">{project.rag_config?.qdrant_collection ?? project.qdrant_collection}</p>
        </div> : null}
      </div>
      <div className="overflow-x-auto px-3">
        <nav className="flex min-w-max items-center gap-1" aria-label="Project sections">
          {groups.map((group, groupIndex) => <div key={group.label} className="flex items-center gap-1">
            {groupIndex > 0 ? <span className="mx-2 h-5 w-px bg-[var(--border)]" aria-hidden="true" /> : null}
            <span className="px-2 font-mono text-[8px] uppercase tracking-[0.12em] text-[var(--ink-disabled)]">{group.label}</span>
            {group.items.map((item) => {
              const Icon = item.icon;
              const selected = pathname === item.href || pathname.startsWith(`${item.href}/`) ||
                (item.label === "Sources" && pathname.includes("/documents")) ||
                (item.label === "Playground" && (pathname.includes("/test") || pathname.includes("/history") || pathname.includes("/chat"))) ||
                (item.label === "Pipelines" && pathname.includes("/runs/")) ||
                (item.label === "Results" && pathname.includes("/evaluation"));
              return <Link key={item.href} href={item.href} aria-current={selected ? "page" : undefined} className={cn("relative flex h-12 items-center gap-2 px-3 text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]", selected ? "text-[var(--ink)]" : "text-[var(--ink-muted)] hover:text-[var(--ink-secondary)]")}>
                <Icon className={cn("size-3.5", selected ? "text-[var(--accent)]" : "text-[var(--ink-muted)]")} />{item.label}
                <span className={cn("absolute inset-x-3 bottom-0 h-px rounded-full", selected ? "bg-[var(--accent)]" : "bg-transparent")} />
              </Link>;
            })}
          </div>)}
          {canConfigure ? <Link href={`/projects/${projectId}/settings`} className="ml-2 flex h-12 items-center gap-2 px-3 text-xs font-medium text-[var(--ink-muted)] hover:text-[var(--ink-secondary)]">Settings</Link> : null}
        </nav>
      </div>
    </section>
    {children}
  </div>;
}
