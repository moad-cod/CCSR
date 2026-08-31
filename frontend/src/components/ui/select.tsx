import * as React from "react";
import {cn} from "@/lib/utils";

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(function Select({className, ...props}, ref) {
  return <select ref={ref} className={cn("h-10 w-full rounded-lg border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 text-sm text-[var(--ink)] outline-none transition focus:border-[var(--accent)] focus:ring-4 focus:ring-[var(--accent-soft)]", className)} {...props} />;
});
