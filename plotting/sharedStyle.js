// Shared style constants and SVG helpers for Figures 3.7

const WIDTH = 2000;
const HEIGHT = 1400;

// Colors
const COLORS = {
  background: '#FFFFFF',
  grid: '#E5E7EB', // light grey
  gridDark: '#9CA3AF', // for centerline
  classical: '#6B7280',
  conversion: '#F4A261',
  conversionDark: '#C06A00',
  interfacial: '#6A4C93',
  shear: '#2A9D8F',
  axis: '#111827',
  text: '#111827',
  legendText: '#111827',
};

// Stroke widths
const STROKES = {
  primary: 3,
  secondary: 2.5,
  thin: 1.2,
  grid: 0.8,
  dotted: 1.2,
};

// Fonts (SVG uses px; map points to px 1:1)
const FONTS = {
  family: 'Helvetica, Arial, sans-serif',
  title: 28,
  axisLabel: 22,
  tick: 16,
  note: 18,
  legend: 16,
  caption: 15,
  subscriptScale: 0.7,
};

// Utility to escape XML special characters
function escapeXml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;');
}

function attrs(a = {}) {
  return Object.entries(a)
    .filter(([, v]) => v !== undefined && v !== null && v !== false)
    .map(([k, v]) => `${k}="${escapeXml(v)}"`)
    .join(' ');
}

function tag(name, a = {}, children = '') {
  const aStr = attrs(a);
  if (children === '' || children === null || children === undefined) {
    return `<${name}${aStr ? ' ' + aStr : ''}/>`;
  }
  return `<${name}${aStr ? ' ' + aStr : ''}>${children}</${name}>`;
}

function svgOpen(width = WIDTH, height = HEIGHT) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">`;
}

function svgClose() {
  return `</svg>`;
}

function defs() {
  // Arrow marker definition and dotted pattern if needed
  return tag('defs', {}, [
    // Arrowhead marker for lines
    tag('marker', {
      id: 'arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto-start-reverse'
    }, tag('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: COLORS.axis })),
    tag('marker', {
      id: 'arrowColored', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto-start-reverse'
    }, tag('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: COLORS.gridDark })),
  ].join(''));
}

function titleText(text) {
  return tag('text', {
    x: 100, y: 80,
    fill: COLORS.text,
    'font-family': FONTS.family,
    'font-size': FONTS.title,
    'font-weight': '700',
  }, escapeXml(text));
}

function captionText(text) {
  return tag('text', {
    x: WIDTH / 2,
    y: HEIGHT - 30,
    fill: COLORS.text,
    'font-family': FONTS.family,
    'font-size': FONTS.caption,
    'font-style': 'italic',
    'text-anchor': 'middle',
  }, escapeXml(text));
}

function legendSwatch(x, y, label, color) {
  return [
    tag('rect', { x, y: y - 12, width: 28, height: 12, fill: color, rx: 2, ry: 2 }),
    tag('text', {
      x: x + 36, y: y - 2,
      fill: COLORS.legendText,
      'font-family': FONTS.family,
      'font-size': FONTS.legend,
      'dominant-baseline': 'ideographic'
    }, escapeXml(label))
  ].join('');
}

function gridLines(x0, y0, plotW, plotH, xTicks, yTicks) {
  const lines = [];
  for (const x of xTicks) {
    const px = x0 + x * plotW;
    lines.push(tag('line', { x1: px, y1: y0, x2: px, y2: y0 + plotH, stroke: COLORS.grid, 'stroke-width': STROKES.grid }));
  }
  for (const y of yTicks) {
    const py = y0 + plotH - y * plotH;
    lines.push(tag('line', { x1: x0, y1: py, x2: x0 + plotW, y2: py, stroke: COLORS.grid, 'stroke-width': STROKES.grid }));
  }
  return lines.join('');
}

function axis(x0, y0, plotW, plotH, {
  xTicks = [], xTickLabels = [], yTicks = [], yTickLabels = [],
  xLabel = '', yLabel = '', xLog = false,
  xFormatter = (d) => String(d), yFormatter = (d) => String(d)
} = {}) {
  const elements = [];
  // Axes lines
  elements.push(tag('line', { x1: x0, y1: y0 + plotH, x2: x0 + plotW, y2: y0 + plotH, stroke: COLORS.axis, 'stroke-width': STROKES.secondary, 'stroke-linecap': 'round' }));
  elements.push(tag('line', { x1: x0, y1: y0, x2: x0, y2: y0 + plotH, stroke: COLORS.axis, 'stroke-width': STROKES.secondary, 'stroke-linecap': 'round' }));

  // Ticks and labels
  for (let i = 0; i < xTicks.length; i++) {
    const t = xTicks[i];
    const px = x0 + t * plotW;
    elements.push(tag('line', { x1: px, y1: y0 + plotH, x2: px, y2: y0 + plotH + 8, stroke: COLORS.axis, 'stroke-width': STROKES.thin }));
    const label = xTickLabels[i] ?? xFormatter(t);
    elements.push(tag('text', { x: px, y: y0 + plotH + 26, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, escapeXml(label)));
  }
  for (let i = 0; i < yTicks.length; i++) {
    const t = yTicks[i];
    const py = y0 + plotH - t * plotH;
    elements.push(tag('line', { x1: x0 - 8, y1: py, x2: x0, y2: py, stroke: COLORS.axis, 'stroke-width': STROKES.thin }));
    const label = yTickLabels[i] ?? yFormatter(t);
    elements.push(tag('text', { x: x0 - 12, y: py + 5, 'text-anchor': 'end', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, escapeXml(label)));
  }

  // Labels
  if (xLabel) {
    elements.push(tag('text', { x: x0 + plotW / 2, y: y0 + plotH + 60, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, xLabel));
  }
  if (yLabel) {
    elements.push(tag('text', { x: x0 - 70, y: y0 + plotH / 2, transform: `rotate(-90 ${x0 - 70} ${y0 + plotH / 2})`, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, yLabel));
  }
  return elements.join('');
}

function dottedLine(x1, y1, x2, y2, color = COLORS.gridDark, width = STROKES.dotted) {
  return tag('line', { x1, y1, x2, y2, stroke: color, 'stroke-width': width, 'stroke-dasharray': '2 6', 'stroke-linecap': 'round' });
}

function dashedLine(x1, y1, x2, y2, color = COLORS.axis, width = STROKES.secondary) {
  return tag('line', { x1, y1, x2, y2, stroke: color, 'stroke-width': width, 'stroke-dasharray': '8 6', 'stroke-linecap': 'round' });
}

function note(x, y, text, anchor = 'start') {
  return tag('text', { x, y, 'text-anchor': anchor, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.note }, escapeXml(text));
}

module.exports = {
  WIDTH,
  HEIGHT,
  COLORS,
  STROKES,
  FONTS,
  escapeXml,
  attrs,
  tag,
  svgOpen,
  svgClose,
  defs,
  titleText,
  captionText,
  legendSwatch,
  gridLines,
  axis,
  dottedLine,
  dashedLine,
  note,
};
