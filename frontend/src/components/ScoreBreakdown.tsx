import { formatPercent, formatScore } from "../lib/format";
import type { ScoreComponents } from "../types/contracts";

const weights: Record<keyof ScoreComponents, number> = {
  manual_effort: 0.3,
  time_cost: 0.25,
  handoff: 0.2,
  repetition: 0.15,
  variance: 0.1,
  coverage_penalty: -0.1,
};

const labels: Record<keyof ScoreComponents, string> = {
  manual_effort: "Manual effort",
  time_cost: "Time cost",
  handoff: "Handoff load",
  repetition: "Repetition",
  variance: "Variant spread",
  coverage_penalty: "Coverage penalty",
};

export function ScoreBreakdown({
  components,
  score,
}: {
  components: ScoreComponents;
  score: number;
}) {
  return (
    <div className="panel rounded-[2rem] p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Score breakdown</p>
          <h3 className="display-text mt-2 text-2xl">Visible ranking logic</h3>
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
            Final score
          </p>
          <p className="display-text text-5xl">{formatScore(score)}</p>
        </div>
      </div>

      <div className="mt-8 space-y-4">
        {Object.entries(components).map(([key, value]) => {
          const componentKey = key as keyof ScoreComponents;
          const positive = weights[componentKey] >= 0;
          const contribution = (value * weights[componentKey]).toFixed(1);

          return (
            <div key={componentKey}>
              <div className="flex items-center justify-between gap-4 text-sm">
                <div>
                  <p className="font-semibold text-ink">{labels[componentKey]}</p>
                  <p className="text-[color:var(--muted)]">
                    Weight {positive ? "+" : ""}
                    {weights[componentKey].toFixed(2)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-ink">{formatPercent(value)}</p>
                  <p className="text-[color:var(--muted)]">
                    Contribution {positive ? "+" : ""}
                    {contribution}
                  </p>
                </div>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-black/10">
                <div
                  className={`h-full rounded-full ${
                    positive ? "bg-teal" : "bg-rust"
                  }`}
                  style={{ width: `${Math.min(value, 100)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
