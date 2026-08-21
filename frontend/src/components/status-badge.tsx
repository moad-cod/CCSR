import {AlertCircle, CheckCircle2, Circle, LoaderCircle, PauseCircle} from "lucide-react";
import {Badge} from "@/components/ui/badge";

export function StatusBadge({status}: {status: string}) {
  const normalized = status.toLowerCase();
  const success = normalized === "indexed" || normalized.includes("completed") || normalized === "ready" || normalized === "answered" || normalized === "used";
  const danger = normalized === "failed" || normalized === "error";
  const warning = normalized === "cancelled" || normalized === "queued";
  const active = normalized === "running" || normalized === "processing" || normalized === "landed";
  const Icon = success ? CheckCircle2 : danger ? AlertCircle : warning ? PauseCircle : active ? LoaderCircle : Circle;
  const label = status.replaceAll("_", " ");
  return <Badge tone={success ? "success" : danger ? "danger" : warning ? "warning" : active ? "info" : "neutral"} className="gap-1.5 capitalize" aria-label={`Status: ${label}`}>
    <Icon className={active ? "size-3 animate-spin" : "size-3"} aria-hidden="true" />
    {label}
  </Badge>;
}
