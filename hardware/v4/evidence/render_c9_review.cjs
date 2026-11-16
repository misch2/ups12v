const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
let svg=fs.readFileSync(path.join(__dirname,'c9-review-copper.svg'),'utf8');
svg=svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/,'width="1440" height="1200" viewBox="48 61 18 15"');
sharp(Buffer.from(svg)).flatten({background:'#fff'}).png().toFile(path.join(__dirname,'c9-review-crop.png')).then(x=>console.log(`${x.width}x${x.height}`));
