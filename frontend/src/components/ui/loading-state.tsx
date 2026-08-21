import {cn} from "@/lib/utils";

export function LoadingState({label = "Loading", rows = 3, className}: {label?: string; rows?: number; className?: string}) {
  const widths = ["w-5/6", "w-2/3", "w-3/4", "w-1/2"];
  return <div className={cn("space-y-3 rounded-lg border border-[var(--border)] bg-[var(--surface)] p-4", className)} role="status" aria-label={label} aria-live="polite" aria-busy="true">
    <span className="sr-only">{label}</span>
    <div className="mb-4 flex items-center gap-3" aria-hidden="true">
      <span className="state-skeleton size-9 rounded-lg" />
      <span className="block space-y-2">
        <span className="state-skeleton block h-3 w-36 rounded" />
        <span className="state-skeleton block h-2 w-24 rounded" />
      </span>
    </div>
    {Array.from({length: rows}, (_, index) => <div key={index} className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4" aria-hidden="true">
      <div className={cn("state-skeleton h-3 rounded", widths[index % widths.length])} />
      <div className="mt-3 grid gap-2 sm:grid-cols-3">
        <div className="state-skeleton h-2 rounded" />
        <div className="state-skeleton h-2 rounded" />
        <div className="state-skeleton h-2 rounded" />
      </div>
    </div>)}
  </div>;
}
