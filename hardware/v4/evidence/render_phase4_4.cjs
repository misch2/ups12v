const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async () => {
  let svg = fs.readFileSync(path.join(__dirname, 'phase4-4-top.svg'), 'utf8');
  svg = svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/, 'width="102mm" height="86mm" viewBox="27 24 102 86"');
  await sharp(Buffer.from(svg), {density:200}).flatten({background:'#fff'}).png().toFile(path.join(__dirname, 'phase4-4-top.png'));
  let sch = fs.readFileSync(path.join(__dirname, 'phase4-4-schematic.svg'), 'utf8');
  sch = sch.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/, 'width="110mm" height="95mm" viewBox="550 85 110 95"');
  await sharp(Buffer.from(sch), {density:120}).flatten({background:'#fff'}).png().toFile(path.join(__dirname, 'phase4-4-u5-schematic.png'));
  console.log('Rendered top PCB snapshot and U5 schematic crop; no CAD changes.');
})();
