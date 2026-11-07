// Crop only the exported SVG review image; never changes CAD.
const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const dir = __dirname;
let svg = fs.readFileSync(path.join(dir, 'phase4-3-initial-placement.svg'), 'utf8');
svg = svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/, 'width="102mm" height="86mm" viewBox="27 24 102 86"');
// Review overlay only: the module library omits its antenna body/keepout.
svg = svg.replace('</svg>', `<g font-family="sans-serif" fill="#173957" font-size="1.6">
<text x="78" y="26.5" text-anchor="middle">96 x 70 mm - cable edge</text>
<rect x="75.4" y="99.2" width="13.2" height="5.4" fill="#e0f4ff" fill-opacity="0.5" stroke="#1676b8" stroke-width="0.15" stroke-dasharray="0.6 0.4"/>
<text x="82" y="107" text-anchor="middle">Antenna envelope (indicative) - keep all layers clear</text>
<text x="82" y="109" text-anchor="middle">15 mm external metal clearance; CAD rule area pending</text>
</g></svg>`);
fs.writeFileSync(path.join(dir, 'phase4-3-placement-review.svg'), svg);
sharp(Buffer.from(svg), {density: 200}).flatten({background:'#ffffff'}).png()
  .toFile(path.join(dir, 'phase4-3-placement-review.png')).then(x => console.log(x.width, x.height));
