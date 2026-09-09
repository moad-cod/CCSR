"use client";

import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {Database, LoaderCircle, Save, Settings, Trash2} from "lucide-react";
import {useRouter} from "next/navigation";
import {use, useState} from "react";
import {toast} from "sonner";
import {ConfirmDeleteDialog} from "@/components/confirm-delete-dialog";
import {PageHeader} from "@/components/page-header";
import {Button} from "@/components/ui/button";
import {ErrorState} from "@/components/ui/error-state";
import {Input} from "@/components/ui/input";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Document, Project} from "@/lib/types";
import {hasProjectCapability} from "@/platform/navigation/navigation";

export default function ProjectSettingsPage({params}: {params: Promise<{projectId: string}>}) {
  const {projectId} = use(params);
  const router = useRouter(); const queryClient = useQueryClient(); const [name, setName] = useState<string | null>(null); const [confirm, setConfirm] = useState(false);
  const project = useQuery({queryKey: ["project", projectId], queryFn: () => apiFetch<Project>(`/projects/${projectId}`)});
  const documents = useQuery({queryKey: ["documents", projectId], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${projectId}`), enabled: Boolean(project.data && hasProjectCapability(project.data, "ragforge"))});
  const effectiveName = name ?? project.data?.name ?? "";
  const rename = useMutation({mutationFn: () => apiFetch<Project>(`/projects/${projectId}`, {method: "PATCH", body: JSON.stringify({name: effectiveName})}), onSuccess: async () => {setName(null); await Promise.all([queryClient.invalidateQueries({queryKey: ["project", projectId]}), queryClient.invalidateQueries({queryKey: ["projects"]})]); toast.success("Project settings saved");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to update project")});
  const remove = useMutation({mutationFn: () => apiFetch(`/projects/${projectId}`, {method: "DELETE"}), onSuccess: async () => {await queryClient.invalidateQueries({queryKey: ["projects"]}); toast.success("Project deleted"); router.replace("/projects");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to delete project")});
  if (project.isLoading) return <LoadingState label="Loading project settings" rows={4} />;
  if (project.isError || !project.data) return <ErrorState title="Project settings could not be loaded" description="The project may not exist or may belong to another tenant." onRetry={() => void project.refetch()} />;
  const canWrite = project.data.permissions?.write ?? false;
  const canManage = project.data.permissions?.manage ?? false;
  const hasRAGForge = hasProjectCapability(project.data, "ragforge");
  return <div className="mx-auto max-w-4xl space-y-6"><PageHeader eyebrow={project.data.name} title="Project settings" description="Update settings supported by the current project API. Collection identity remains immutable to preserve indexed data." />
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-3"><span className="flex size-9 items-center justify-center rounded-lg bg-[var(--accent-soft)] text-[var(--accent)]"><Settings className="size-4" /></span><div><h2 className="text-sm font-semibold">General</h2><p className="mt-0.5 text-[9px] text-[var(--ink-muted)]">{canWrite ? "Your project access permits name updates." : "You have read-only access to this project."}</p></div></div><label className="mt-5 block"><span className="mb-2 block text-xs font-medium">Project name</span><Input value={effectiveName} disabled={!canWrite} onChange={(event) => setName(event.target.value)} /></label>{canWrite ? <div className="mt-5 flex justify-end"><Button disabled={rename.isPending || effectiveName.trim().length < 2 || effectiveName === project.data.name} onClick={() => rename.mutate()}>{rename.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Save className="size-4" />}Save name</Button></div> : null}</section>
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><div className="flex items-center gap-3"><Database className="size-4 text-[var(--ink-muted)]" /><div><h2 className="text-sm font-semibold">Storage identity</h2><p className="mt-0.5 text-[9px] text-[var(--ink-muted)]">Read-only values assigned by enabled capabilities.</p></div></div><dl className="mt-5 space-y-3 text-[10px]"><div className="grid gap-1 sm:grid-cols-[150px_1fr]"><dt className="text-[var(--ink-muted)]">Project ID</dt><dd className="mono break-all text-[var(--ink-secondary)]">{project.data.project_id}</dd></div>{hasRAGForge ? <div className="grid gap-1 sm:grid-cols-[150px_1fr]"><dt className="text-[var(--ink-muted)]">RAG collection</dt><dd className="mono break-all text-[var(--ink-secondary)]">{project.data.rag_config?.qdrant_collection ?? project.data.qdrant_collection}</dd></div> : null}</dl></section>
    {canManage ? <section className="rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] p-5"><h2 className="text-sm font-semibold text-[var(--danger-soft-text)]">Danger zone</h2><p className="mt-2 text-[10px] leading-5 text-[var(--ink-secondary)]">Deleting this project removes its research hierarchy and enabled capability data{hasRAGForge ? `, including ${documents.data?.length ?? "all"} RAG sources` : ""}.</p><Button className="mt-4" variant="danger" onClick={() => setConfirm(true)}><Trash2 className="size-4" />Delete project</Button></section> : null}
    {canManage ? <ConfirmDeleteDialog open={confirm} onClose={() => setConfirm(false)} name={project.data.name} title={`Delete ${project.data.name}?`} consequences="Research records, runs, artifacts, publications, and enabled capability data will be affected." isPending={remove.isPending} onConfirm={() => remove.mutate()} /> : null}
  </div>;
}
