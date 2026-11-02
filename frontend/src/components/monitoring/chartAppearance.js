/** Shared Recharts styling so every chart uses the same recessive axes and grid. */

export const CHART_MARGIN = { top: 8, right: 8, bottom: 0, left: -12 };

export const AXIS_PROPS = {
  stroke: "var(--color-line)",
  tick: { fill: "var(--color-ink-muted)", fontSize: 11 },
  tickLine: false,
};

export const GRID_PROPS = {
  stroke: "var(--color-line)",
  strokeDasharray: undefined,
  vertical: false,
};

export const BAR_MAX_WIDTH = 24;

/** Rounded data-end, square at the baseline. */
export const BAR_TOP_RADIUS = [4, 4, 0, 0];

export const HOVER_CURSOR = { fill: "var(--color-canvas)" };
