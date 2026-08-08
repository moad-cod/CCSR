import {
  Atom,
  BrainCircuit,
  DatabaseZap,
  FileText,
  MessagesSquare,
  Route,
  Search,
} from "lucide-react";

const featureSteps = [
  {
    number: "01",
    title: "Ingest",
    description: "Documents, datasets, and source material become structured research artifacts.",
    icon: FileText,
    accent: "#F2A65A",
    tint: "rgba(242,166,90,0.12)",
    border: "rgba(242,166,90,0.32)",
  },
  {
    number: "02",
    title: "Retrieve",
    description: "Hybrid search connects questions to grounded context and evidence.",
    icon: Search,
    accent: "#8C6BDB",
    tint: "rgba(140,107,219,0.13)",
    border: "rgba(140,107,219,0.34)",
  },
  {
    number: "03",
    title: "Observe",
    description: "Traces, metrics, and run history preserve how each answer was produced.",
    icon: Route,
    accent: "#8CCB6B",
    tint: "rgba(140,203,107,0.12)",
    border: "rgba(140,203,107,0.32)",
  },
];

export default function AuthLayout({children}: {children: React.ReactNode}) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#080808] text-[#f5f1ea]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_16%,rgba(232,93,158,0.13),transparent_28%),radial-gradient(circle_at_72%_18%,rgba(111,168,220,0.12),transparent_28%),radial-gradient(circle_at_64%_82%,rgba(242,166,90,0.10),transparent_30%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(245,241,234,0.025)_1px,transparent_1px),linear-gradient(90deg,rgba(245,241,234,0.025)_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(circle_at_42%_34%,black,transparent_72%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_42%,rgba(0,0,0,0.72)_100%)]" />

      <div className="relative z-10 mx-auto grid min-h-screen w-full max-w-[1440px] gap-8 px-5 py-6 sm:px-8 md:px-12 lg:grid-cols-[minmax(0,1.38fr)_minmax(420px,1fr)] lg:px-16">
        <ProductIntroduction />
        <section className="flex min-h-[calc(100vh-3rem)] items-start justify-center py-2 sm:py-6 lg:min-h-0 lg:items-center lg:py-12">
          <div className="w-full max-w-[460px]">
            <div className="mb-5 lg:hidden">
              <ProductMark compact />
            </div>
            <div className="relative overflow-hidden rounded-[28px] border border-[#2a2a2a] bg-[#111111]/95 p-6 shadow-[0_24px_90px_rgba(0,0,0,0.62),0_0_0_1px_rgba(245,241,234,0.035)] backdrop-blur sm:p-8 lg:p-10">
              <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-[#e85d9e]/70 to-transparent" />
              <div className="pointer-events-none absolute -right-16 -top-20 size-48 rounded-full bg-[#8c6bdb]/10 blur-3xl" />
              <div className="relative">{children}</div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function ProductIntroduction() {
  return (
    <section className="relative hidden overflow-hidden py-12 lg:flex lg:min-h-screen lg:flex-col">
      <div className="relative z-10">
        <ProductMark />
      </div>

      <div className="relative z-10 my-auto max-w-[760px]">
        <p className="inline-flex items-center gap-2 rounded-full border border-[#e85d9e]/25 bg-[#e85d9e]/10 px-3 py-1.5 font-mono text-[12px] font-semibold uppercase tracking-[0.14em] text-[#f5b5d4]">
          <Atom className="size-3.5" aria-hidden="true" />
          Canonical computer science research
        </p>
        <h1 className="mt-6 max-w-[720px] text-[44px] font-semibold leading-[1.04] tracking-[-0.02em] text-[#f5f1ea] xl:text-[58px]">
          Research systems that are{" "}
          <span className="text-[#e85d9e]">traceable</span>,{" "}
          <span className="text-[#f2a65a]">measurable</span>, and{" "}
          <span className="text-[#8ccb6b]">reproducible</span>.
        </h1>
        <p className="mt-6 max-w-[590px] text-[17px] leading-8 text-[#b8b0a3]">
          Define research questions, run experiments, track configurations and
          artifacts, evaluate results, compare runs, and preserve findings in a
          local-first workspace.
        </p>
        <RAGWorkflow />
      </div>

      <div className="relative z-10 mt-10 flex flex-wrap gap-3 font-mono text-[12px] uppercase tracking-[0.08em] text-[#b8b0a3]">
        {[
          {label: "Research questions", color: "#E85D9E"},
          {label: "Artifact lineage", color: "#6FA8DC"},
          {label: "Evaluation traces", color: "#8CCB6B"},
        ].map((item) => (
          <span
            key={item.label}
            className="rounded-full border bg-[#111111]/80 px-3 py-1.5 shadow-[0_10px_34px_rgba(0,0,0,0.24)]"
            style={{
              borderColor: `${item.color}52`,
              color: "#d8d0c5",
            }}
          >
            <span
              className="mr-2 inline-block size-1.5 rounded-full align-middle"
              style={{backgroundColor: item.color}}
            />
            {item.label}
          </span>
        ))}
      </div>
    </section>
  );
}

function ProductMark({compact = false}: {compact?: boolean}) {
  return (
    <div className="flex items-center gap-3">
      <span
        className={[
          "relative flex items-center justify-center rounded-2xl border border-[#2a2a2a] bg-[#111111] text-[#f5f1ea] shadow-[0_12px_38px_rgba(0,0,0,0.32)]",
          compact ? "size-10" : "size-11",
        ].join(" ")}
      >
        <span className="absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_28%_18%,rgba(232,93,158,0.38),transparent_34%),radial-gradient(circle_at_70%_80%,rgba(111,168,220,0.30),transparent_38%)]" />
        <DatabaseZap className={compact ? "relative size-4" : "relative size-5"} />
      </span>
      <div>
        <div className={compact ? "text-lg font-semibold" : "text-xl font-semibold"}>
          CCSR
        </div>
        <div className="font-mono text-[11px] uppercase tracking-[0.12em] text-[#b8b0a3]">
          Research control plane
        </div>
      </div>
    </div>
  );
}

function RAGWorkflow() {
  return (
    <div className="mt-12 max-w-[680px] rounded-[24px] border border-[#2a2a2a] bg-[#111111]/82 p-4 shadow-[0_22px_70px_rgba(0,0,0,0.36),inset_0_1px_0_rgba(245,241,234,0.04)] backdrop-blur">
      <div className="grid gap-3 xl:grid-cols-3">
        {featureSteps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div
              key={step.title}
              className="group relative overflow-hidden rounded-2xl border bg-[#161616] p-4 transition duration-200 hover:-translate-y-0.5 hover:bg-[#191919] hover:shadow-[0_18px_42px_rgba(0,0,0,0.28)]"
              style={{borderColor: step.border}}
            >
              <span
                className="pointer-events-none absolute inset-x-0 top-0 h-px opacity-80"
                style={{
                  background: `linear-gradient(90deg, transparent, ${step.accent}, transparent)`,
                }}
              />
              {index < featureSteps.length - 1 ? (
                <span
                  className="absolute left-[calc(100%+0.25rem)] top-1/2 hidden h-px w-2 xl:block"
                  style={{backgroundColor: step.border}}
                />
              ) : null}
              <div className="flex items-center justify-between gap-3">
                <span className="font-mono text-xs text-[#77716a]">{step.number}</span>
                <span
                  className="flex size-10 items-center justify-center rounded-xl border transition group-hover:scale-[1.03]"
                  style={{
                    borderColor: step.border,
                    backgroundColor: step.tint,
                    color: step.accent,
                  }}
                >
                  <Icon className="size-5" strokeWidth={1.9} />
                </span>
              </div>
              <h2 className="mt-5 text-sm font-semibold uppercase tracking-[0.12em] text-[#f5f1ea]">
                {step.title}
              </h2>
              <p className="mt-2 min-h-10 text-[13px] leading-5 text-[#aaa39a]">
                {step.description}
              </p>
            </div>
          );
        })}
      </div>
      <div className="mt-3 rounded-xl border border-[#2a2825] bg-[#0d0d0d] p-4">
        <div className="flex items-center gap-2 text-sm font-medium text-[#f5f1eb]">
          <MessagesSquare className="size-4 text-[#ebe0d1]" />
          Document-to-answer workflow
        </div>
        <div className="mt-3 grid gap-2 font-mono text-[12px] text-[#aaa39a] sm:grid-cols-[1fr_auto_1fr] sm:items-center">
          <span>Documents → Chunking → Retrieval</span>
          <span className="hidden h-px w-8 bg-[#2a2825] sm:block" />
          <span>Grounded answer + trace</span>
        </div>
      </div>
    </div>
  );
}
