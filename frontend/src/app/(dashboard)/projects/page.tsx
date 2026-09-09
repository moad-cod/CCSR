"use client";

import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {FolderKanban, Grid2X2, List, Plus, Search} from "lucide-react";
import {useRouter} from "next/navigation";
import {useMemo, useState} from "react";
import {toast} from "sonner";
import {ConfirmDeleteDialog} from "@/components/confirm-delete-dialog";
import {PageHeader} from "@/components/page-header";
import {ProjectCard} from "@/components/project-card";
import {ProjectForm, type ProjectFormValues} from "@/components/project-form";
import {Button} from "@/components/ui/button";
import {Dialog} from "@/components/ui/dialog";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {Input} from "@/components/ui/input";
import {LoadingState} from "@/components/ui/loading-state";
import {useWorkspaceOverview} from "@/hooks/use-workspace-overview";
import {apiFetch} from "@/lib/api";
import type {Chunker, Organization, Project} from "@/lib/types";
import {cn} from "@/lib/utils";

export default function ProjectsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [dialog, setDialog] = useState<"create" | "rename" | null>(null);
  const [selected, setSelected] = useState<Project | null>(null);
  const [deleting, setDeleting] = useState<Project | null>(null);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("updated");
  const [view, setView] = useState<"grid" | "list">("grid");
  const overview = useWorkspaceOverview({documents: false});
  const organizationsQuery = useQuery({queryKey: ["organizations"], queryFn: () => apiFetch<Organization[]>("/organizations/"), enabled: dialog === "create"});
  const chunkersQuery = useQuery({queryKey: ["chunkers"], queryFn: () => apiFetch<Chunker[]>("/chunkers"), enabled: dialog === "create"});
  const projects = useMemo(() => overview.projects, [overview.projects]);
  const stats = new Map(projects.map((project) => {
    const summary = overview.summaries.get(project.project_id);
    return [project.project_id, {documents: summary?.document_count ?? 0, active: summary?.active_run_count ?? 0}];
  }));
  const filtered = useMemo(() => projects.filter((project) => project.name.toLowerCase().includes(search.trim().toLowerCase())).sort((a, b) => sort === "name" ? a.name.localeCompare(b.name) : new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()), [projects, search, sort]);

  const refreshProjects = () => Promise.all([queryClient.invalidateQueries({queryKey: ["projects"]}), queryClient.invalidateQueries({queryKey: ["project-overviews"]}), queryClient.invalidateQueries({queryKey: ["ragforge", "workspace-overview"]})]);
  const create = useMutation({mutationFn: (values: ProjectFormValues) => apiFetch<Project>("/projects/", {method: "POST", body: JSON.stringify({name: values.name, organization_id: values.organization_id || null})}), onSuccess: async (project, values) => {localStorage.setItem(`ragforge:project:${project.project_id}:chunker`, values.chunker); await refreshProjects(); toast.success("Project created"); router.push(`/projects/${project.project_id}/onboarding`);}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to create project")});
  const rename = useMutation({mutationFn: (values: ProjectFormValues) => apiFetch<Project>(`/projects/${selected?.project_id}`, {method: "PATCH", body: JSON.stringify({name: values.name})}), onSuccess: async () => {await refreshProjects(); setDialog(null); setSelected(null); toast.success("Project renamed");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to rename project")});
  const remove = useMutation({mutationFn: (projectId: string) => apiFetch(`/projects/${projectId}`, {method: "DELETE"}), onSuccess: async () => {await refreshProjects(); setDeleting(null); toast.success("Project deleted");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to delete project")});

  return <div className="mx-auto max-w-7xl space-y-6">
    <PageHeader eyebrow="Workspace" title="Projects" description="Open a project-first research workspace for sources, playground queries, pipelines, experiments, and evaluation." actions={<Button onClick={() => setDialog("create")}><Plus className="size-4" />New project</Button>} />
    <div className="flex flex-col gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 sm:flex-row sm:items-center">
      <label className="relative min-w-0 flex-1"><span className="sr-only">Search projects</span><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--ink-muted)]" /><Input className="pl-9" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search projects" /></label>
      <select value={sort} onChange={(event) => setSort(event.target.value)} className="h-10 rounded-lg border border-[var(--border)] bg-[var(--surface-muted)] px-3 text-xs outline-none" aria-label="Sort projects"><option value="updated">Recently updated</option><option value="name">Name</option></select>
      <div className="flex rounded-lg border border-[var(--border)] p-1"><button className={cn("flex size-8 items-center justify-center rounded-md", view === "grid" ? "bg-[var(--accent-soft)] text-[var(--accent)]" : "text-[var(--ink-muted)]")} onClick={() => setView("grid")} aria-label="Grid view"><Grid2X2 className="size-4" /></button><button className={cn("flex size-8 items-center justify-center rounded-md", view === "list" ? "bg-[var(--accent-soft)] text-[var(--accent)]" : "text-[var(--ink-muted)]")} onClick={() => setView("list")} aria-label="List view"><List className="size-4" /></button></div>
    </div>
    {overview.pending ? <LoadingState label="Loading projects" rows={3} className={view === "grid" ? "grid gap-4 md:grid-cols-2 xl:grid-cols-3 [&>*]:h-64" : undefined} /> : overview.error ? <ErrorState title="Projects could not be loaded" description="The authenticated project API did not return a usable response." onRetry={() => void overview.refetch()} /> : filtered.length ? <div className={view === "grid" ? "grid gap-4 md:grid-cols-2 xl:grid-cols-3" : "space-y-3"}>{filtered.map((project) => <ProjectCard key={project.project_id} project={project} documentCount={stats.get(project.project_id)?.documents ?? null} activeRuns={stats.get(project.project_id)?.active ?? null} view={view} onRename={() => {setSelected(project); setDialog("rename");}} onDelete={() => setDeleting(project)} />)}</div> : <EmptyState icon={FolderKanban} title={search ? "No matching projects" : "No projects yet"} description={search ? "Try a different project name." : "Create your first project to organize sources, runs, traces, and reproducible findings."} action={search ? undefined : "Create project"} onAction={search ? undefined : () => setDialog("create")} />}

    <Dialog open={dialog === "create"} onClose={() => setDialog(null)} title="Create project" description="Create an isolated workspace and choose the initial upload preference."><ProjectForm organizations={organizationsQuery.data ?? []} chunkers={chunkersQuery.data ?? []} isPending={create.isPending} onCancel={() => setDialog(null)} onSubmit={(values) => create.mutate(values)} /></Dialog>
    <Dialog open={dialog === "rename" && Boolean(selected)} onClose={() => {setDialog(null); setSelected(null);}} title="Rename project" description="The Qdrant collection and indexed data remain unchanged.">{selected ? <ProjectForm initialName={selected.name} submitLabel="Save name" isPending={rename.isPending} onCancel={() => {setDialog(null); setSelected(null);}} onSubmit={(values) => rename.mutate(values)} /> : null}</Dialog>
    {deleting ? <ConfirmDeleteDialog open name={deleting.name} title={`Delete ${deleting.name}?`} consequences={`${stats.get(deleting.project_id)?.documents ?? "All"} project documents, the vector collection, and associated query history will no longer be available.`} isPending={remove.isPending} onClose={() => setDeleting(null)} onConfirm={() => remove.mutate(deleting.project_id)} /> : null}
  </div>;
}
