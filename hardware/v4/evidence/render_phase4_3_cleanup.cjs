const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
let svg = fs.readFileSync(path.join(__dirname, 'phase4-3-cleanup-current.svg'), 'utf8');
svg = svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/, 'width="102mm" height="86mm" viewBox="27 24 102 86"');
svg = svg.replace('</svg>', '<g font-family="sans-serif" fill="#173957" font-size="1.6"><text x="78" y="26.5" text-anchor="middle">96 x 70 mm - right-angle cable edge</text><text x="78" y="106" text-anchor="middle">Placement cleanup incomplete: RF rule area / U1 field pending</text><text x="78" y="109" text-anchor="middle">No routing or copper zones</text></g></svg>');
fs.writeFileSync(path.join(__dirname, 'phase4-3-cleanup-review.svg'), svg);
sharp(Buffer.from(svg), {density:200}).flatten({background:'#fff'}).png().toFile(path.join(__dirname, 'phase4-3-cleanup-review.png')).then(x=>console.log(`${x.width} x ${x.height}`));
