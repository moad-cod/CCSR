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
    accent: "var(--domain-ml)",
    tint: "rgba(242, 184, 96, 0.10)",
    border: "rgba(242, 184, 96, 0.25)",
  },
  {
    number: "02",
    title: "Retrieve",
    description: "Hybrid search connects questions to grounded context and evidence.",
    icon: Search,
    accent: "var(--research-violet)",
    tint: "rgba(167, 139, 250, 0.10)",
    border: "rgba(167, 139, 250, 0.26)",
  },
  {
    number: "03",
    title: "Observe",
    description: "Traces, metrics, and run history preserve how each answer was produced.",
    icon: Route,
    accent: "var(--success)",
    tint: "rgba(69, 214, 154, 0.10)",
    border: "rgba(69, 214, 154, 0.25)",
  },
];

export default function AuthLayout({children}: {children: React.ReactNode}) {
  return (
    <main className="auth-shell relative isolate min-h-[100svh] overflow-x-hidden bg-[var(--background)] text-[var(--ink)]">
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
            <div className="relative overflow-hidden rounded-[26px] border border-[var(--border-strong)] bg-[var(--surface-glass)] p-5 shadow-[var(--shadow-lg)] backdrop-blur sm:p-6 lg:p-7">
              <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-[var(--accent-soft-line)]" />
              <div className="pointer-events-none absolute -right-16 -top-20 size-48 rounded-full bg-[var(--accent-muted)] blur-3xl" />
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
        <p className="inline-flex items-center gap-2 rounded-full border border-[var(--accent-border)] bg-[var(--accent-soft)] px-3 py-1.5 font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--accent-hover)]">
          <Atom className="size-3.5" aria-hidden="true" />
          Canonical computer science research
        </p>
        <h1 className="mt-[clamp(1.1rem,2.4svh,1.5rem)] max-w-[690px] text-[clamp(2.45rem,3.9vw,4.15rem)] font-semibold leading-[1.01] tracking-[-0.02em] text-[var(--ink)]">
          Research systems that are{" "}
          <span className="text-[var(--accent)]">traceable</span>,{" "}
          <span className="text-[var(--warning)]">measurable</span>, and{" "}
          <span className="text-[var(--success)]">reproducible</span>.
        </h1>
        <p className="mt-[clamp(1rem,2svh,1.35rem)] max-w-[570px] text-[16px] leading-7 text-[var(--ink-secondary)]">
          Define research questions, run experiments, track configurations and
          artifacts, evaluate results, compare runs, and preserve findings in a
          local-first workspace.
        </p>
        <ResearchWorkflow />
      </div>

      <div className="relative z-10 mt-[clamp(1rem,2.4svh,1.5rem)] flex flex-wrap gap-2.5 font-mono text-[11px] uppercase tracking-[0.08em] text-[var(--ink-muted)]">
        {[
          {label: "Research questions", color: "var(--accent)"},
          {label: "Artifact lineage", color: "var(--info)"},
          {label: "Evaluation traces", color: "var(--success)"},
        ].map((item) => (
          <span
            key={item.label}
            className="rounded-full border bg-[var(--surface-panel)] px-3 py-1 shadow-[var(--shadow-sm)]"
            style={{
              borderColor: item.color,
              color: "var(--text-secondary)",
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
          "relative flex items-center justify-center rounded-2xl border border-[var(--border-strong)] bg-[var(--surface)] text-[var(--ink)] shadow-[var(--shadow-sm)]",
          compact ? "size-10" : "size-11",
        ].join(" ")}
      >
        <span className="absolute inset-0 rounded-2xl bg-[var(--accent-muted)]" />
        <DatabaseZap className={compact ? "relative size-4" : "relative size-5"} />
      </span>
      <div>
        <div className={compact ? "text-lg font-semibold" : "text-xl font-semibold"}>
          CCSR
        </div>
        <div className="font-mono text-[11px] uppercase tracking-[0.12em] text-[var(--ink-muted)]">
          Research control plane
        </div>
      </div>
    </div>
  );
}

function ResearchWorkflow() {
  return (
    <div className="mt-[clamp(1.45rem,3svh,2rem)] max-w-[660px] rounded-[22px] border border-[var(--border)] bg-[var(--surface-panel)] p-3.5 shadow-[var(--shadow-md)] backdrop-blur">
      <div className="grid items-stretch gap-2.5 xl:grid-cols-3">
        {featureSteps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div
              key={step.title}
              className="group relative flex min-h-[150px] flex-col overflow-hidden rounded-2xl border bg-[var(--surface-muted)] p-3.5 transition duration-200 hover:-translate-y-0.5 hover:bg-[var(--surface-hover)] hover:shadow-[var(--shadow-md)]"
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
                <span className="font-mono text-xs text-[var(--ink-muted)]">{step.number}</span>
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
              <h2 className="mt-4 text-[13px] font-semibold uppercase tracking-[0.12em] text-[var(--ink)]">
                {step.title}
              </h2>
              <p className="mt-1.5 text-[12.5px] leading-[1.45] text-[var(--ink-secondary)]">
                {step.description}
              </p>
            </div>
          );
        })}
      </div>
      <div className="mt-2.5 rounded-2xl border border-[var(--border)] bg-[var(--background-panel)] p-3.5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[var(--ink)]">
            <span className="flex size-7 items-center justify-center rounded-lg border border-[var(--info-border)] bg-[var(--info-soft)] text-[var(--info)]">
              <MessagesSquare className="size-4" />
            </span>
            Document-to-answer workflow
          </div>
          <BrainCircuit className="hidden size-4 text-[var(--research-violet)] sm:block" />
        </div>
        <div className="mt-3 grid gap-2 font-mono text-[11.5px] text-[var(--ink-secondary)] xl:grid-cols-[1fr_auto_1fr] xl:items-center">
          <span>
            <span className="text-[var(--info)]">Documents</span> {"->"}{" "}
            <span className="text-[var(--warning)]">Chunking</span> {"->"}{" "}
            <span className="text-[var(--research-violet)]">Retrieval</span>
          </span>
          <span className="auth-flow-line hidden h-px w-14 bg-[var(--border-strong)] xl:block" />
          <span>
            <span className="text-[var(--ink)]">Grounded answer</span> +{" "}
            <span className="text-[var(--success)]">trace</span>
          </span>
        </div>
      </div>
    </div>
  );
}
