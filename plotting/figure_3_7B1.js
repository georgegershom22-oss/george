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

function sharesHighRi() {
  // Smooth qualitative shapes obeying constraints.
  // Use Gaussian-like domes for conversion and tiny shoulder for shear; classical baseline gentle rise.
  const classical = (x) => 0.38 + 0.04 * Math.tanh((x - 1.2) * 1.2);
  const conversion = (x) => 0.5 * Math.exp(-0.5 * Math.pow((x - 1.0) / 0.35, 2));
  const shear = (x) => 0.06 + 0.06 * Math.exp(-0.5 * Math.pow((x - 1.05) / 0.2, 2));
  const interfacial = (x) => 0.08; // small flat
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

function renderFigureB1(outDir) {
  const { content, plot } = commonAxes('Figure 3.7B1 — Mechanism shares vs ω/N (High Ri)', '');

  const shareFns = normalizeShares(sharesHighRi());

  const curves = [
    { key: 'classical', color: COLORS.classical, y: (x) => shareFns(x).classical },
    { key: 'conversion', color: COLORS.conversion, y: (x) => shareFns(x).conversion },
    { key: 'interfacial', color: COLORS.interfacial, y: (x) => shareFns(x).interfacial },
    { key: 'shear', color: COLORS.shear, y: (x) => shareFns(x).shear },
  ];

  content.push(makeStackedAreas(plot.x, plot.y, plot.w, plot.h, curves));

  // Annotations
  content.push(note(plot.x + plot.w * 0.53, plot.y + plot.h * 0.16, 'conversion peak near ω/N ≈ 1'));
  content.push(note(plot.x + plot.w * 0.18, plot.y + plot.h * 0.68, 'classical baseline'));
  content.push(note(plot.x + plot.w * 0.77, plot.y + plot.h * 0.28, 'secondary shear (stable)'));

  // Legend inside axes (top-right), frame off
  const legX = plot.x + plot.w - 260;
  const legY = plot.y + 30;
  content.push(legendSwatch(legX, legY, 'Classical', COLORS.classical));
  content.push(legendSwatch(legX, legY + 26, 'Mode conversion', COLORS.conversion));
  content.push(legendSwatch(legX, legY + 52, 'Interfacial', COLORS.interfacial));
  content.push(legendSwatch(legX, legY + 78, 'Shear-mediated', COLORS.shear));

  content.push(captionText('Figure 3.7B1. Under high Ri and continuous stratification, mode conversion dominates near ω/N ≈ 1; classical loss is the baseline; shear and interfacial contributions are secondary.'));

  content.push(svgClose());
  const svg = content.join('');
  const outPath = path.join(outDir, 'figure_3_7B1.svg');
  fs.writeFileSync(outPath, svg, 'utf-8');
  return outPath;
}

if (require.main === module) {
  const outDir = process.argv[2] || path.join(__dirname, '..', 'figures');
  fs.mkdirSync(outDir, { recursive: true });
  const out = renderFigureB1(outDir);
  console.log('Wrote', out);
}

module.exports = { renderFigureB1 };
