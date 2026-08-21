import type {LucideIcon} from "lucide-react";
import {Button} from "@/components/ui/button";
import {cn} from "@/lib/utils";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  onAction,
  className,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: string;
  onAction?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex min-h-64 flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border-strong)] bg-[var(--surface)] px-5 py-10 text-center sm:px-6", className)} aria-live="polite">
      <div className="mb-4 flex size-11 items-center justify-center rounded-lg border border-[var(--accent-border)] bg-[var(--accent-soft)] text-[var(--accent)]" aria-hidden="true">
        <Icon className="size-6" />
      </div>
      <h3 className="text-base font-semibold text-[var(--ink)]">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-[var(--ink-muted)]">
        {description}
      </p>
      {action && onAction ? (
        <Button className="mt-5" size="sm" onClick={onAction}>
          {action}
        </Button>
      ) : null}
    </div>
  );
}
