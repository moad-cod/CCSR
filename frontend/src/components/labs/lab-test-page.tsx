"use client";

import {useQuery} from "@tanstack/react-query";
import {Activity, Beaker, Boxes, CircleDot, Database, FlaskConical, MessageSquareText, TimerReset} from "lucide-react";
import Link from "next/link";
import {useState} from "react";
import {MetricCard} from "@/components/metric-card";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {WorkspaceEntry} from "@/components/workspace/workspace-entry";
import {apiFetch} from "@/lib/api";
import type {Document, IngestionRun, Project, QueryHistoryItem} from "@/lib/types";
import {cn, relativeTime} from "@/lib/utils";

type VariantId = "baseline" | "retrieval" | "adaptation" | "final";

type TestVariant = {
  id: VariantId;
  label: string;
  title: string;
  system: string;
  status: string;
  executable: boolean;
  accent: string;
  detail: string;
};

function percent(part: number, total: number) {
  if (!total) return 0;
  return Math.round((part / total) * 100);
}

function ReadinessBar({label, value, total, color}: {label: string; value: number; total: number; color: string}) {
  const progress = percent(value, total);
  return <div>
    <div className="mb-1 flex items-center justify-between gap-3 text-[10px]"><span className="text-[var(--ink-muted)]">{label}</span><span className="font-mono text-[var(--ink-secondary)]">{value}/{total}</span></div>
    <div className="h-2 rounded-full bg-[var(--surface-elevated)]"><div className="h-full rounded-full" style={{width: `${progress}%`, backgroundColor: color}} /></div>
  </div>;
}

function VariantCard({variant, selected, onSelect}: {variant: TestVariant; selected: boolean; onSelect: () => void}) {
  return <button
    type="button"
    onClick={onSelect}
    className={cn(
      "group rounded-lg border bg-[var(--surface-elevated)] p-4 text-left transition hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]",
      selected ? "border-[var(--accent-border)] bg-[var(--surface-hover)]" : "border-[var(--border)]",
    )}
  >
    <div className="flex items-start justify-between gap-3">
      <div className="flex min-w-0 items-center gap-2">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-md border font-mono text-[11px] font-semibold" style={{borderColor: variant.accent, color: variant.accent}}>{variant.label}</span>
        <div className="min-w-0">
          <p className="font-mono text-[9px] uppercase tracking-[0.14em]" style={{color: variant.accent}}>{variant.title}</p>
          <h3 className="mt-1 truncate text-sm font-semibold text-[var(--ink)]">{variant.system}</h3>
        </div>
      </div>
      <StatusBadge status={variant.status} />
    </div>
    <p className="mt-3 line-clamp-3 text-xs leading-5 text-[var(--ink-muted)]">{variant.detail}</p>
    <div className="mt-4 flex items-center gap-2 text-[9px] text-[var(--ink-disabled)]">
      <CircleDot className="size-3" style={{color: variant.accent}} />
      {variant.executable ? "Uses the implemented interactive playground" : "Comparison slot is not executable yet"}
    </div>
  </button>;
}

export function LabTestPage({projectId}: {projectId: string}) {
  return <div className="space-y-6">
    <PageHeader eyebrow="Interactive test" title="Test" description="Run the implemented RAG playground, inspect citations, and turn grounded answers into persisted result evidence." />
    <section className="h-[calc(100dvh-22rem)] min-h-[640px] overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--background)]">
      <WorkspaceEntry projectId={projectId} />
    </section>
  </div>;
}
