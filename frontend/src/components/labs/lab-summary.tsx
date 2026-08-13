import {labDomains} from "./lab-domain";

type LabSummaryProps = {
  totals: {
    labs: number;
    sources: number;
    active: number;
  };
};

export function LabSummary({totals}: LabSummaryProps) {
  return <section className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
    <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-2xl">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-[var(--accent)]">Lab discovery</p>
          <h2 className="mt-2 text-xl font-semibold leading-7">Research workspaces by computational domain</h2>
          <p className="mt-2 text-sm leading-6 text-[var(--ink-secondary)]">Each lab maps to an implemented project workspace: sources, ingestion runs, playground tests, history, and retrieval traces.</p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="min-w-20 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3"><b className="block text-lg">{totals.labs}</b><span className="text-[9px] text-[var(--ink-muted)]">Labs</span></div>
          <div className="min-w-20 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3"><b className="block text-lg">{totals.sources}</b><span className="text-[9px] text-[var(--ink-muted)]">Sources</span></div>
          <div className="min-w-20 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-3"><b className="block text-lg">{totals.active}</b><span className="text-[9px] text-[var(--ink-muted)]">Active</span></div>
        </div>
      </div>
    </div>
    <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-[var(--ink-muted)]">Domain palette</p>
      <div className="mt-4 grid grid-cols-2 gap-2">
        {labDomains.filter((domain) => domain.id !== "all").slice(0, 6).map((domain) => <div key={domain.id} className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] px-3 py-2 text-xs text-[var(--ink-secondary)]"><span className="size-2 rounded-full" style={{backgroundColor: domain.color}} />{domain.shortLabel}</div>)}
      </div>
    </div>
  </section>;
}
