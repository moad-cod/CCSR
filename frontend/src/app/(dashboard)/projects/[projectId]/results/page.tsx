import {LabResultsPage} from "@/components/labs/lab-results-page";
import {LabShell} from "@/components/labs/lab-shell";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabResultsPage projectId={projectId} /></LabShell>;
}
