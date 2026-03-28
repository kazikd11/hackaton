export const formatHours = (value: number) =>
  `${value.toLocaleString(undefined, {
    maximumFractionDigits: value >= 100 ? 0 : 1,
  })}h`;

export const formatPercent = (value: number) =>
  `${Math.round(value <= 1 ? value * 100 : value)}%`;

export const formatScore = (value: number) => value.toFixed(1);

export const formatCompact = (value: number) =>
  value.toLocaleString(undefined, {
    notation: value >= 1000 ? "compact" : "standard",
    maximumFractionDigits: 1,
  });
