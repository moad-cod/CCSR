"use client";

import {File, FileSpreadsheet, FileText, MoreHorizontal, Trash2} from "lucide-react";
import Link from "next/link";
import {StatusBadge} from "@/components/status-badge";
import type {Document, Project} from "@/lib/types";
import {relativeTime} from "@/lib/utils";

function DocumentIcon({extension}: {extension: string | null}) {
  const Icon = extension === ".csv" || extension === ".xlsx" ? FileSpreadsheet : extension === ".txt" || extension === ".docx" ? FileText : File;
  return <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-[var(--info-soft)] text-[var(--info)]"><Icon className="size-4" /></span>;
}

export function DocumentList({items, project, onDelete}: {items: Document[]; project?: Project; onDelete?: (document: Document) => void}) {
  return <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)]">
    <div className="hidden grid-cols-[minmax(220px,2fr)_1fr_1fr_1fr_auto] gap-4 border-b border-[var(--border)] px-4 py-2.5 text-[9px] font-semibold uppercase tracking-[.12em] text-[var(--ink-disabled)] md:grid"><span>Document</span><span>Source</span><span>Status</span><span>Updated</span><span>Actions</span></div>
    <div className="divide-y divide-[var(--border)]">{items.map((document) => <article key={document.document_id} className="grid gap-3 p-4 md:grid-cols-[minmax(220px,2fr)_1fr_1fr_1fr_auto] md:items-center md:gap-4">
      <Link href={`/projects/${document.project_id}/documents/${document.document_id}`} className="flex min-w-0 items-center gap-3 group"><DocumentIcon extension={document.extension} /><span className="min-w-0"><span className="block truncate text-xs font-medium group-hover:text-[var(--accent-hover)]">{document.filename ?? "Untitled document"}</span><span className="mono mt-0.5 block truncate text-[8px] text-[var(--ink-disabled)]">{document.document_id}</span>{project ? null : <span className="mt-0.5 block truncate text-[9px] text-[var(--ink-muted)]">Project: {(document as Document & {project?: Project}).project?.name ?? "Unknown"}</span>}</span></Link>
      <span className="text-[10px] capitalize text-[var(--ink-secondary)]">{document.source_type ?? "unknown"}</span><StatusBadge status={document.status} /><span className="text-[10px] text-[var(--ink-muted)]">{relativeTime(document.updated_at)}</span>
      <div className="flex items-center gap-1"><Link href={`/projects/${document.project_id}/documents/${document.document_id}`} className="icon-button" aria-label={`Open ${document.filename}`}><MoreHorizontal className="size-4" /></Link>{onDelete ? <button className="icon-button text-[var(--danger)]" onClick={() => onDelete(document)} aria-label={`Delete ${document.filename}`}><Trash2 className="size-4" /></button> : null}</div>
    </article>)}</div>
  </div>;
}
