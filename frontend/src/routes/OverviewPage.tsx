import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  CoverageBar,
  LoadingState,
  MetricStrip,
  SectionHeading,
  SourceChip,
  StoryLink,
} from "../components/Primitives";
import { formatCompact, formatHours, formatPercent, formatScore } from "../lib/format";
import { getOverview } from "../lib/repository";
import { useResource } from "../lib/useResource";

export function OverviewPage() {
  const { loading, error, value } = useResource(getOverview, []);

  if (loading || !value) {
    return <LoadingState title="Loading overview" />;
  }

  if (error) {
    return <div>{error}</div>;
  }

  const { data, source, mode } = value;

  return (
    <div className="space-y-12">
      <section className="panel rounded-[2.5rem] px-6 py-8 md:px-10 md:py-10">
        <div className="grid gap-10 xl:grid-cols-[minmax(0,1.25fr)_340px]">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <SourceChip source={source} mode={mode} />
              <span className="rounded-full border border-black/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--muted)]">
                {data.refreshLabel}
              </span>
            </div>

            <motion.h1
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55 }}
              className="display-text mt-6 max-w-4xl text-5xl leading-[0.95] text-ink md:text-7xl"
            >
              Process evidence, automation ranking, and a workflow draft in one
              five-minute story.
            </motion.h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-[color:var(--muted)] md:text-lg">
              The guided demo starts with communication work because the event logs
              show a clear pattern: Teams, Youtrack, and Outlook keep repeating the
              same lookup and reply loop. From there, the app makes the evidence,
              score, and workflow definition visible.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to={`/processes/${data.guidedProcessId}`}
                className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white"
              >
                Start guided walkthrough
              </Link>
              <Link
                to={`/workflow/${data.guidedOpportunityId}`}
                className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold text-ink"
              >
                Open workflow studio
              </Link>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-[2rem] border border-black/10 bg-white/80 p-6">
              <p className="eyebrow">Guided in four moves</p>
              <div className="mt-5 space-y-3">
                <StoryLink
                  step="01"
                  label="Ground the demo"
                  body="Show the high-level process families, user coverage, and why communication stands out."
                  to="/"
                />
                <StoryLink
                  step="02"
                  label="Expose the bottleneck"
                  body="Open the process detail and show the graph, variants, and copy-heavy response step."
                  to={`/processes/${data.guidedProcessId}`}
                />
                <StoryLink
                  step="03"
                  label="Explain the ranking"
                  body="Use the opportunity detail to show fixed scoring with visible evidence components."
                  to={`/opportunities/${data.guidedOpportunityId}`}
                />
                <StoryLink
                  step="04"
                  label="Export the workflow"
                  body="End with the generated flow, guardrails, and JSON or YAML export for the handoff."
                  to={`/workflow/${data.guidedOpportunityId}`}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <MetricStrip
        items={[
          {
            label: "Tracked hours",
            value: formatHours(data.totalTrackedHours),
            hint: "Drawn from the challenge exports, including communication, production, coding, and support work.",
          },
          {
            label: "Measured users",
            value: `${data.measuredUsers} / ${data.expectedUsers}`,
            hint: "Coverage is visible enough to rank opportunities while still showing where penalties apply.",
          },
          {
            label: "Opportunity hours",
            value: formatHours(data.opportunityHours),
            hint: "Hours that look recoverable with automation or copilot support in the current signal window.",
          },
          {
            label: "Manual load",
            value: formatPercent(data.averageManualLoad),
            hint: "Average share of work that still depends on human handoffs, message drafting, or repeated data movement.",
          },
        ]}
      />

      <section className="grid gap-8 xl:grid-cols-[minmax(0,1.2fr)_340px]">
        <div className="space-y-6">
          <SectionHeading
            eyebrow="Process families"
            title="A guided shortlist, not a wall of cards"
            body="The first screen stays focused on the families judges need to understand. Each row exposes why the process matters and where the most convincing next click lives."
          />

          <div className="space-y-4">
            {data.families.map((process, index) => (
              <motion.article
                key={process.id}
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * index, duration: 0.45 }}
                className="panel rounded-[2rem] px-5 py-5 md:px-6"
              >
                <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_220px]">
                  <div>
                    <div className="flex flex-wrap items-center gap-3">
                      <p className="display-text text-3xl text-ink">{process.name}</p>
                      {process.unassigned ? (
                        <span className="rounded-full bg-[color:var(--heat-soft)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-rust">
                          exploratory
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-3 max-w-2xl text-sm leading-7 text-[color:var(--muted)] md:text-base">
                      {process.narrative}
                    </p>
                    <div className="mt-5 flex flex-wrap gap-2 text-sm text-[color:var(--muted)]">
                      {process.dominantApps.map((app) => (
                        <span
                          key={app}
                          className="rounded-full border border-black/10 px-3 py-1"
                        >
                          {app}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-[1.5rem] border border-black/10 bg-white/70 p-4">
                    <div className="flex items-end justify-between gap-3">
                      <div>
                        <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                          Automation potential
                        </p>
                        <p className="mt-1 text-3xl font-semibold text-ink">
                          {process.automationPotential}%
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                          Manual effort
                        </p>
                        <p className="mt-1 text-xl font-semibold text-ink">
                          {formatHours(process.manualEffortHours)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 h-2 overflow-hidden rounded-full bg-black/10">
                      <div
                        className="h-full rounded-full bg-teal"
                        style={{ width: `${process.automationPotential}%` }}
                      />
                    </div>
                    <dl className="mt-4 space-y-2 text-sm text-[color:var(--muted)]">
                      <div className="flex justify-between gap-4">
                        <dt>Cases</dt>
                        <dd>{formatCompact(process.totalCases)}</dd>
                      </div>
                      <div className="flex justify-between gap-4">
                        <dt>Variants</dt>
                        <dd>{process.variantCount}</dd>
                      </div>
                      <div className="flex justify-between gap-4">
                        <dt>Context switches</dt>
                        <dd>{process.contextSwitchRate.toFixed(1)} per case</dd>
                      </div>
                    </dl>
                  </div>
                </div>

                <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-black/10 pt-5">
                  <p className="text-sm leading-6 text-[color:var(--muted)]">
                    Bottleneck step:{" "}
                    <span className="font-semibold text-ink">{process.bottleneckStep}</span>
                  </p>
                  <Link
                    to={`/processes/${process.id}`}
                    className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-black hover:text-white"
                  >
                    Explore process
                  </Link>
                </div>
              </motion.article>
            ))}
          </div>
        </div>

        <div className="space-y-5">
          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Coverage and confidence</p>
            <h3 className="display-text mt-2 text-2xl">Signal quality stays visible</h3>
            <p className="mt-4 text-sm leading-7 text-[color:var(--muted)]">
              The app does not hide uncertainty. Unassigned work remains visible,
              and coverage penalties reduce scores instead of pretending the data is complete.
            </p>
            <CoverageBar value={data.processCoverage} />
          </div>

          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Challenge-derived notes</p>
            <div className="mt-4 space-y-4 text-sm leading-7 text-[color:var(--muted)]">
              <p>
                Tool usage is communication-heavy, with Teams as the top measured
                application and Youtrack close behind the main coordination steps.
              </p>
              <p>
                The process distribution shifts from raw collector activity into named
                families after mid-March, which makes the guided story easy to explain.
              </p>
              <p>
                Copy and paste heatmaps are strongest inside IDE, Excel, SharePoint,
                and communication surfaces, which supports the workflow and copilot recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <SectionHeading
          eyebrow="Automation opportunities"
          title="Ranked queue with fixed, visible score components"
          body="The shortlist is opinionated on purpose. Judges can see the component mix behind every rank, then jump straight into the detail or workflow view."
        />

        <div className="space-y-4">
          {data.topOpportunities.map((opportunity) => (
            <div
              key={opportunity.id}
              className="panel rounded-[2rem] px-5 py-5 md:px-6"
            >
              <div className="grid gap-6 lg:grid-cols-[80px_minmax(0,1fr)_160px]">
                <div className="rounded-[1.5rem] bg-ink px-4 py-5 text-center text-white">
                  <p className="text-xs uppercase tracking-[0.18em] text-white/70">
                    Rank
                  </p>
                  <p className="display-text mt-2 text-4xl">{opportunity.rank}</p>
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <p className="display-text text-3xl text-ink">{opportunity.title}</p>
                    <span className="rounded-full bg-[color:var(--accent-soft)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-teal">
                      {opportunity.class}
                    </span>
                  </div>
                  <p className="mt-3 max-w-3xl text-sm leading-7 text-[color:var(--muted)] md:text-base">
                    {opportunity.summary}
                  </p>
                  <div className="mt-5 grid gap-3 md:grid-cols-3">
                    {Object.entries(opportunity.scoreComponents)
                      .slice(0, 3)
                      .map(([label, componentValue]) => (
                        <div
                          key={label}
                          className="rounded-[1.25rem] border border-black/10 bg-white/60 px-4 py-4"
                        >
                          <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                            {label.replaceAll("_", " ")}
                          </p>
                          <p className="mt-2 text-xl font-semibold text-ink">
                            {formatPercent(componentValue)}
                          </p>
                        </div>
                      ))}
                  </div>
                </div>

                <div className="flex flex-col justify-between gap-4 rounded-[1.5rem] border border-black/10 bg-white/70 p-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                      Score
                    </p>
                    <p className="display-text mt-1 text-4xl text-ink">
                      {formatScore(opportunity.score)}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Link
                      to={`/opportunities/${opportunity.id}`}
                      className="block rounded-full bg-ink px-4 py-2 text-center text-sm font-semibold text-white"
                    >
                      Open opportunity
                    </Link>
                    <Link
                      to={`/workflow/${opportunity.id}`}
                      className="block rounded-full border border-black/10 px-4 py-2 text-center text-sm font-semibold text-ink"
                    >
                      Open workflow
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
