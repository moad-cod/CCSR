import {DatabaseZap} from "lucide-react";
import {cn} from "@/lib/utils";

export function Brand({inverse = false}: {inverse?: boolean}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex size-10 items-center justify-center rounded-xl bg-[var(--accent)] text-[var(--ink)] shadow-[var(--shadow-md)] ">
        <DatabaseZap className="size-5" />
      </div>
      <div>
        <div
          className={cn(
            "text-base font-bold tracking-tight",
            inverse ? "text-[var(--ink)]" : "text-[var(--ink)]",
          )}
        >
          CCSR
        </div>
        <div
          className={cn(
            "text-[11px] font-medium uppercase tracking-[0.16em]",
            inverse ? "text-[var(--ink-muted)]" : "text-[var(--ink-faint)]",
          )}
        >
          Control plane
        </div>
      </div>
    </div>
  );
}
