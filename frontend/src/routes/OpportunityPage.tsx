import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ErrorState,
  LoadingState,
  MiniStat,
  SectionHeading,
  SourceChip,
} from "../components/Primitives";
import { ScoreBreakdown } from "../components/ScoreBreakdown";
import { formatHours } from "../lib/format";
import { getOpportunityDetail } from "../lib/repository";
import { useResource } from "../lib/useResource";

export function OpportunityPage() {
  const params = useParams();
  const opportunityId = params.id ?? "";
  const loader = useMemo(
    () => () => getOpportunityDetail(opportunityId),
    [opportunityId],
  );
  const { loading, error, value } = useResource(loader, [loader]);

  if (loading || !value) {
    return <LoadingState title="Loading opportunity detail" />;
  }

  if (error) {
    return <ErrorState title="Opportunity detail unavailable" message={error} />;
  }

  const { data, source, mode } = value;

  return (
    <div className="space-y-10">
      <section className="panel rounded-[2.5rem] px-6 py-8 md:px-10 md:py-10">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.1fr)_300px]">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <SourceChip source={source} mode={mode} />
              <span className="rounded-full bg-[color:var(--accent-soft)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-teal">
                {data.opportunity.class}
              </span>
            </div>

            <h1 className="display-text mt-6 max-w-4xl text-5xl leading-[0.96] text-ink md:text-6xl">
              {data.opportunity.title}
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-[color:var(--muted)] md:text-lg">
              {data.opportunity.summary}
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to={`/workflow/${data.opportunity.id}`}
                className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white"
              >
                Open workflow studio
              </Link>
              <Link
                to={`/processes/${data.process.id}`}
                className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold text-ink"
              >
                Back to process evidence
              </Link>
            </div>
          </div>

          <div className="grid gap-4">
            <MiniStat
              label="Rank"
              value={`#${data.opportunity.rank}`}
              hint="Position in the current automation shortlist."
            />
            <MiniStat
              label="Annualized hours"
              value={formatHours(data.opportunity.annualHours)}
              hint="Estimated recoverable hours if this recommendation lands well."
            />
            <MiniStat
              label="Confidence"
              value={`${Math.round(data.opportunity.confidence * 100)}%`}
              hint="How strongly the available evidence supports this recommendation."
            />
            <MiniStat
              label="Process family"
              value={data.process.name}
              hint="The family this opportunity belongs to in the current ranked demo story."
            />
          </div>
        </div>
      </section>

      <section className="grid gap-8 xl:grid-cols-[minmax(0,1.05fr)_360px]">
        <ScoreBreakdown
          components={data.opportunity.scoreComponents}
          score={data.opportunity.score}
        />

        <div className="panel rounded-[2rem] p-6">
          <p className="eyebrow">Copilot explanation</p>
          <h2 className="display-text mt-2 text-2xl">Why this class fits</h2>
          <p className="mt-4 text-sm leading-7 text-[color:var(--muted)]">
            {data.explanation.headline}
          </p>

          <div className="mt-6 space-y-4">
            {data.explanation.reasoning.map((reason) => (
              <div
                key={reason}
                className="rounded-[1.4rem] border border-black/10 bg-white/70 px-4 py-4 text-sm leading-7 text-[color:var(--muted)]"
              >
                {reason}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <SectionHeading
          eyebrow="Evidence pack"
          title="Grounded reasons, not black-box ranking"
          body="Every score ties back to a process signal that can be shown during the demo. The goal is to make the recommendation legible enough for judges to trust it quickly."
        />

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Object.entries(data.opportunity.evidence).map(([label, body]) => (
            <div key={label} className="panel rounded-[2rem] p-6">
              <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                {label.replace(/[A-Z]/g, (letter) => ` ${letter}`).trim()}
              </p>
              <p className="mt-3 text-sm leading-7 text-[color:var(--muted)]">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="panel rounded-[2rem] p-6">
          <p className="eyebrow">Primary steps</p>
          <h2 className="display-text mt-2 text-2xl">Where the recommendation lands</h2>
          <div className="mt-6 space-y-4">
            {data.opportunity.primarySteps.map((step, index) => (
              <div
                key={step}
                className="flex items-center gap-4 rounded-[1.5rem] border border-black/10 bg-white/70 px-4 py-4"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-full bg-ink text-sm font-semibold text-white">
                  0{index + 1}
                </span>
                <div>
                  <p className="text-lg font-semibold text-ink">{step}</p>
                  <p className="text-sm leading-6 text-[color:var(--muted)]">
                    {data.opportunity.recommendedOutcome}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel rounded-[2rem] p-6">
          <p className="eyebrow">Next actions</p>
          <h2 className="display-text mt-2 text-2xl">Practical handoff</h2>
          <div className="mt-6 space-y-3">
            {data.explanation.nextActions.map((action) => (
              <div
                key={action}
                className="rounded-[1.5rem] border border-black/10 bg-white/70 px-4 py-4 text-sm leading-7 text-[color:var(--muted)]"
              >
                {action}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
