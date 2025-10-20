const fs = require('fs');
const path = require('path');
const { renderFigureA } = require('./figure_3_7A');
const { renderFigureB1 } = require('./figure_3_7B1');
const { renderFigureB2 } = require('./figure_3_7B2');
const { renderFigureC1 } = require('./figure_3_7C1');

function main() {
  const outDir = path.join(__dirname, '..', 'figures');
  fs.mkdirSync(outDir, { recursive: true });

  const outs = [];
  outs.push(renderFigureA(outDir));
  outs.push(renderFigureB1(outDir));
  outs.push(renderFigureB2(outDir));
  outs.push(renderFigureC1(outDir));

  console.log('Generated files:', outs.join('\n'));
}

if (require.main === module) {
  main();
}
