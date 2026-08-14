import {LabShell} from "@/components/labs/lab-shell";
import {LabTestPage} from "@/components/labs/lab-test-page";

export default async function TestPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabTestPage projectId={projectId} /></LabShell>;
}
