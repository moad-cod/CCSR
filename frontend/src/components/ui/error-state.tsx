import {AlertTriangle, RefreshCw} from "lucide-react";
import {Button} from "@/components/ui/button";
import {cn} from "@/lib/utils";

export function ErrorState({title = "Something went wrong", description, onRetry, className}: {title?: string; description: string; onRetry?: () => void; className?: string}) {
  return <div role="alert" className={cn("flex min-h-64 flex-col items-center justify-center rounded-lg border border-[var(--danger-border)] bg-[var(--danger-soft)] px-5 py-10 text-center sm:px-6", className)}>
    <span className="flex size-11 items-center justify-center rounded-lg border border-[var(--danger-border)] bg-[var(--danger-soft-hover)] text-[var(--danger)]" aria-hidden="true"><AlertTriangle className="size-5" /></span>
    <h3 className="mt-4 text-sm font-semibold text-[var(--danger-soft-text)]">{title}</h3>
    <p className="mt-2 max-w-md text-xs leading-5 text-[var(--ink-secondary)]">{description}</p>
    {onRetry ? <Button className="mt-5" variant="secondary" size="sm" onClick={onRetry}><RefreshCw className="size-3.5" />Try again</Button> : null}
  </div>;
}
