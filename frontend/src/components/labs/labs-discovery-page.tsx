"use client";

import {useMutation, useQueries, useQuery, useQueryClient} from "@tanstack/react-query";
import {FlaskConical, Plus} from "lucide-react";
import {useRouter} from "next/navigation";
import {useMemo, useState} from "react";
import {toast} from "sonner";
import {ConfirmDeleteDialog} from "@/components/confirm-delete-dialog";
import {PageHeader} from "@/components/page-header";
import {ProjectForm, type ProjectFormValues} from "@/components/project-form";
import {Button} from "@/components/ui/button";
import {Dialog} from "@/components/ui/dialog";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {Chunker, Document, IngestionRun, Organization, Project} from "@/lib/types";
import {LabCard} from "./lab-card";
import {LabFilters} from "./lab-filters";
import {inferDomain, type LabDomainId, type LabStats} from "./lab-domain";
import {LabSummary} from "./lab-summary";

const emptyStats: LabStats = {documents: null, active: null, indexed: null, latestRun: null};

export function LabsDiscoveryPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [dialog, setDialog] = useState<"create" | "rename" | null>(null);
  const [selected, setSelected] = useState<Project | null>(null);
  const [deleting, setDeleting] = useState<Project | null>(null);
  const [search, setSearch] = useState("");
  const [domainFilter, setDomainFilter] = useState<LabDomainId>("all");
  const projectsQuery = useQuery({queryKey: ["projects"], queryFn: () => apiFetch<Project[]>("/projects/")});
  const organizationsQuery = useQuery({queryKey: ["organizations"], queryFn: () => apiFetch<Organization[]>("/organizations/"), enabled: dialog === "create"});
  const chunkersQuery = useQuery({queryKey: ["chunkers"], queryFn: () => apiFetch<Chunker[]>("/chunkers"), enabled: dialog === "create"});
  const projects = useMemo(() => projectsQuery.data ?? [], [projectsQuery.data]);
  const documentQueries = useQueries({queries: projects.map((project) => ({queryKey: ["documents", project.project_id], queryFn: () => apiFetch<Document[]>(`/documents/?project_id=${project.project_id}`), staleTime: 30_000}))});
  const runQueries = useQueries({queries: projects.map((project) => ({queryKey: ["ingestion-runs", project.project_id], queryFn: () => apiFetch<IngestionRun[]>(`/ingest/runs?project_id=${project.project_id}&limit=30`), staleTime: 15_000}))});
  const stats = new Map(projects.map((project, index) => {
    const documents = documentQueries[index]?.data;
    const runs = runQueries[index]?.data;
    const latestRun = runs?.[0] ?? null;
    return [project.project_id, {
      documents: documents?.length ?? null,
      active: runs?.filter((run) => !["indexed", "failed", "cancelled"].includes(run.status)).length ?? null,
      indexed: documents?.filter((document) => document.status === "indexed").length ?? null,
      latestRun,
    }];
  }));
  const create = useMutation({mutationFn: (values: ProjectFormValues) => apiFetch<Project>("/projects/", {method: "POST", body: JSON.stringify({name: values.name, organization_id: values.organization_id || null})}), onSuccess: async (project, values) => {localStorage.setItem(`ragforge:project:${project.project_id}:chunker`, values.chunker); await queryClient.invalidateQueries({queryKey: ["projects"]}); toast.success("Lab created"); router.push(`/projects/${project.project_id}/onboarding`);}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to create lab")});
  const rename = useMutation({mutationFn: (values: ProjectFormValues) => apiFetch<Project>(`/projects/${selected?.project_id}`, {method: "PATCH", body: JSON.stringify({name: values.name})}), onSuccess: async () => {await queryClient.invalidateQueries({queryKey: ["projects"]}); setDialog(null); setSelected(null); toast.success("Lab renamed");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to rename lab")});
  const remove = useMutation({mutationFn: (projectId: string) => apiFetch(`/projects/${projectId}`, {method: "DELETE"}), onSuccess: async () => {await queryClient.invalidateQueries({queryKey: ["projects"]}); setDeleting(null); toast.success("Lab deleted");}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to delete lab")});
  const labRecords = projects.map((project) => ({project, domain: inferDomain(project), stats: stats.get(project.project_id) ?? emptyStats}));
  const filtered = labRecords.filter(({project, domain}) => {
    const matchesSearch = project.name.toLowerCase().includes(search.trim().toLowerCase());
    const matchesDomain = domainFilter === "all" || domain.id === domainFilter;
    return matchesSearch && matchesDomain;
  }).sort((a, b) => new Date(b.project.updated_at).getTime() - new Date(a.project.updated_at).getTime());
  const totals = {
    labs: projects.length,
    sources: labRecords.reduce((sum, item) => sum + (item.stats.documents ?? 0), 0),
    active: labRecords.reduce((sum, item) => sum + (item.stats.active ?? 0), 0),
  };

  return <div className="space-y-6">
    <PageHeader eyebrow="Research" title="Labs" description="Discover local CCSR research labs by domain, source readiness, pipeline activity, and reproducible evidence." actions={<Button onClick={() => setDialog("create")}><Plus className="size-4" />New lab</Button>} />
    <LabSummary totals={totals} />
    <LabFilters search={search} domainFilter={domainFilter} onSearchChange={setSearch} onDomainFilterChange={setDomainFilter} />

    {projectsQuery.isLoading ? <LoadingState label="Loading labs" rows={6} className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 [&>*]:h-72" /> : projectsQuery.isError ? <ErrorState title="Labs could not be loaded" description="The authenticated project API did not return a usable response." onRetry={() => void projectsQuery.refetch()} /> : filtered.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{filtered.map(({project, domain, stats: labStats}) => <LabCard key={project.project_id} project={project} domain={domain} stats={labStats} onRename={() => {setSelected(project); setDialog("rename");}} onDelete={() => setDeleting(project)} />)}</div> : <EmptyState icon={FlaskConical} title={search || domainFilter !== "all" ? "No matching labs" : "No labs yet"} description={search || domainFilter !== "all" ? "Try another search or domain filter." : "Create a lab to organize sources, pipeline runs, traces, and reproducible findings."} action={search || domainFilter !== "all" ? undefined : "Create lab"} onAction={search || domainFilter !== "all" ? undefined : () => setDialog("create")} />}

    <Dialog open={dialog === "create"} onClose={() => setDialog(null)} title="Create lab" description="Create an isolated research workspace and choose the initial upload preference."><ProjectForm organizations={organizationsQuery.data ?? []} chunkers={chunkersQuery.data ?? []} isPending={create.isPending} submitLabel="Create lab" onCancel={() => setDialog(null)} onSubmit={(values) => create.mutate(values)} /></Dialog>
    <Dialog open={dialog === "rename" && Boolean(selected)} onClose={() => {setDialog(null); setSelected(null);}} title="Rename lab" description="The Qdrant collection and indexed data remain unchanged.">{selected ? <ProjectForm initialName={selected.name} submitLabel="Save lab" isPending={rename.isPending} onCancel={() => {setDialog(null); setSelected(null);}} onSubmit={(values) => rename.mutate(values)} /> : null}</Dialog>
    {deleting ? <ConfirmDeleteDialog open name={deleting.name} title={`Delete ${deleting.name}?`} consequences={`${stats.get(deleting.project_id)?.documents ?? "All"} lab sources, the vector collection, and associated query history will no longer be available.`} isPending={remove.isPending} onClose={() => setDeleting(null)} onConfirm={() => remove.mutate(deleting.project_id)} /> : null}
  </div>;
}
