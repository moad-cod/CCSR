"use client";

import {useQuery} from "@tanstack/react-query";
import {Archive, BarChart3, Beaker, BookOpenText, CheckCheck, FlaskConical, Home, RotateCcw, ScrollText, Settings} from "lucide-react";
import Link from "next/link";
import {usePathname} from "next/navigation";
import type {ReactNode} from "react";
import {apiFetch} from "@/lib/api";
import type {Project} from "@/lib/types";
import {cn} from "@/lib/utils";

type LabShellProps = {
  projectId: string;
  children: ReactNode;
};

const tabs = [
  {label: "Overview", href: "overview", icon: Home},
  {label: "Research", href: "research", icon: BookOpenText},
  {label: "Experiments", href: "experiments", icon: FlaskConical},
  {label: "Results", href: "results", icon: BarChart3},
  {label: "Artifacts", href: "artifacts", icon: Archive},
  {label: "Test", href: "test", icon: Beaker},
  {label: "Reproduce", href: "reproduce", icon: RotateCcw},
] as const;

function activeTab(pathname: string) {
  if (pathname.includes("/sources") || pathname.includes("/documents")) return "research";
  if (pathname.includes("/playground") || pathname.includes("/history")) return "test";
  if (pathname.includes("/pipelines") || pathname.includes("/runs/")) return "artifacts";
  if (pathname.includes("/evaluation")) return "results";
  return tabs.find((tab) => pathname.includes(`/${tab.href}`))?.href ?? "overview";
}

export function LabShell({projectId, children}: LabShellProps) {
  const pathname = usePathname();
  const active = activeTab(pathname);
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const projectName = project.data?.name ?? "Research lab";

  return <div className="mx-auto max-w-7xl space-y-6">
    <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)]">
      <div className="flex flex-col gap-4 border-b border-[var(--border)] p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-md border border-[var(--accent-border)] bg-[var(--accent-soft)] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--accent-hover)]"><CheckCheck className="size-3" />Lab</span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-[var(--tertiary-border)] bg-[var(--tertiary-soft)] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--research-violet)]"><ScrollText className="size-3" />Project-backed</span>
          </div>
          <h1 className="mt-3 truncate text-xl font-semibold leading-7 text-[var(--ink)]">{projectName}</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[var(--ink-secondary)]">A common research shell for methodology, experiments, evidence, artifacts, interactive testing, and reproducibility state.</p>
        </div>
        <div className="min-w-0 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] px-3 py-2">
          <p className="font-mono text-[8px] uppercase tracking-[0.14em] text-[var(--ink-disabled)]">Collection</p>
          <p className="mono mt-1 max-w-72 truncate text-[10px] text-[var(--ink-secondary)]">{project.data?.qdrant_collection ?? projectId}</p>
        </div>
      </div>
      <div className="overflow-x-auto px-3">
        <nav className="flex min-w-max items-center gap-1" aria-label="Lab sections">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const selected = active === tab.href;
            return <Link
              key={tab.href}
              href={`/projects/${projectId}/${tab.href}`}
              aria-current={selected ? "page" : undefined}
              className={cn(
                "relative flex h-12 items-center gap-2 px-3 text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]",
                selected ? "text-[var(--ink)]" : "text-[var(--ink-muted)] hover:text-[var(--ink-secondary)]",
              )}
            >
              <Icon className={cn("size-3.5", selected ? "text-[var(--accent)]" : "text-[var(--ink-muted)]")} />
              {tab.label}
              <span className={cn("absolute inset-x-3 bottom-0 h-px rounded-full", selected ? "bg-[var(--accent)]" : "bg-transparent")} />
            </Link>;
          })}
          <Link href={`/projects/${projectId}/settings`} className="ml-2 flex h-12 items-center gap-2 px-3 text-xs font-medium text-[var(--ink-muted)] hover:text-[var(--ink-secondary)]"><Settings className="size-3.5" />Settings</Link>
        </nav>
      </div>
    </section>
    {children}
  </div>;
}
