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
    <main className="auth-shell relative isolate min-h-[100svh] overflow-x-hidden bg-[#080808] text-[#f5f1ea]">
      <div className="auth-background" aria-hidden="true">
        <div className="auth-gradient-field" />
        <div className="auth-aurora auth-aurora-one" />
        <div className="auth-aurora auth-aurora-two" />
        <div className="auth-grid-field" />
        <div className="auth-vignette" />
      </div>

      <div className="relative z-10 mx-auto grid min-h-[100svh] w-full max-w-[1400px] items-center gap-6 px-5 py-[clamp(1rem,2.4svh,2rem)] sm:px-8 md:px-10 lg:px-[clamp(2rem,4vw,4rem)] xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.75fr)]">
        <ProductIntroduction />
        <section className="flex items-start justify-center py-2 sm:py-4 xl:items-center xl:py-0">
          <div className="w-full max-w-[460px]">
            <div className="mb-4 lg:hidden">
              <ProductMark compact />
            </div>
            <div className="relative overflow-hidden rounded-[26px] border border-[#2a2a2a] bg-[#111111]/95 p-5 shadow-[0_24px_90px_rgba(0,0,0,0.62),0_0_0_1px_rgba(245,241,234,0.035)] backdrop-blur sm:p-6 lg:p-7">
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
    <section className="relative hidden overflow-hidden xl:flex xl:flex-col xl:justify-center">
      <div className="relative z-10">
        <ProductMark />
      </div>

      <div className="relative z-10 mt-[clamp(0.85rem,1.8svh,1.1rem)] max-w-[720px]">
        <p className="inline-flex items-center gap-2 rounded-full border border-[#e85d9e]/25 bg-[#e85d9e]/10 px-3 py-1.5 font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-[#f5b5d4]">
          <Atom className="size-3.5" aria-hidden="true" />
          Canonical computer science research
        </p>
        <h1 className="mt-[clamp(1.1rem,2.4svh,1.5rem)] max-w-[690px] text-[clamp(2.45rem,3.9vw,4.15rem)] font-semibold leading-[1.01] tracking-[-0.02em] text-[#f5f1ea]">
          Research systems that are{" "}
          <span className="text-[#e85d9e]">traceable</span>,{" "}
          <span className="text-[#f2a65a]">measurable</span>, and{" "}
          <span className="text-[#8ccb6b]">reproducible</span>.
        </h1>
        <p className="mt-[clamp(1rem,2svh,1.35rem)] max-w-[570px] text-[16px] leading-7 text-[#c7bfb4]">
          Define research questions, run experiments, track configurations and
          artifacts, evaluate results, compare runs, and preserve findings in a
          local-first workspace.
        </p>
        <RAGWorkflow />
      </div>

      <div className="relative z-10 mt-[clamp(1rem,2.4svh,1.5rem)] flex flex-wrap gap-2.5 font-mono text-[11px] uppercase tracking-[0.08em] text-[#b8b0a3]">
        {[
          {label: "Research questions", color: "#E85D9E"},
          {label: "Artifact lineage", color: "#6FA8DC"},
          {label: "Evaluation traces", color: "#8CCB6B"},
        ].map((item) => (
          <span
            key={item.label}
            className="rounded-full border bg-[#111111]/80 px-3 py-1 shadow-[0_10px_34px_rgba(0,0,0,0.24)]"
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
    <div className="mt-[clamp(1.45rem,3svh,2rem)] max-w-[660px] rounded-[22px] border border-[#2a2a2a] bg-[#111111]/82 p-3.5 shadow-[0_22px_70px_rgba(0,0,0,0.36),inset_0_1px_0_rgba(245,241,234,0.04)] backdrop-blur">
      <div className="grid items-stretch gap-2.5 xl:grid-cols-3">
        {featureSteps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div
              key={step.title}
              className="group relative flex min-h-[150px] flex-col overflow-hidden rounded-2xl border bg-[#161616] p-3.5 transition duration-200 hover:-translate-y-0.5 hover:bg-[#191919] hover:shadow-[0_18px_42px_rgba(0,0,0,0.28)]"
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
                  className="flex size-9 items-center justify-center rounded-xl border transition group-hover:scale-[1.03]"
                  style={{
                    borderColor: step.border,
                    backgroundColor: step.tint,
                    color: step.accent,
                  }}
                >
                  <Icon className="size-[18px]" strokeWidth={1.9} />
                </span>
              </div>
              <h2 className="mt-4 text-[13px] font-semibold uppercase tracking-[0.12em] text-[#f5f1ea]">
                {step.title}
              </h2>
              <p className="mt-1.5 text-[12.5px] leading-[1.45] text-[#c0b8ae]">
                {step.description}
              </p>
            </div>
          );
        })}
      </div>
      <div className="mt-2.5 rounded-2xl border border-[#2a2a2a] bg-[#080808]/72 p-3.5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[#f5f1ea]">
            <span className="flex size-7 items-center justify-center rounded-lg border border-[#6fa8dc]/30 bg-[#6fa8dc]/10 text-[#9cc6ea]">
              <MessagesSquare className="size-4" />
            </span>
            Document-to-answer workflow
          </div>
          <BrainCircuit className="hidden size-4 text-[#8c6bdb] sm:block" />
        </div>
        <div className="mt-3 grid gap-2 font-mono text-[11.5px] text-[#c0b8ae] xl:grid-cols-[1fr_auto_1fr] xl:items-center">
          <span>
            <span className="text-[#6fa8dc]">Documents</span> {"->"}{" "}
            <span className="text-[#f2a65a]">Chunking</span> {"->"}{" "}
            <span className="text-[#8c6bdb]">Retrieval</span>
          </span>
          <span className="auth-flow-line hidden h-px w-14 bg-gradient-to-r from-[#f2a65a] via-[#8c6bdb] to-[#8ccb6b] xl:block" />
          <span>
            <span className="text-[#f5f1ea]">Grounded answer</span> +{" "}
            <span className="text-[#8ccb6b]">trace</span>
          </span>
        </div>
      </div>
    </div>
  );
}
