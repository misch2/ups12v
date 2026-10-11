const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
let svg = fs.readFileSync(path.join(__dirname, 'phase4-4-native-top.svg'), 'utf8');
svg = svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/, 'width="102mm" height="82mm" viewBox="27 27 102 82"');
sharp(Buffer.from(svg), {density:200}).flatten({background:'#fff'}).png().toFile(path.join(__dirname, 'phase4-4-native-top.png')).then(x => console.log(`${x.width} x ${x.height}`));
