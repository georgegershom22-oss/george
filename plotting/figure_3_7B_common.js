const fs = require('fs');
const path = require('path');
const {
  WIDTH,
  HEIGHT,
  COLORS,
  STROKES,
  FONTS,
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
  note,
} = require('./sharedStyle');

function toPixelX(x0, plotW, x, xMin = 0.2, xMax = 2.2) {
  return x0 + ((x - xMin) / (xMax - xMin)) * plotW;
}

function toPixelY(y0, plotH, y) {
  return y0 + plotH - y * plotH;
}

function areaPath(points, baselineY) {
  // points: [{x,y}] in pixel space
  const top = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ');
  const bottom = points.slice().reverse().map((p, i) => `${i === 0 ? 'L' : 'L'} ${p.x.toFixed(2)} ${baselineY.toFixed(2)}`).join(' ');
  return `${top} ${bottom} Z`;
}

function makeStackedAreas(x0, y0, plotW, plotH, curves) {
  // curves: array of {key, color, y(x)} in bottom->top order; shares sum to 1
  // construct x grid
  const xs = [];
  const N = 200;
  const xmin = 0.2, xmax = 2.2;
  for (let i = 0; i <= N; i++) {
    xs.push(xmin + (i / N) * (xmax - xmin));
  }

  // compute stacked tops
  const cumulative = xs.map(() => 0);
  const layers = [];
  for (const c of curves) {
    const ptsTop = xs.map((x, idx) => {
      const yShare = Math.max(0, Math.min(1, c.y(x)));
      const yCum = cumulative[idx] + yShare;
      cumulative[idx] = yCum;
      return { x: toPixelX(x0, plotW, x), y: toPixelY(y0, plotH, yCum) };
    });
    const baseline = toPixelY(y0, plotH, 0);
    const pathD = areaPath(ptsTop, baseline);
    layers.push(tag('path', { d: pathD, fill: c.color, 'fill-opacity': 1, stroke: 'none' }));
  }
  return layers.join('');
}

function conversionBand(x0, y0, plotW, plotH) {
  const xStart = toPixelX(x0, plotW, 0.8);
  const xEnd = toPixelX(x0, plotW, 1.2);
  return tag('rect', { x: xStart, y: y0, width: xEnd - xStart, height: plotH, fill: COLORS.conversion, 'fill-opacity': 0.2 });
}

function centerLine(x0, y0, plotW, plotH) {
  const x = toPixelX(x0, plotW, 1.0);
  return dottedLine(x, y0, x, y0 + plotH, COLORS.gridDark, 1.2);
}

function commonAxes(title, caption, seriesLegend = true) {
  const margin = { top: 120, right: 120, bottom: 140, left: 130 };
  const plot = { x: margin.left, y: margin.top, w: WIDTH - margin.left - margin.right, h: HEIGHT - margin.top - margin.bottom };

  const content = [];
  content.push(svgOpen());
  content.push(defs());
  content.push(tag('rect', { x: 0, y: 0, width: WIDTH, height: HEIGHT, fill: COLORS.background }));
  content.push(titleText(title));

  // Grid (major ticks only on shared set)
  const xTickVals = [0.2, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0];
  const xTicks = xTickVals.map(v => (v - 0.2) / (2.2 - 0.2));
  const yTickVals = [0, 0.25, 0.5, 0.75, 1.0];
  const yTicks = yTickVals.map(v => v);
  content.push(gridLines(plot.x, plot.y, plot.w, plot.h, xTicks, yTicks));

  // Axes
  content.push(axis(plot.x, plot.y, plot.w, plot.h, {
    xTicks,
    xTickLabels: xTickVals.map(v => String(v)),
    yTicks,
    yTickLabels: yTickVals.map(v => String(v)),
    xLabel: 'ω/N',
    yLabel: 'Share (0–1)'
  }));

  // Band and center dotted line
  content.push(conversionBand(plot.x, plot.y, plot.w, plot.h));
  content.push(centerLine(plot.x, plot.y, plot.w, plot.h));

  return { content, plot, margin };
}

module.exports = {
  WIDTH,
  HEIGHT,
  COLORS,
  STROKES,
  FONTS,
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
  note,
  toPixelX,
  toPixelY,
  areaPath,
  makeStackedAreas,
  conversionBand,
  centerLine,
  commonAxes,
};
