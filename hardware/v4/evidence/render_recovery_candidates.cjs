const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{
for(const [name,x,y,w,h] of [['revised-c9-candidate',52,62,14,12],['recovery-artwork-candidate',36,28,64,15],['recovery-artwork-candidate-j7',115,74,13,14]]){
  const input=name.includes('-j7')?'recovery-artwork-candidate':name;
  let svg=fs.readFileSync(path.join(__dirname,input+'.svg'),'utf8');
  svg=svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/,
    `width="1200" height="${Math.round(1200*h/w)}" viewBox="${x} ${y} ${w} ${h}"`);
  await sharp(Buffer.from(svg)).flatten({background:'#fff'}).png().toFile(path.join(__dirname,name+'-inspection.png'));
}
console.log('Saved three inspection crops');
})();
