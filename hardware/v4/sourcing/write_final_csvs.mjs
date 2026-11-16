// Artifact-tool cell authoring and plain RFC 4180 CSV export (no XLSX requested).
import fs from 'node:fs/promises';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const require = createRequire('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { Workbook } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const base = path.resolve('hardware/v4/sourcing');
const evidence = path.resolve('hardware/v4/evidence/phase5-6-sourcing');
const tables = JSON.parse(await fs.readFile(path.join(evidence, 'final-tables.json'), 'utf8'));
const quote = value => {
  const text = value === null || value === undefined ? '' : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
};
function columnName(index) {
  let name = '';
  for (let n=index; n>0; n=Math.floor((n-1)/26)) name=String.fromCharCode(65+(n-1)%26)+name;
  return name;
}
const report = [];
for (const [name, table] of Object.entries(tables)) {
  const w = Workbook.create();
  const s = w.worksheets.add('PurchaseData');
  const values = [table.columns, ...table.rows.map(r=>table.columns.map(c=>r[c]))];
  const range=s.getRange(`A1:${columnName(table.columns.length)}${values.length}`);
  range.values=values;
  w.recalculate();
  const actual=range.values;
  if (JSON.stringify(actual)!==JSON.stringify(values)) throw new Error(`Cell round-trip mismatch: ${name}`);
  // The documented artifact exporter has no CSV output. Serialize its verified
  // authored cell values directly; preserve text MPNs, decimal precision and URLs.
  await fs.writeFile(path.join(base,name),'\uFEFF'+actual.map(r=>r.map(quote).join(',')).join('\r\n')+'\r\n','utf8');
  const inspected=await w.inspect({kind:'table',range:'PurchaseData!A1:H3',include:'values',tableMaxRows:3,tableMaxCols:8});
  report.push({file:name,rows:table.rows.length,columns:table.columns.length,cellRoundTrip:'PASS',sample:inspected.ndjson});
}
await fs.writeFile(path.join(evidence,'artifact-verification.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.map(({sample,...r})=>r)));
