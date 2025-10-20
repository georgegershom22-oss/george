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

function sharesMarginalRi() {
  // Modify shapes so shear rises broadly near 1, conversion slightly reduced, classical reduced in band, interfacial small.
  const classical = (x) => 0.42 - 0.14 * Math.exp(-0.5 * Math.pow((x - 1.05) / 0.35, 2));
  const conversion = (x) => 0.42 * Math.exp(-0.5 * Math.pow((x - 1.0) / 0.38, 2));
  const shear = (x) => 0.12 + 0.32 * Math.exp(-0.5 * Math.pow((x - 1.02) / 0.32, 2));
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

function renderFigureB2(outDir) {
  const { content, plot } = commonAxes('Figure 3.7B2 — Mechanism shares vs ω/N (Marginal Ri)', '');

  const shareFns = normalizeShares(sharesMarginalRi());

  const curves = [
    { key: 'classical', color: COLORS.classical, y: (x) => shareFns(x).classical },
    { key: 'conversion', color: COLORS.conversion, y: (x) => shareFns(x).conversion },
    { key: 'interfacial', color: COLORS.interfacial, y: (x) => shareFns(x).interfacial },
    { key: 'shear', color: COLORS.shear, y: (x) => shareFns(x).shear },
  ];

  content.push(makeStackedAreas(plot.x, plot.y, plot.w, plot.h, curves));

  // Annotation
  content.push(note(plot.x + plot.w * 0.52, plot.y + plot.h * 0.30, 'shear-mediated share expands and can rival conversion near 1'));

  // Legend inside axes (top-right), frame off
  const legX = plot.x + plot.w - 260;
  const legY = plot.y + 30;
  content.push(legendSwatch(legX, legY, 'Classical', COLORS.classical));
  content.push(legendSwatch(legX, legY + 26, 'Mode conversion', COLORS.conversion));
  content.push(legendSwatch(legX, legY + 52, 'Interfacial', COLORS.interfacial));
  content.push(legendSwatch(legX, legY + 78, 'Shear-mediated', COLORS.shear));

  content.push(captionText('Figure 3.7B2. For marginal Ri, shear-mediated loss broadens around the conversion band and can rival conversion near ω/N ∼ 1; classical share correspondingly diminishes.'));

  content.push(svgClose());
  const svg = content.join('');
  const outPath = path.join(outDir, 'figure_3_7B2.svg');
  fs.writeFileSync(outPath, svg, 'utf-8');
  return outPath;
}

if (require.main === module) {
  const outDir = process.argv[2] || path.join(__dirname, '..', 'figures');
  fs.mkdirSync(outDir, { recursive: true });
  const out = renderFigureB2(outDir);
  console.log('Wrote', out);
}

module.exports = { renderFigureB2 };
