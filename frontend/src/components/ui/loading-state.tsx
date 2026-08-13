import {cn} from "@/lib/utils";

export function LoadingState({label = "Loading", rows = 3, className}: {label?: string; rows?: number; className?: string}) {
  return <div className={cn("space-y-3", className)} aria-label={label} aria-live="polite">
    {Array.from({length: rows}, (_, index) => <div key={index} className="h-20 animate-pulse rounded-xl border border-[var(--border)] bg-[var(--surface)]" />)}
  </div>;
}
