"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import {X} from "lucide-react";
import {cn} from "@/lib/utils";

/** Keeps the application's controlled-dialog API while Radix owns focus and modal semantics. */
export function Dialog({open, onClose, title, description, children, className}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return <DialogPrimitive.Root open={open} onOpenChange={(nextOpen) => {if (!nextOpen) onClose();}}>
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-[120] bg-[var(--background-overlay)]" />
      <DialogPrimitive.Content className={cn("fixed left-1/2 top-1/2 z-[121] w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-xl border border-[var(--border-strong)] bg-[var(--surface-muted)] p-5 shadow-[var(--shadow-lg)] outline-none sm:p-6", className)}>
        <div className="flex items-start gap-4"><div className="min-w-0 flex-1"><DialogPrimitive.Title className="text-lg font-semibold">{title}</DialogPrimitive.Title>{description ? <DialogPrimitive.Description className="mt-1.5 text-sm leading-6 text-[var(--ink-muted)]">{description}</DialogPrimitive.Description> : null}</div><DialogPrimitive.Close className="icon-button -mr-2 -mt-2" aria-label="Close dialog"><X className="size-4" /></DialogPrimitive.Close></div>
        {children}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  </DialogPrimitive.Root>;
}
