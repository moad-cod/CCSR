"use client";

import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import * as React from "react";
import {cn} from "@/lib/utils";

export const DropdownMenu = DropdownMenuPrimitive.Root;
export const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
export const DropdownMenuContent = React.forwardRef<React.ElementRef<typeof DropdownMenuPrimitive.Content>, React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>>(function DropdownMenuContent({className, sideOffset = 6, ...props}, ref) {
  return <DropdownMenuPrimitive.Portal><DropdownMenuPrimitive.Content ref={ref} sideOffset={sideOffset} className={cn("z-[130] min-w-40 rounded-xl border border-[var(--border-strong)] bg-[var(--surface-raised)] p-1 shadow-[var(--shadow-lg)] outline-none", className)} {...props} /></DropdownMenuPrimitive.Portal>;
});
export const DropdownMenuItem = React.forwardRef<React.ElementRef<typeof DropdownMenuPrimitive.Item>, React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item>>(function DropdownMenuItem({className, ...props}, ref) {
  return <DropdownMenuPrimitive.Item ref={ref} className={cn("flex h-9 cursor-default items-center gap-2.5 rounded-lg px-2.5 text-left text-[11px] text-[var(--ink-muted)] outline-none transition data-[highlighted]:bg-[var(--surface-hover)] data-[highlighted]:text-[var(--ink)] data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className)} {...props} />;
});
export const DropdownMenuLabel = React.forwardRef<React.ElementRef<typeof DropdownMenuPrimitive.Label>, React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label>>(function DropdownMenuLabel({className, ...props}, ref) {
  return <DropdownMenuPrimitive.Label ref={ref} className={cn("px-2.5 py-2 text-[11px] font-medium text-[var(--ink)]", className)} {...props} />;
});
export const DropdownMenuSeparator = React.forwardRef<React.ElementRef<typeof DropdownMenuPrimitive.Separator>, React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>>(function DropdownMenuSeparator({className, ...props}, ref) {
  return <DropdownMenuPrimitive.Separator ref={ref} className={cn("my-1 h-px bg-[var(--border)]", className)} {...props} />;
});
