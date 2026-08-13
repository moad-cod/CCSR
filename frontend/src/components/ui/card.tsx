import type {HTMLAttributes} from "react";
import {cn} from "@/lib/utils";

export function Card({className, ...props}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)]",
        className,
      )}
      {...props}
    />
  );
}
