import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const require = createRequire('C:/Users/Michal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { Workbook } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const w = Workbook.create();
console.log(w.help('CSV export', {include:'index,examples,notes',maxChars:2500}).ndjson);
