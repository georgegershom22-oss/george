const fs = require('fs');
const path = require('path');
const {
  COLORS,
  STROKES,
  FONTS,
  tag,
  svgClose,
  captionText,
  legendSwatch,
  note,
  commonAxes,
  makeStackedAreas,
  toPixelX,
  toPixelY,
  WIDTH,
  HEIGHT,
  svgOpen,
  defs,
} = require('./figure_3_7B_common');

function commonAxesC1(title) {
  // Override x-axis to be log for kδ
  const margin = { top: 120, right: 120, bottom: 160, left: 130 };
  const plot = { x: margin.left, y: margin.top, w: WIDTH - margin.left - margin.right, h: HEIGHT - margin.top - margin.bottom };

  const content = [];
  content.push(svgOpen());
  content.push(defs());
  content.push(tag('rect', { x: 0, y: 0, width: WIDTH, height: HEIGHT, fill: COLORS.background }));
  content.push(tag('text', { x: 100, y: 80, fill: '#111827', 'font-family': 'Helvetica, Arial, sans-serif', 'font-size': 28, 'font-weight': '700' }, title));

  // Grid and axes with specific ticks
  const xVals = [0.1, 0.2, 0.5, 1, 2, 3];
  const xTicks = xVals.map(v => (Math.log10(v) - Math.log10(0.1)) / (Math.log10(3) - Math.log10(0.1)));
  const yVals = [0, 0.25, 0.5, 0.75, 1.0];
  const yTicks = yVals.map(v => v);

  // Grid
  content.push(require('./sharedStyle').gridLines(plot.x, plot.y, plot.w, plot.h, xTicks, yTicks));
  // Axes
  content.push(require('./sharedStyle').axis(plot.x, plot.y, plot.w, plot.h, {
    xTicks,
    xTickLabels: xVals.map(v => String(v)),
    yTicks,
    yTickLabels: yVals.map(v => String(v)),
    xLabel: 'kδ (log scale)',
    yLabel: 'Share (0–1)'
  }));

  return { content, plot };
}

function sharesVsKd() {
  const interfacial = (kd) => {
    // monotone decreasing from ~0.6 at 0.1 to ~0.1 at 3
    const t = (Math.log(kd) - Math.log(0.1)) / (Math.log(3) - Math.log(0.1));
    return 0.62 * (1 - t) + 0.10 * t; // linear in log-kd space
  };
  const classical = (kd) => 0.18 + (0.48 - 0.18) * ((Math.log(kd) - Math.log(0.1)) / (Math.log(3) - Math.log(0.1)));
  const conversion = (kd) => 0.24 + 0.04 * Math.exp(-0.5 * Math.pow((Math.log(kd) - Math.log(1)) / 0.5, 2));
  const shear = (kd) => 0.06; // small, nearly flat
  return { classical, conversion, interfacial, shear };
}

function normalizeShares(fns) {
  return (x) => {
    const raw = {
      classical: Math.max(0, fns.classical(x)),
      conversion: Math.max(0, fns.conversion(x)),
      interfacial: Math.max(0, fns.interfacial(x)),
      shear: Math.max(0, fns.shear(x)),
    };
    const sum = raw.classical + raw.conversion + raw.interfacial + raw.shear;
    return {
      classical: raw.classical / sum,
      conversion: raw.conversion / sum,
      interfacial: raw.interfacial / sum,
      shear: raw.shear / sum,
    };
  };
}

function makeStackedAreasLogX(x0, y0, plotW, plotH, curves) {
  const xs = [];
  const N = 200;
  const xmin = 0.1, xmax = 3;
  for (let i = 0; i <= N; i++) {
    const t = i / N;
    const x = Math.pow(10, Math.log10(xmin) + t * (Math.log10(xmax) - Math.log10(xmin)));
    xs.push(x);
  }
  const cumulative = xs.map(() => 0);
  const layers = [];
  for (const c of curves) {
    const ptsTop = xs.map((x, idx) => {
      const yShare = Math.max(0, Math.min(1, c.y(x)));
      const yCum = cumulative[idx] + yShare;
      cumulative[idx] = yCum;
      const px = x0 + ((Math.log10(x) - Math.log10(xmin)) / (Math.log10(xmax) - Math.log10(xmin))) * plotW;
      const py = y0 + plotH - yCum * plotH;
      return { x: px, y: py };
    });
    const baseline = y0 + plotH;
    const pathD = require('./figure_3_7B_common').areaPath(ptsTop, baseline);
    layers.push(tag('path', { d: pathD, fill: c.color, 'fill-opacity': 1, stroke: 'none' }));
  }
  return layers.join('');
}

function renderFigureC1(outDir) {
  const { content, plot } = commonAxesC1('Figure 3.7C1 — Mechanism shares vs kδ (interface sharpness), fixed ω/N=1');

  const shareFns = normalizeShares(sharesVsKd());
  const curves = [
    { key: 'classical', color: COLORS.classical, y: (x) => shareFns(x).classical },
    { key: 'conversion', color: COLORS.conversion, y: (x) => shareFns(x).conversion },
    { key: 'interfacial', color: COLORS.interfacial, y: (x) => shareFns(x).interfacial },
    { key: 'shear', color: COLORS.shear, y: (x) => shareFns(x).shear },
  ];

  content.push(makeStackedAreasLogX(plot.x, plot.y, plot.w, plot.h, curves));

  // Mini gauge under x-axis
  const x0 = plot.x, y0 = plot.y, w = plot.w, h = plot.h;
  const px = (val) => x0 + ((Math.log10(val) - Math.log10(0.1)) / (Math.log10(3) - Math.log10(0.1))) * w;
  const baseY = plot.y + plot.h + 80;
  content.push(tag('line', { x1: px(0.1), y1: baseY, x2: px(3), y2: baseY, stroke: COLORS.axis, 'stroke-width': STROKES.thin }));
  content.push(tag('text', { x: px(0.1), y: baseY + 26, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, 'thin (0.1)'));
  content.push(tag('text', { x: px(1), y: baseY + 26, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, 'resonant (1)'));
  content.push(tag('text', { x: px(3), y: baseY + 26, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, 'thick (3)'));

  // Legend inside axes (top-right), frame off
  const legX = plot.x + plot.w - 260;
  const legY = plot.y + 30;
  content.push(legendSwatch(legX, legY, 'Classical', COLORS.classical));
  content.push(legendSwatch(legX, legY + 26, 'Mode conversion', COLORS.conversion));
  content.push(legendSwatch(legX, legY + 52, 'Interfacial', COLORS.interfacial));
  content.push(legendSwatch(legX, legY + 78, 'Shear-mediated', COLORS.shear));

  content.push(captionText('Figure 3.7C1. Interfacial share peaks for sharp, high-contrast transitions (low kδ) and decays as the interface becomes diffuse (large kδ). Classical share increases complementarily; conversion and shear change little at fixed ω/N.'));

  content.push(svgClose());
  const svg = content.join('');
  const outPath = path.join(outDir, 'figure_3_7C1.svg');
  fs.writeFileSync(outPath, svg, 'utf-8');
  return outPath;
}

if (require.main === module) {
  const outDir = process.argv[2] || path.join(__dirname, '..', 'figures');
  fs.mkdirSync(outDir, { recursive: true });
  const out = renderFigureC1(outDir);
  console.log('Wrote', out);
}

module.exports = { renderFigureC1 };
