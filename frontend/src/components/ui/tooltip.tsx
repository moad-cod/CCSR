"use client";

import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import * as React from "react";
import {cn} from "@/lib/utils";

export const TooltipProvider = TooltipPrimitive.Provider;
export function Tooltip({children, ...props}: React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Root>) {
  // Keep the primitive safe in isolated renders (tests, Storybook, embedded UI).
  return <TooltipPrimitive.Provider delayDuration={350}><TooltipPrimitive.Root {...props}>{children}</TooltipPrimitive.Root></TooltipPrimitive.Provider>;
}
export const TooltipTrigger = TooltipPrimitive.Trigger;
export const TooltipContent = React.forwardRef<React.ElementRef<typeof TooltipPrimitive.Content>, React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>>(function TooltipContent({className, sideOffset = 6, ...props}, ref) {
  return <TooltipPrimitive.Portal><TooltipPrimitive.Content ref={ref} sideOffset={sideOffset} className={cn("z-[140] rounded-md border border-[var(--border-strong)] bg-[var(--surface-raised)] px-2 py-1 text-[10px] text-[var(--ink-secondary)] shadow-[var(--shadow-md)]", className)} {...props} /></TooltipPrimitive.Portal>;
});
