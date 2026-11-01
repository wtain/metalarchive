// Turns the backend's raw time-axis labels into short, human-friendly ones.
//
// The backend sends different shapes depending on the series:
//   datetime  "2026-11-01T13:37:05.163753"  (naive UTC; per-batch snapshots)
//   day       "2026-11-01"                  (period=daily)
//   week      "2026-44"                     (period=weekly, ISO year-week)
//   month     "2026-11"                     (period=monthly)
// "week" and "month" look alike as strings, so the caller says which one it
// is via `period` rather than us guessing.

export type LabelKind = "datetime" | "day" | "week" | "month";

const SHORT_RANGE_MS = 48 * 60 * 60 * 1000;

export function detectLabelKind(label: string, period?: string): LabelKind {
  if (label.includes("T")) return "datetime";
  if (/^\d{4}-\d{2}-\d{2}$/.test(label)) return "day";
  return period === "weekly" ? "week" : "month";
}

function parseDatetime(label: string): Date {
  // Backend timestamps are naive UTC; mark them so the browser converts to local.
  return new Date(/Z|[+-]\d{2}:\d{2}$/.test(label) ? label : `${label}Z`);
}

function parseDay(label: string): Date {
  const [year, month, day] = label.split("-").map(Number);
  return new Date(year, month - 1, day);
}

// Monday of ISO week `week` in ISO year `year` (week 1 is the one with Jan 4th).
function isoWeekStart(year: number, week: number): Date {
  const jan4 = new Date(year, 0, 4);
  const jan4Weekday = (jan4.getDay() + 6) % 7; // Mon=0
  return new Date(year, 0, 4 - jan4Weekday + (week - 1) * 7);
}

const monthDay = (date: Date) => date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
const hourMinute = (date: Date) => date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });

/** True when a datetime series spans less than 48h, i.e. time of day is worth showing. */
export function isShortRange(labels: string[], period?: string): boolean {
  if (labels.length < 2 || detectLabelKind(labels[0], period) !== "datetime") return false;
  const first = parseDatetime(labels[0]).getTime();
  const last = parseDatetime(labels[labels.length - 1]).getTime();
  return Math.abs(last - first) < SHORT_RANGE_MS;
}

/** Compact axis label: month + day; hour:minute added only for short datetime ranges. */
export function formatAxisLabel(label: string, opts: { period?: string; showTime?: boolean } = {}): string {
  switch (detectLabelKind(label, opts.period)) {
    case "datetime": {
      const date = parseDatetime(label);
      return opts.showTime ? `${monthDay(date)} ${hourMinute(date)}` : monthDay(date);
    }
    case "day":
      return monthDay(parseDay(label));
    case "week": {
      const [year, week] = label.split("-").map(Number);
      return monthDay(isoWeekStart(year, week));
    }
    case "month": {
      const [year, month] = label.split("-").map(Number);
      return new Date(year, month - 1, 1).toLocaleDateString(undefined, { month: "short" });
    }
  }
}

/** Fuller label for tooltips, where there is room: includes the year (and time). */
export function formatTooltipLabel(label: string, period?: string): string {
  switch (detectLabelKind(label, period)) {
    case "datetime": {
      const date = parseDatetime(label);
      return `${monthDay(date)}, ${date.getFullYear()} ${hourMinute(date)}`;
    }
    case "day": {
      const date = parseDay(label);
      return `${monthDay(date)}, ${date.getFullYear()}`;
    }
    case "week": {
      const [year, week] = label.split("-").map(Number);
      const start = isoWeekStart(year, week);
      return `Week of ${monthDay(start)}, ${start.getFullYear()}`;
    }
    case "month": {
      const [year, month] = label.split("-").map(Number);
      return new Date(year, month - 1, 1).toLocaleDateString(undefined, { month: "long", year: "numeric" });
    }
  }
}
