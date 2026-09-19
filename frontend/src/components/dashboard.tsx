import type {LucideIcon} from "lucide-react";
import {cn} from "@/lib/utils";

export function DashboardPanel({
  children,
  className,
  title,
  description,
  action,
}: {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return <section className={cn("dashboard-panel", className)}>
    {title || description || action ? <div className="dashboard-panel-header">
      <div className="min-w-0">
        {title ? <h2 className="text-[15px] font-semibold tracking-[-0.01em] text-[var(--ink)]">{title}</h2> : null}
        {description ? <p className="mt-1 text-[11px] leading-5 text-[var(--ink-muted)]">{description}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div> : null}
    {children}
  </section>;
}

export function MetricCell({label, value, detail, icon: Icon, accent = "blue"}: {
  label: string;
  value: string | number;
  detail?: string;
  icon: LucideIcon;
  accent?: "blue" | "violet" | "neutral";
}) {
  return <div className="metric-cell">
    <div className="flex items-center justify-between gap-3">
      <span className="text-[10px] font-medium uppercase tracking-[0.1em] text-[var(--ink-muted)]">{label}</span>
      <Icon className={cn("size-3.5", accent === "violet" ? "text-[var(--research-violet)]" : accent === "blue" ? "text-[var(--accent)]" : "text-[var(--ink-muted)]")} aria-hidden="true" />
    </div>
    <p className="mt-3 font-mono text-[25px] font-semibold leading-none tracking-[-0.04em] tabular-nums text-[var(--ink)]">{value}</p>
    {detail ? <p className="mt-2 text-[10px] text-[var(--ink-muted)]">{detail}</p> : null}
  </div>;
}

export function EvidenceBar({label, state, value, tone = "blue"}: {
  label: string;
  state: string;
  value: number;
  tone?: "blue" | "violet" | "success" | "warning";
}) {
  const width = Math.max(3, Math.min(100, value));
  const color = tone === "violet" ? "var(--research-violet)" : tone === "success" ? "var(--success)" : tone === "warning" ? "var(--warning)" : "var(--accent)";
  return <div>
    <div className="mb-2 flex items-center justify-between gap-4 text-[11px]"><span className="text-[var(--ink-secondary)]">{label}</span><span className="text-[var(--ink-muted)]">{state}</span></div>
    <div className="h-1 overflow-hidden rounded-full bg-[var(--surface-hover)]" role="img" aria-label={`${label}: ${state}`}><div className="h-full rounded-full" style={{width: `${width}%`, background: color}} /></div>
  </div>;
}
