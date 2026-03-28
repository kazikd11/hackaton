import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { stringify } from "yaml";
import { CodeBlock } from "../components/CodeBlock";
import {
  ErrorState,
  LoadingState,
  MiniStat,
  SectionHeading,
  SourceChip,
} from "../components/Primitives";
import { getWorkflowStudio } from "../lib/repository";
import { useResource } from "../lib/useResource";

export function WorkflowPage() {
  const params = useParams();
  const workflowId = params.id ?? "";
  const loader = useMemo(() => () => getWorkflowStudio(workflowId), [workflowId]);
  const { loading, error, value } = useResource(loader, [loader]);
  const [format, setFormat] = useState<"json" | "yaml">("json");

  if (loading || !value) {
    return <LoadingState title="Loading workflow studio" />;
  }

  if (error) {
    return <ErrorState title="Workflow studio unavailable" message={error} />;
  }

  const { data, source, mode } = value;
  const jsonExport = JSON.stringify(data.workflow.exportPayload, null, 2);
  const yamlExport = stringify(data.workflow.exportPayload);

  return (
    <div className="space-y-10">
      <section className="panel rounded-[2.5rem] px-6 py-8 md:px-10 md:py-10">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.08fr)_320px]">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <SourceChip source={source} mode={mode} />
              <span className="rounded-full bg-[color:var(--accent-soft)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-teal">
                {data.opportunity.class}
              </span>
            </div>

            <h1 className="display-text mt-6 max-w-4xl text-5xl leading-[0.96] text-ink md:text-6xl">
              {data.workflow.title}
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-[color:var(--muted)] md:text-lg">
              {data.workflow.summary}
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to={`/opportunities/${data.opportunity.id}`}
                className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold text-ink"
              >
                Back to opportunity
              </Link>
              <Link
                to={`/processes/${data.process.id}`}
                className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold text-ink"
              >
                Back to process
              </Link>
            </div>
          </div>

          <div className="grid gap-4">
            <MiniStat
              label="Trigger"
              value="Live event"
              hint={data.workflow.trigger}
            />
            <MiniStat
              label="Systems"
              value={String(data.workflow.systems.length)}
              hint={data.workflow.systems.join(", ")}
            />
            <MiniStat
              label="Guardrails"
              value={String(data.workflow.guardrails.length)}
              hint="Safety checks remain part of the generated workflow definition."
            />
            <MiniStat
              label="Evidence class"
              value={data.explanation.recommendedClass}
              hint="The workflow stays aligned with the opportunity rationale."
            />
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <SectionHeading
          eyebrow="Diagram preview"
          title="A clean workflow the judges can follow at a glance"
          body="The viewer keeps the narrative simple: one trigger, a few actions, an explicit exception gate, and a final output that stays grounded in source evidence."
        />

        <div className="panel rounded-[2rem] p-6">
          <div className="grid gap-4 xl:grid-cols-5">
            {data.workflow.steps.map((step, index) => (
              <div key={step.id} className="relative">
                <div className="rounded-[1.7rem] border border-black/10 bg-white/75 p-5">
                  <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                    {step.type}
                  </p>
                  <p className="mt-2 text-lg font-semibold text-ink">{step.name}</p>
                  <p className="mt-1 text-sm font-medium text-teal">{step.system}</p>
                  <p className="mt-3 text-sm leading-7 text-[color:var(--muted)]">
                    {step.description}
                  </p>
                </div>
                {index < data.workflow.steps.length - 1 ? (
                  <div className="hidden xl:block">
                    <div className="absolute right-[-16px] top-1/2 h-px w-8 -translate-y-1/2 bg-black/20" />
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-8 xl:grid-cols-[340px_minmax(0,1fr)]">
        <div className="space-y-5">
          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Guardrails</p>
            <h2 className="display-text mt-2 text-2xl">Responsible by default</h2>
            <div className="mt-6 space-y-3">
              {data.workflow.guardrails.map((guardrail) => (
                <div
                  key={guardrail}
                  className="rounded-[1.4rem] border border-black/10 bg-white/70 px-4 py-4 text-sm leading-7 text-[color:var(--muted)]"
                >
                  {guardrail}
                </div>
              ))}
            </div>
          </div>

          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Copilot note</p>
            <h2 className="display-text mt-2 text-2xl">Why this export is demo-safe</h2>
            <p className="mt-4 text-sm leading-7 text-[color:var(--muted)]">
              {data.explanation.headline}
            </p>
          </div>
        </div>

        <div className="space-y-5">
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setFormat("json")}
              className={`rounded-full px-4 py-2 text-sm font-semibold ${
                format === "json" ? "bg-ink text-white" : "border border-black/10"
              }`}
            >
              JSON export
            </button>
            <button
              type="button"
              onClick={() => setFormat("yaml")}
              className={`rounded-full px-4 py-2 text-sm font-semibold ${
                format === "yaml" ? "bg-ink text-white" : "border border-black/10"
              }`}
            >
              YAML export
            </button>
          </div>

          <CodeBlock
            label="Workflow export"
            language={format.toUpperCase()}
            content={format === "json" ? jsonExport : yamlExport}
          />
        </div>
      </section>
    </div>
  );
}
