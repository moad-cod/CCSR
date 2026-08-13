"use client";

import {Search} from "lucide-react";
import {Input} from "@/components/ui/input";
import {cn} from "@/lib/utils";
import {labDomains, type LabDomainId} from "./lab-domain";

type LabFiltersProps = {
  search: string;
  domainFilter: LabDomainId;
  onSearchChange: (value: string) => void;
  onDomainFilterChange: (value: LabDomainId) => void;
};

export function LabFilters({search, domainFilter, onSearchChange, onDomainFilterChange}: LabFiltersProps) {
  return <section className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
      <label className="relative min-w-0 flex-1"><span className="sr-only">Search labs</span><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--ink-muted)]" /><Input className="pl-9" value={search} onChange={(event) => onSearchChange(event.target.value)} placeholder="Search labs by title" /></label>
      <div className="flex gap-1 overflow-x-auto">
        {labDomains.map((domain) => <button key={domain.id} onClick={() => onDomainFilterChange(domain.id)} className={cn("flex h-9 shrink-0 items-center gap-2 rounded-lg border px-3 text-xs transition", domainFilter === domain.id ? "border-[var(--accent-border)] bg-[var(--accent-soft)] text-[var(--ink)]" : "border-[var(--border)] text-[var(--ink-muted)] hover:bg-[var(--surface-hover)] hover:text-[var(--ink)]")}><span className="size-1.5 rounded-full" style={{backgroundColor: domain.color}} />{domain.shortLabel}</button>)}
      </div>
    </div>
  </section>;
}
