const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

async function rasterizeSvgToPng(svgPath, outPath, width = 2000, height = 1400) {
  const svg = fs.readFileSync(svgPath);
  await sharp(svg, { density: 300 })
    .resize(width, height, { fit: 'fill' })
    .png({ compressionLevel: 9 })
    .toFile(outPath);
}

async function main() {
  const figuresDir = path.join(__dirname, '..', 'figures');
  const files = fs.readdirSync(figuresDir).filter(f => f.endsWith('.svg'));
  for (const f of files) {
    const svgPath = path.join(figuresDir, f);
    const pngPath = path.join(figuresDir, f.replace(/\.svg$/, '.png'));
    await rasterizeSvgToPng(svgPath, pngPath, 2000, 1400);
    console.log('Rasterized', path.basename(pngPath));
  }
}

if (require.main === module) {
  main().catch(err => { console.error(err); process.exit(1); });
}
