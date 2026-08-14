import {PageHeader} from "@/components/page-header";
import {WorkspaceEntry} from "@/components/workspace/workspace-entry";

export function LabTestPage({projectId}: {projectId: string}) {
  return <div className="space-y-6">
    <PageHeader eyebrow="Interactive test" title="Test" description="Run the implemented RAG playground, inspect citations, and turn grounded answers into persisted result evidence." />
    <section className="h-[calc(100dvh-22rem)] min-h-[640px] overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--background)]">
      <WorkspaceEntry projectId={projectId} />
    </section>
  </div>;
}
