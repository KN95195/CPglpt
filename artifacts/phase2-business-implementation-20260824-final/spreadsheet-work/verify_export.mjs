import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const inputPath = fileURLToPath(new URL('../export-samples/桥梁防撞业务验收项目-BOM-V3-标准模板.xlsx', import.meta.url));
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const table = await workbook.inspect({
  kind: 'table',
  range: '配单明细!A1:H12',
  include: 'values,formulas',
  tableMaxRows: 12,
  tableMaxCols: 8,
});
console.log(table.ndjson);
const errors = await workbook.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',
  options: { useRegex: true, maxResults: 100 },
  summary: 'export formula error scan',
});
console.log(errors.ndjson);
const preview = await workbook.render({ sheetName: '配单明细', autoCrop: 'all', scale: 2, format: 'png' });
await fs.writeFile(fileURLToPath(new URL('../tests/ordinary-export-preview.png', import.meta.url)), new Uint8Array(await preview.arrayBuffer()));
