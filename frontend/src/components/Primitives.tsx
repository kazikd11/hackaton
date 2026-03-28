import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { formatCompact, formatPercent } from "../lib/format";
import type { AppMode, DataSource } from "../types/contracts";

export function SourceChip({
  source,
  mode,
}: {
  source: DataSource;
  mode: AppMode;
}) {
  const live = source === "live";

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${
        live
          ? "bg-[color:var(--accent-soft)] text-teal"
          : "bg-[color:var(--heat-soft)] text-rust"
      }`}
    >
      {live ? "Live API" : mode === "live" ? "Fixture backup" : "Fixture mode"}
    </span>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  body,
}: {
  eyebrow: string;
  title: string;
  body: string;
}) {
  return (
    <div className="max-w-2xl">
      <p className="eyebrow">{eyebrow}</p>
      <h2 className="display-text mt-3 text-3xl text-ink md:text-4xl">{title}</h2>
      <p className="mt-4 text-sm leading-7 text-[color:var(--muted)] md:text-base">
        {body}
      </p>
    </div>
  );
}

export function MetricStrip({
  items,
}: {
  items: Array<{ label: string; value: string; hint: string }>;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item, index) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 * index, duration: 0.45 }}
          className="rounded-[1.75rem] border border-black/10 bg-white/70 px-5 py-5"
        >
          <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
            {item.label}
          </p>
          <p className="mt-3 text-3xl font-semibold text-ink">{item.value}</p>
          <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">
            {item.hint}
          </p>
        </motion.div>
      ))}
    </div>
  );
}

export function StoryLink({
  step,
  label,
  body,
  to,
}: {
  step: string;
  label: string;
  body: string;
  to: string;
}) {
  return (
    <Link
      to={to}
      className="group block rounded-[1.6rem] border border-black/10 bg-white/75 px-5 py-5 transition duration-300 hover:-translate-y-1 hover:border-teal/30 hover:bg-white"
    >
      <p className="text-xs uppercase tracking-[0.2em] text-[color:var(--muted)]">
        {step}
      </p>
      <p className="mt-2 text-lg font-semibold text-ink">{label}</p>
      <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">{body}</p>
      <p className="mt-4 text-sm font-semibold text-teal">Open story</p>
    </Link>
  );
}

export function LoadingState({ title }: { title: string }) {
  return (
    <div className="panel rounded-[2rem] p-8">
      <p className="eyebrow">Loading</p>
      <h1 className="display-text mt-3 text-3xl">{title}</h1>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <div
            key={item}
            className="h-36 animate-pulse rounded-[1.5rem] bg-black/5"
          />
        ))}
      </div>
    </div>
  );
}

export function ErrorState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <div className="panel rounded-[2rem] p-8">
      <p className="eyebrow">Unavailable</p>
      <h1 className="display-text mt-3 text-3xl">{title}</h1>
      <p className="mt-4 max-w-xl text-sm leading-7 text-[color:var(--muted)]">
        {message}
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white"
      >
        Back to overview
      </Link>
    </div>
  );
}

export function MiniStat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-[1.5rem] border border-black/10 bg-white/60 px-4 py-4">
      <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">{hint}</p>
    </div>
  );
}

export function CoverageBar({ value }: { value: number }) {
  return (
    <div className="mt-4">
      <div className="h-2 overflow-hidden rounded-full bg-black/10">
        <div
          className="h-full rounded-full bg-teal"
          style={{ width: formatPercent(value) }}
        />
      </div>
      <p className="mt-3 text-sm leading-6 text-[color:var(--muted)]">
        Measured users cover {formatPercent(value)} of the expected audience.
      </p>
    </div>
  );
}

export function CompactMetric({
  label,
  value,
  body,
}: {
  label: string;
  value: number | string;
  body: string;
}) {
  return (
    <div className="rounded-[1.4rem] border border-black/10 bg-white/70 px-4 py-4">
      <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold">
        {typeof value === "number" ? formatCompact(value) : value}
      </p>
      <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">{body}</p>
    </div>
  );
}
