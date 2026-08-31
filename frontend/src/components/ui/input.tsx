import * as React from "react";
import {cn} from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(function Input({
  className,
  ...props
}, ref) {
  return (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-lg border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 text-sm text-[var(--ink)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)] focus:ring-4 focus:ring-[var(--accent-soft)]",
        className,
      )}
      {...props}
    />
  );
});
