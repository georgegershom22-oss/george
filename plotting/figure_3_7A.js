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
  note,
  dottedLine,
  escapeXml,
} = require('./sharedStyle');

function roundedRect(x, y, w, h, r, options = {}) {
  return tag('rect', { x, y, width: w, height: h, rx: r, ry: r, fill: options.fill ?? 'none', stroke: options.stroke ?? COLORS.axis, 'stroke-width': options.strokeWidth ?? STROKES.secondary });
}

function arrow(x1, y1, x2, y2, color = COLORS.axis, width = 1.5, dotted = false) {
  return tag('line', { x1, y1, x2, y2, stroke: color, 'stroke-width': width, 'marker-end': 'url(#arrow)', 'stroke-dasharray': dotted ? '2 6' : undefined, 'stroke-linecap': 'round' });
}

function smallBullet(x, y, color = COLORS.axis) {
  return tag('circle', { cx: x, cy: y, r: 6, fill: color });
}

function similarityThumbnail(x, y, w, h) {
  const elements = [];
  // Frame
  elements.push(roundedRect(x, y, w, h, 10, { fill: 'none', stroke: COLORS.axis }));
  // Axes labels Ri (vertical) and ω/N (horizontal)
  elements.push(tag('text', { x: x + w / 2, y: y + h + 24, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, 'ω/N'));
  elements.push(tag('text', { x: x - 24, y: y + h / 2, transform: `rotate(-90 ${x - 24} ${y + h / 2})`, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.tick }, 'Ri'));
  // Soft regions
  elements.push(tag('rect', { x: x + 0.25 * w, y: y + 0.2 * h, width: 0.5 * w, height: 0.6 * h, fill: COLORS.conversion, 'fill-opacity': 0.18 })); // conversion belt
  elements.push(tag('ellipse', { cx: x + 0.8 * w, cy: y + 0.25 * h, rx: 0.16 * w, ry: 0.12 * h, fill: COLORS.shear, 'fill-opacity': 0.18 })); // shear-favored
  elements.push(tag('ellipse', { cx: x + 0.2 * w, cy: y + 0.75 * h, rx: 0.18 * w, ry: 0.12 * h, fill: COLORS.classical, 'fill-opacity': 0.12 })); // near-classical
  // Labels
  elements.push(tag('text', { x: x + 0.5 * w, y: y + 0.18 * h, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.note }, 'conversion belt'));
  elements.push(tag('text', { x: x + 0.8 * w, y: y + 0.25 * h - 10, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.note }, 'shear-favored'));
  elements.push(tag('text', { x: x + 0.2 * w, y: y + 0.78 * h, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.note }, 'near-classical'));
  return elements.join('');
}

function stackedGauge(x, y, w, h, shares) {
  // shares: { classical, conversion, interfacial, shear } sum to 1
  const order = [
    ['Classical', 'classical'],
    ['Conversion', 'conversion'],
    ['Interfacial', 'interfacial'],
    ['Shear-mediated', 'shear'],
  ];
  let curX = x;
  const elements = [roundedRect(x, y, w, h, 10, { fill: 'none', stroke: COLORS.axis })];
  for (const [label, key] of order) {
    const width = Math.max(0, Math.min(1, shares[key])) * w;
    elements.push(tag('rect', { x: curX, y, width, height: h, fill: COLORS[key] }));
    // Inline label
    elements.push(tag('text', { x: curX + width / 2, y: y + h / 2 + 6, 'text-anchor': 'middle', fill: '#000', 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, label));
    curX += width;
  }
  return elements.join('');
}

function renderFigureA(outDir) {
  const parts = [];
  parts.push(svgOpen());
  parts.push(defs());
  parts.push(tag('rect', { x: 0, y: 0, width: WIDTH, height: HEIGHT, fill: COLORS.background }));
  parts.push(titleText('Figure 3.7A — Composite attenuation concept'));

  // Layout constants
  const margin = { top: 110, right: 80, bottom: 90, left: 80 };

  // Inputs column (A)
  const inputsX = margin.left;
  const inputsY = margin.top + 40;
  const inputsW = 300;
  const inputsH = 520;
  parts.push(roundedRect(inputsX, inputsY, inputsW, inputsH, 14));
  parts.push(tag('text', { x: inputsX + 16, y: inputsY - 10, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel, 'font-weight': '700' }, 'Inputs'));

  const items = [
    'ω/N (frequency ratio)',
    'Ri (stability)',
    'kδ (interface thickness)',
    'CZ, At (contrast)',
    'θ (incidence), r (range)'
  ];
  let iy = inputsY + 40;
  for (const label of items) {
    parts.push(smallBullet(inputsX + 20, iy - 6));
    parts.push(tag('text', { x: inputsX + 40, y: iy, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, label));
    iy += 56;
  }

  // Similarity space cue (B)
  const simX = inputsX + inputsW + 60;
  const simY = margin.top;
  const simW = 520;
  const simH = 320;
  parts.push(similarityThumbnail(simX, simY, simW, simH));
  parts.push(tag('text', { x: simX + 8, y: simY - 10, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel, 'font-weight': '700' }, 'Similarity space cue'));

  // Mechanism weighting module (C)
  const modX = simX + 40;
  const modY = simY + simH + 30;
  const modW = 560;
  const modH = 260;
  parts.push(roundedRect(modX, modY, modW, modH, 16));
  parts.push(tag('text', { x: modX + 16, y: modY - 10, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel, 'font-weight': '700' }, 'Mechanism weighting (shares sum to 1)'));

  // Horizontal gauge (100% stacked)
  const gaugeX = modX + 30;
  const gaugeY = modY + 60;
  const gaugeW = modW - 60;
  const gaugeH = 70;
  parts.push(stackedGauge(gaugeX, gaugeY, gaugeW, gaugeH, { classical: 0.35, conversion: 0.4, interfacial: 0.1, shear: 0.15 }));
  parts.push(tag('text', { x: modX + modW - 80, y: gaugeY + gaugeH + 20, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.note }, '∑wi=1'));
  parts.push(tag('text', { x: modX + 30, y: gaugeY + gaugeH + 46, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': 16 }, escapeXml('shares guided by §3.2 similarity & §3.4–3.6 scalings')));

  // Input arrows to module
  const moduleCenterY = gaugeY + gaugeH / 2;
  for (let i = 0; i < items.length; i++) {
    const y = inputsY + 40 + i * 56 - 6;
    parts.push(arrow(inputsX + inputsW, y, modX, moduleCenterY));
  }

  // Combination node (D)
  const nodeX = modX + modW / 2;
  const nodeY = modY + modH + 70;
  // Sigma-like node (approximate with path)
  const sigmaPath = `M ${nodeX - 30} ${nodeY} C ${nodeX - 10} ${nodeY - 24}, ${nodeX + 10} ${nodeY - 24}, ${nodeX + 30} ${nodeY} C ${nodeX + 10} ${nodeY + 24}, ${nodeX - 10} ${nodeY + 24}, ${nodeX - 30} ${nodeY}`;
  parts.push(tag('path', { d: sigmaPath, stroke: COLORS.axis, 'stroke-width': STROKES.primary, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
  parts.push(tag('text', { x: nodeX, y: nodeY + 48, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, 'Composite attenuation'));
  // Arrow from module to node
  parts.push(arrow(modX + modW / 2, modY + modH, nodeX, nodeY - 26));

  // Outputs column (E)
  const outX = modX + modW + 120;
  const outY = modY + 10;
  const outW = 360;
  const outH = 420;
  parts.push(roundedRect(outX, outY, outW, outH, 14));
  parts.push(tag('text', { x: outX + 16, y: outY - 10, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel, 'font-weight': '700' }, 'Predicted / measured outputs'));
  // Tiny icons
  const iconY0 = outY + 56;
  // TL(ω) curve icon
  parts.push(tag('path', { d: `M ${outX + 30} ${iconY0} C ${outX + 120} ${iconY0 - 24}, ${outX + 180} ${iconY0 + 18}, ${outX + 300} ${iconY0 - 10}`, stroke: COLORS.axis, 'stroke-width': STROKES.secondary, fill: 'none' }));
  parts.push(tag('text', { x: outX + 30, y: iconY0 - 14, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, 'TL(ω)'));
  // γ^2(ω)
  const iconY1 = iconY0 + 90;
  parts.push(tag('path', { d: `M ${outX + 30} ${iconY1} C ${outX + 120} ${iconY1 - 20}, ${outX + 190} ${iconY1 + 30}, ${outX + 300} ${iconY1 - 6}`, stroke: COLORS.axis, 'stroke-width': STROKES.secondary, fill: 'none' }));
  parts.push(tag('circle', { cx: outX + 180, cy: iconY1 + 10, r: 6, fill: COLORS.axis }));
  parts.push(tag('text', { x: outX + 30, y: iconY1 - 14, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, 'γ²(ω)'));
  // PSD width icon
  const iconY2 = iconY1 + 90;
  parts.push(tag('path', { d: `M ${outX + 40} ${iconY2 + 30} Q ${outX + 70} ${iconY2 - 10}, ${outX + 100} ${iconY2 + 30}`, stroke: COLORS.axis, 'stroke-width': STROKES.secondary, fill: 'none' }));
  parts.push(tag('path', { d: `M ${outX + 180} ${iconY2 + 30} Q ${outX + 230} ${iconY2 - 16}, ${outX + 280} ${iconY2 + 30}`, stroke: COLORS.axis, 'stroke-width': STROKES.secondary, fill: 'none' }));
  parts.push(tag('text', { x: outX + 30, y: iconY2 - 14, fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.axisLabel }, 'PSD(ω) width'));

  // Design implications note
  parts.push(arrow(outX + outW / 2, outY + outH, outX + outW / 2, outY + outH + 60));
  parts.push(tag('text', { x: outX + outW / 2, y: outY + outH + 86, 'text-anchor': 'middle', fill: COLORS.text, 'font-family': FONTS.family, 'font-size': FONTS.note }, 'Design implications: Choose ω, θ, Ri, kδ to target mechanisms; update priors with data.'));

  // Priors dotted back-arrow
  parts.push(tag('path', { d: `M ${modX + modW} ${modY + modH / 2} C ${modX + modW + 200} ${modY + modH / 2 - 100}, ${outX - 80} ${outY + outH + 40}, ${modX + modW / 2} ${modY + modH + 20}`,
    stroke: COLORS.gridDark, 'stroke-width': STROKES.dotted, 'stroke-dasharray': '2 6', fill: 'none', 'marker-end': 'url(#arrowColored)'}));
  parts.push(note(modX + modW + 10, modY + modH / 2 - 8, 'priors'));
  parts.push(tag('path', { d: `M ${modX + modW / 2} ${modY + modH + 20} C ${modX + modW / 2 - 100} ${modY + modH + 80}, ${outX} ${outY + outH + 30}, ${outX + outW} ${outY + outH + 10}`,
    stroke: COLORS.axis, 'stroke-width': STROKES.secondary, fill: 'none', 'marker-end': 'url(#arrow)'}));
  parts.push(note(outX + outW - 4, outY + outH + 4, 'posterior (with data)', 'end'));

  // Legend (bottom-right)
  const legX = WIDTH - 420;
  const legY = HEIGHT - 120;
  parts.push(legendSwatch(legX, legY, 'Classical', COLORS.classical));
  parts.push(legendSwatch(legX, legY + 26, 'Mode conversion', COLORS.conversion));
  parts.push(legendSwatch(legX, legY + 52, 'Interfacial', COLORS.interfacial));
  parts.push(legendSwatch(legX, legY + 78, 'Shear-mediated', COLORS.shear));

  // Caption
  parts.push(captionText('Figure 3.7A. Composite attenuation concept. Similarity variables feed a mechanism-weighting module that yields shares summing to unity; these combine into a composite prediction of attenuation and observables used to set priors and design experiments.'));

  parts.push(svgClose());
  const svg = parts.join('');
  const outPath = path.join(outDir, 'figure_3_7A.svg');
  fs.writeFileSync(outPath, svg, 'utf-8');
  return outPath;
}

if (require.main === module) {
  const outDir = process.argv[2] || path.join(__dirname, '..', 'figures');
  fs.mkdirSync(outDir, { recursive: true });
  const out = renderFigureA(outDir);
  console.log('Wrote', out);
}

module.exports = { renderFigureA };
