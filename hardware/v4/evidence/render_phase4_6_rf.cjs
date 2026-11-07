// Render the native filled-copper export; never write a CAD document.
const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async () => {
  const source = path.join(__dirname, 'phase4-6-in1.svg');
  let svg = fs.readFileSync(source, 'utf8');
  svg = svg.replace(/width="[^"]+" height="[^"]+" viewBox="[^"]+"/, 'width="20mm" height="6mm" viewBox="72 95 20 6"');
  await sharp(Buffer.from(svg), { density: 150 }).resize({width: 1500}).png().toFile(path.join(__dirname, 'phase4-6-rf-filled-detail.png'));
})();
