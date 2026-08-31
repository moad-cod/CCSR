"use client";

import * as TabsPrimitive from "@radix-ui/react-tabs";
import * as React from "react";
import {cn} from "@/lib/utils";

export const Tabs = TabsPrimitive.Root;
export const TabsList = React.forwardRef<React.ElementRef<typeof TabsPrimitive.List>, React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>>(function TabsList({className, ...props}, ref) {
  return <TabsPrimitive.List ref={ref} className={cn("inline-grid min-h-9 items-center rounded-lg bg-[var(--surface-elevated)] p-1", className)} {...props} />;
});
export const TabsTrigger = React.forwardRef<React.ElementRef<typeof TabsPrimitive.Trigger>, React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>>(function TabsTrigger({className, ...props}, ref) {
  return <TabsPrimitive.Trigger ref={ref} className={cn("inline-flex h-8 items-center justify-center gap-1 rounded-md px-2 text-xs text-[var(--ink-muted)] outline-none transition hover:text-[var(--ink)] data-[state=active]:bg-[var(--surface-active)] data-[state=active]:text-[var(--accent-hover)] focus-visible:ring-2 focus-visible:ring-[var(--accent)]", className)} {...props} />;
});
export const TabsContent = TabsPrimitive.Content;
