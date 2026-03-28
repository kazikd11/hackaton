import { motion } from "framer-motion";
import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { ProcessGraphView } from "../components/ProcessGraph";
import {
  ErrorState,
  LoadingState,
  MiniStat,
  SectionHeading,
  SourceChip,
} from "../components/Primitives";
import { formatCompact, formatHours } from "../lib/format";
import { getProcessDetail } from "../lib/repository";
import { useResource } from "../lib/useResource";

export function ProcessPage() {
  const params = useParams();
  const processId = params.id ?? "";
  const loader = useMemo(() => () => getProcessDetail(processId), [processId]);
  const { loading, error, value } = useResource(loader, [loader]);

  if (loading || !value) {
    return <LoadingState title="Loading process detail" />;
  }

  if (error) {
    return <ErrorState title="Process detail unavailable" message={error} />;
  }

  const { data, source, mode } = value;
  const topWait = [...data.steps].sort((left, right) => right.waitMinutes - left.waitMinutes)[0];
  const topCopy = [...data.steps].sort(
    (left, right) => right.copyPasteSignals - left.copyPasteSignals,
  )[0];
  const topSwitch = [...data.steps].sort(
    (left, right) => right.contextSwitches - left.contextSwitches,
  )[0];
  const recommendedOpportunity =
    data.process.id === "communication"
      ? "opp-comm-sharepoint"
      : data.process.id === "coding" || data.process.id === "coding-activities"
        ? "opp-coding-copypaste"
        : data.process.id === "support" || data.process.id === "youtrack-support"
          ? "opp-youtrack-support"
          : data.process.id === "other" ||
              data.process.id === "unassigned" ||
              data.process.id === "collector"
            ? "opp-unassigned-excel"
            : "opp-youtrack-triage";

  return (
    <div className="space-y-10">
      <section className="panel rounded-[2.5rem] px-6 py-8 md:px-10 md:py-10">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.1fr)_300px]">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <SourceChip source={source} mode={mode} />
              <span className="rounded-full border border-black/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--muted)]">
                / processes / {data.process.id}
              </span>
            </div>
            <h1 className="display-text mt-6 text-5xl leading-[0.96] text-ink md:text-6xl">
              {data.process.name}
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-[color:var(--muted)] md:text-lg">
              {data.process.description} The strongest bottleneck is{" "}
              <span className="font-semibold text-ink">{data.process.bottleneckStep}</span>,
              where the path slows down and context has to be reconstructed by hand.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to={`/opportunities/${recommendedOpportunity}`}
                className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white"
              >
                See ranked opportunity
              </Link>
              <Link
                to="/"
                className="rounded-full border border-black/10 px-5 py-3 text-sm font-semibold text-ink"
              >
                Back to overview
              </Link>
            </div>
          </div>

          <div className="grid gap-4">
            <MiniStat
              label="Cases"
              value={formatCompact(data.process.totalCases)}
              hint="Observed cases in the current mined slice."
            />
            <MiniStat
              label="Cycle time"
              value={formatHours(data.process.avgCycleHours)}
              hint="Average journey length across the visible variants."
            />
            <MiniStat
              label="Manual effort"
              value={formatHours(data.process.manualEffortHours)}
              hint="Estimated annualized effort tied to repeated manual steps."
            />
            <MiniStat
              label="Automation potential"
              value={`${data.process.automationPotential}%`}
              hint="A quick read for how compelling the process is as a demo path."
            />
          </div>
        </div>
      </section>

      <section className="grid gap-8 xl:grid-cols-[minmax(0,1.15fr)_340px]">
        <ProcessGraphView graph={data.graph} />

        <div className="panel rounded-[2rem] p-6">
          <p className="eyebrow">Variant table</p>
          <h2 className="display-text mt-2 text-2xl">What repeats, what diverges</h2>
          <div className="mt-6 space-y-4">
            {data.variants.map((variant) => (
              <div
                key={variant.id}
                className="rounded-[1.5rem] border border-black/10 bg-white/70 px-4 py-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-lg font-semibold text-ink">{variant.label}</p>
                    <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">
                      {variant.narrative}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                      Share
                    </p>
                    <p className="mt-1 text-2xl font-semibold text-ink">
                      {Math.round(variant.share * 100)}%
                    </p>
                  </div>
                </div>
                <div className="mt-4 h-2 overflow-hidden rounded-full bg-black/10">
                  <div
                    className="h-full rounded-full bg-teal"
                    style={{ width: `${variant.share * 100}%` }}
                  />
                </div>
                <div className="mt-4 grid gap-3 text-sm text-[color:var(--muted)] md:grid-cols-3">
                  <p>{variant.cases} cases</p>
                  <p>{variant.avgCycleHours.toFixed(1)}h average cycle</p>
                  <p>{variant.automationFit} automation fit</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <SectionHeading
          eyebrow="Evidence panel"
          title="Bottlenecks, context switching, and copy-heavy work"
          body="This panel keeps the reasoning tactile. The demo can point at one step for delay, one for switching, and one for copy pain without leaving the page."
        />

        <div className="grid gap-4 xl:grid-cols-3">
          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Bottleneck</p>
            <h3 className="display-text mt-2 text-2xl">{topWait.name}</h3>
            <p className="mt-4 text-4xl font-semibold text-ink">
              {topWait.waitMinutes.toFixed(1)}m
            </p>
            <p className="mt-3 text-sm leading-7 text-[color:var(--muted)]">
              Longest average wait. This is where the path slows down and where a
              missing signal often triggers the next human loop.
            </p>
            <p className="mt-4 text-sm leading-7 text-ink">{topWait.evidence[0]}</p>
          </div>

          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Context switching</p>
            <h3 className="display-text mt-2 text-2xl">{topSwitch.name}</h3>
            <p className="mt-4 text-4xl font-semibold text-ink">
              {topSwitch.contextSwitches}
            </p>
            <p className="mt-3 text-sm leading-7 text-[color:var(--muted)]">
              Highest visible tool hopping. The app list below makes it obvious why
              automation or copilot support could remove friction here.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {topSwitch.apps.map((app) => (
                <span
                  key={app}
                  className="rounded-full border border-black/10 px-3 py-1 text-sm"
                >
                  {app}
                </span>
              ))}
            </div>
          </div>

          <div className="panel rounded-[2rem] p-6">
            <p className="eyebrow">Copy and paste pain</p>
            <h3 className="display-text mt-2 text-2xl">{topCopy.name}</h3>
            <p className="mt-4 text-4xl font-semibold text-ink">
              {topCopy.copyPasteSignals}
            </p>
            <p className="mt-3 text-sm leading-7 text-[color:var(--muted)]">
              Strongest copy signal in the process. This is the easiest place for a
              judge to understand why the recommendation is not arbitrary.
            </p>
            <p className="mt-4 text-sm leading-7 text-ink">{topCopy.evidence[0]}</p>
          </div>
        </div>
      </section>

      <section className="panel rounded-[2rem] p-6">
        <p className="eyebrow">Step detail</p>
        <h2 className="display-text mt-2 text-2xl">Observed step signals</h2>
        <div className="mt-6 space-y-4">
          {data.steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.04 * index, duration: 0.35 }}
              className="rounded-[1.5rem] border border-black/10 bg-white/70 px-5 py-5"
            >
              <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)_160px]">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                    Step {step.order}
                  </p>
                  <p className="mt-2 text-xl font-semibold text-ink">{step.name}</p>
                  <p className="mt-3 text-sm text-[color:var(--muted)]">
                    {step.nodeType}
                  </p>
                </div>

                <div>
                  <p className="text-sm leading-7 text-[color:var(--muted)]">
                    {step.evidence[0]}
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {step.apps.map((app) => (
                      <span
                        key={app}
                        className="rounded-full border border-black/10 px-3 py-1 text-sm"
                      >
                        {app}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-2 text-sm text-[color:var(--muted)]">
                  <p>{step.avgDurationMinutes.toFixed(1)}m active</p>
                  <p>{step.waitMinutes.toFixed(1)}m wait</p>
                  <p>{step.manualTouches} manual touches</p>
                  <p>{step.copyPasteSignals} copy signals</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
