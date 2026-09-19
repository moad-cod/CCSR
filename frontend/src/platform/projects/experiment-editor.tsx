"use client";

import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {ArrowLeft, FlaskConical, LoaderCircle, Save} from "lucide-react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import {useState} from "react";
import {toast} from "sonner";
import {PageHeader} from "@/components/page-header";
import {StatusBadge} from "@/components/status-badge";
import {Button} from "@/components/ui/button";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {Input} from "@/components/ui/input";
import {LoadingState} from "@/components/ui/loading-state";
import {Textarea} from "@/components/ui/textarea";
import {apiFetch} from "@/lib/api";
import type {ResearchExperiment, ResearchStudy} from "@/lib/types";
import {relativeTime} from "@/lib/utils";

export function NewExperiment({projectId}: {projectId: string}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [studyId, setStudyId] = useState(""); const [name, setName] = useState(""); const [objective, setObjective] = useState(""); const [status, setStatus] = useState("planned"); const [configuration, setConfiguration] = useState("{}");
  const studies = useQuery({queryKey: ["research-studies", projectId], queryFn: () => apiFetch<ResearchStudy[]>(`/projects/${projectId}/research/studies`)});
  const create = useMutation({mutationFn: () => {let parsed: Record<string, unknown>; try {parsed = JSON.parse(configuration) as Record<string, unknown>;} catch {throw new Error("Configuration must be valid JSON");} const targetStudy = studyId || studies.data?.[0]?.id; if (!targetStudy) throw new Error("Select a research study"); return apiFetch<ResearchExperiment>(`/projects/${projectId}/research/studies/${targetStudy}/experiments`, {method: "POST", body: JSON.stringify({name, objective: objective || null, status, configuration: parsed})});}, onSuccess: async (experiment) => {await queryClient.invalidateQueries({queryKey: ["research-experiments", projectId]}); toast.success("Experiment created"); router.push(`/projects/${projectId}/experiments/${experiment.id}`);}, onError: (error) => toast.error(error instanceof Error ? error.message : "Unable to create experiment")});
  if (studies.isLoading) return <LoadingState label="Loading research studies" rows={4} />;
  if (studies.isError) return <ErrorState title="Studies unavailable" description="Experiment creation requires an accessible research study." onRetry={() => void studies.refetch()} />;
  if (!studies.data?.length) return <EmptyState icon={FlaskConical} title="Create a research study first" description="Experiments belong to a durable study. Define the research context before creating an experiment." action="Open research" onAction={() => router.push(`/projects/${projectId}/research`)} />;
  const selectedStudy = studyId || studies.data[0].id;
  return <div className="mx-auto max-w-3xl space-y-6"><PageHeader eyebrow="Experiment builder" title="New experiment" description="Create a durable experiment definition backed by the existing research API." actions={<Link href={`/projects/${projectId}/experiments`}><Button variant="secondary"><ArrowLeft className="size-4" />Back</Button></Link>} /><form className="space-y-5 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5" onSubmit={(event) => {event.preventDefault(); if (!studyId) setStudyId(selectedStudy); create.mutate();}}><label className="block"><span className="mb-2 block text-xs font-medium">Research study</span><select value={selectedStudy} onChange={(event) => setStudyId(event.target.value)} className="h-10 w-full rounded-lg border border-[var(--border)] bg-[var(--surface-muted)] px-3 text-sm">{studies.data.map((study) => <option key={study.id} value={study.id}>{study.title}</option>)}</select></label><label className="block"><span className="mb-2 block text-xs font-medium">Experiment name</span><Input value={name} onChange={(event) => setName(event.target.value)} required /></label><label className="block"><span className="mb-2 block text-xs font-medium">Objective</span><Textarea value={objective} onChange={(event) => setObjective(event.target.value)} rows={4} /></label><div className="grid gap-4 sm:grid-cols-2"><label><span className="mb-2 block text-xs font-medium">Status</span><select value={status} onChange={(event) => setStatus(event.target.value)} className="h-10 w-full rounded-lg border border-[var(--border)] bg-[var(--surface-muted)] px-3 text-sm"><option value="planned">Planned</option><option value="running">Running</option><option value="completed">Completed</option><option value="failed">Failed</option><option value="cancelled">Cancelled</option></select></label><label><span className="mb-2 block text-xs font-medium">Configuration JSON</span><Textarea className="font-mono text-xs" value={configuration} onChange={(event) => setConfiguration(event.target.value)} rows={5} /></label></div><div className="flex justify-end"><Button type="submit" disabled={!name.trim() || create.isPending}>{create.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Save className="size-4" />}Create experiment</Button></div></form></div>;
}

export function ExperimentDetail({projectId, experimentId}: {projectId: string; experimentId: string}) {
  const experiments = useQuery({queryKey: ["research-experiments", projectId], queryFn: () => apiFetch<ResearchExperiment[]>(`/projects/${projectId}/research/experiments`)});
  if (experiments.isLoading) return <LoadingState label="Loading experiment" rows={5} />;
  if (experiments.isError) return <ErrorState title="Experiment unavailable" description="The durable experiment index could not be loaded." onRetry={() => void experiments.refetch()} />;
  const experiment = experiments.data?.find((item) => item.id === experimentId);
  if (!experiment) return <EmptyState icon={FlaskConical} title="Experiment not found" description="This experiment is unavailable or no longer belongs to the project." />;
  return <div className="space-y-6"><PageHeader eyebrow="Experiment detail" title={experiment.name} description={experiment.objective ?? "No objective has been recorded."} actions={<Link href={`/projects/${projectId}/experiments`}><Button variant="secondary"><ArrowLeft className="size-4" />Experiments</Button></Link>} /><div className="grid gap-4 md:grid-cols-3"><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><p className="text-[9px] uppercase tracking-[.13em] text-[var(--ink-muted)]">Status</p><div className="mt-3"><StatusBadge status={experiment.status} /></div></section><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><p className="text-[9px] uppercase tracking-[.13em] text-[var(--ink-muted)]">Created</p><p className="mt-3 text-sm font-medium">{relativeTime(experiment.created_at)}</p></section><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"><p className="text-[9px] uppercase tracking-[.13em] text-[var(--ink-muted)]">Study</p><p className="mt-3 truncate font-mono text-[10px]">{experiment.study_id}</p></section></div><section className="rounded-xl border border-[var(--border)] bg-[var(--surface)]"><div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Configuration snapshot</h2></div><pre className="overflow-x-auto p-5 text-xs leading-6 text-[var(--ink-secondary)]">{JSON.stringify(experiment.configuration, null, 2)}</pre></section><p className="text-[10px] leading-5 text-[var(--ink-muted)]">The backend currently exposes experiment definitions through the project experiment index. Execution logs and standardized evaluation metrics remain linked through generic runs and artifacts when those records exist.</p></div>;
}
