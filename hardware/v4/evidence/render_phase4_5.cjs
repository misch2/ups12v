// Render derived layer plots only; no CAD source is written.
const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async () => {
  for (const side of ['top','bottom','in1','in2']) {
    const file = path.join(__dirname, `phase4-5-${side}.svg`);
    let svg = fs.readFileSync(file, 'utf8').replace(/width="[^"]+" height="[^"]+" viewBox="[^"]+"/, 'width="98mm" height="72mm" viewBox="29 29 98 72"');
    await sharp(Buffer.from(svg), {density: 400}).png().toFile(path.join(__dirname, `phase4-5-${side}.png`));
  }
})();
