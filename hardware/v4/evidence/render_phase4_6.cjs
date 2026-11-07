const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async () => {
  for (const side of ['top', 'bottom', 'in1']) {
    let svg = fs.readFileSync(path.join(__dirname, `phase4-6-${side}.svg`), 'utf8');
    svg = svg.replace(/width="[^"]+" height="[^"]+" viewBox="[^"]+"/, 'width="31mm" height="26mm" viewBox="43 45 31 26"');
    await sharp(Buffer.from(svg), {density: 150}).resize({width: 1500}).png().toFile(path.join(__dirname, `phase4-6-${side}-detail.png`));
  }
})();
