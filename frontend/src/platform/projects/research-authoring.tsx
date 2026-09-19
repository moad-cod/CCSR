"use client";

import {useMutation, useQueryClient} from "@tanstack/react-query";
import {LoaderCircle, Plus} from "lucide-react";
import {useState} from "react";
import {toast} from "sonner";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Textarea} from "@/components/ui/textarea";
import {apiFetch} from "@/lib/api";
import type {ResearchStudyDetail} from "@/lib/types";

type RecordKind = "study" | "question" | "hypothesis" | "dataset" | "comparison" | "finding";

export function ResearchAuthoring({projectId, study}: {projectId: string; study?: ResearchStudyDetail}) {
  const queryClient = useQueryClient();
  const [kind, setKind] = useState<RecordKind>(study ? "question" : "study");
  const [title, setTitle] = useState("");
  const [detail, setDetail] = useState("");
  const [secondary, setSecondary] = useState("");
  const [selection, setSelection] = useState<string[]>([]);
  const endpoint = kind === "study" ? `/projects/${projectId}/research/studies` : `/projects/${projectId}/research/studies/${study?.id}/${kind === "hypothesis" ? "hypotheses" : `${kind}s`}`;
  const body = () => {
    if (kind === "study") return {title, abstract: detail || null, objective: secondary || null, status: "planned"};
    if (kind === "question") return {question: title, rationale: detail || null};
    if (kind === "hypothesis") return {statement: title, rationale: detail || null, status: "proposed"};
    if (kind === "dataset") return {artifact_id: title, role: secondary || "input", description: detail || null};
    if (kind === "comparison") return {name: title, experiment_ids: selection, criteria: {}, result_summary: {}, conclusion: detail || null};
    return {title, statement: detail, evidence_summary: secondary || null, status: "draft", visibility: "private"};
  };
  const create = useMutation({mutationFn: () => apiFetch(endpoint, {method: "POST", body: JSON.stringify(body())}), onSuccess: async () => {setTitle(""); setDetail(""); setSecondary(""); setSelection([]); await Promise.all([queryClient.invalidateQueries({queryKey: ["research-studies", projectId]}), queryClient.invalidateQueries({queryKey: ["research-study", projectId, study?.id]}), queryClient.invalidateQueries({queryKey: ["research-experiments", projectId]})]); toast.success(`${kind[0].toUpperCase()}${kind.slice(1)} created`);}, onError: (error) => toast.error(error instanceof Error ? error.message : `Unable to create ${kind}`)});
  const options: RecordKind[] = study ? ["question", "hypothesis", "dataset", "comparison", "finding", "study"] : ["study"];
  const needsStatement = kind === "finding";
  const valid = title.trim() && (!needsStatement || detail.trim()) && (kind !== "comparison" || selection.length >= 2);

  return <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)]"><div className="border-b border-[var(--border)] p-4"><h2 className="text-sm font-semibold">Research authoring</h2><p className="mt-1 text-[9px] text-[var(--ink-muted)]">Create durable records supported by the platform research API.</p></div><div className="space-y-4 p-4"><label className="block"><span className="mb-2 block text-xs font-medium">Record type</span><select value={kind} onChange={(event) => setKind(event.target.value as RecordKind)} className="h-10 w-full rounded-lg border border-[var(--border)] bg-[var(--surface-muted)] px-3 text-sm">{options.map((option) => <option key={option} value={option}>{option[0].toUpperCase()}{option.slice(1)}</option>)}</select></label><label className="block"><span className="mb-2 block text-xs font-medium">{kind === "dataset" ? "Artifact ID" : kind === "question" ? "Question" : kind === "hypothesis" ? "Statement" : "Title / name"}</span><Input value={title} onChange={(event) => setTitle(event.target.value)} /></label><label className="block"><span className="mb-2 block text-xs font-medium">{kind === "finding" ? "Finding statement" : kind === "study" ? "Abstract" : kind === "comparison" ? "Conclusion" : "Rationale / description"}</span><Textarea rows={3} value={detail} onChange={(event) => setDetail(event.target.value)} /></label>{kind === "study" || kind === "finding" || kind === "dataset" ? <label className="block"><span className="mb-2 block text-xs font-medium">{kind === "study" ? "Objective" : kind === "finding" ? "Evidence summary" : "Dataset role"}</span>{kind === "dataset" ? <select value={secondary || "input"} onChange={(event) => setSecondary(event.target.value)} className="h-10 w-full rounded-lg border border-[var(--border)] bg-[var(--surface-muted)] px-3 text-sm"><option value="input">Input</option><option value="reference">Reference</option><option value="evaluation">Evaluation</option><option value="output">Output</option></select> : <Textarea rows={2} value={secondary} onChange={(event) => setSecondary(event.target.value)} />}</label> : null}{kind === "comparison" ? <fieldset><legend className="mb-2 text-xs font-medium">Experiments (select at least two)</legend><div className="grid gap-2 sm:grid-cols-2">{study?.experiments.map((experiment) => <label key={experiment.id} className="flex items-center gap-2 rounded-lg border border-[var(--border)] p-2 text-xs"><input type="checkbox" checked={selection.includes(experiment.id)} onChange={(event) => setSelection((current) => event.target.checked ? [...current, experiment.id] : current.filter((id) => id !== experiment.id))} />{experiment.name}</label>)}</div></fieldset> : null}<div className="flex justify-end"><Button disabled={!valid || create.isPending || (kind !== "study" && !study)} onClick={() => create.mutate()}>{create.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Plus className="size-4" />}Create {kind}</Button></div></div></section>;
}
