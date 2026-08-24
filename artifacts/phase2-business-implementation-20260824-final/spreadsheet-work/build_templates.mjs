import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const outputDir = fileURLToPath(new URL('../tests/', import.meta.url));
await fs.mkdir(outputDir, { recursive: true });

const titleFormat = {
  fill: '#0B66D4',
  font: { bold: true, color: '#FFFFFF', size: 16 },
  horizontalAlignment: 'center',
  verticalAlignment: 'center',
};
const sectionFormat = {
  fill: '#EAF3FF',
  font: { bold: true, color: '#15345B' },
};
const headerFormat = {
  fill: '#DCE9F8',
  font: { bold: true, color: '#19324D' },
  horizontalAlignment: 'center',
  verticalAlignment: 'center',
  borders: { preset: 'inside', style: 'thin', color: '#B9CBE0' },
};

async function savePlaceholderTemplate() {
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add('项目配单');
  sheet.showGridLines = false;
  sheet.mergeCells('A1:I1');
  sheet.getRange('A1').values = [['海智产品中心项目配单']];
  sheet.getRange('A1:I1').format = titleFormat;
  sheet.getRange('A1:I1').format.rowHeight = 30;
  sheet.getRange('A3:F5').values = [
    ['项目名称', '{{project.name}}', '客户名称', '{{project.customer}}', '项目地区', '{{project.region}}'],
    ['业务场景', '{{project.scene}}', 'BOM版本', '{{bom.version}}', '导出日期', '{{export.date}}'],
    ['备注', '{{project.notes}}', null, null, null, null],
  ];
  sheet.getRange('A3:F5').format.borders = { preset: 'inside', style: 'thin', color: '#D6E1EC' };
  sheet.getRange('A3:F5').format.wrapText = true;
  sheet.getRange('A3:A5').format = sectionFormat;
  sheet.getRange('C3:C4').format = sectionFormat;
  sheet.getRange('E3:E4').format = sectionFormat;
  sheet.getRange('A7:I7').values = [['序号', '产品名称', '型号', '数量', '单位', '项目单价', '小计', '用途', '备注']];
  sheet.getRange('A7:I7').format = headerFormat;
  sheet.getRange('A8:I8').values = [['{{bom.lineNo}}', '{{bom.productName}}', '{{bom.model}}', '{{bom.quantity}}', '{{bom.unit}}', '{{bom.unitPrice}}', '{{bom.subtotal}}', '{{bom.purpose}}', '{{bom.note}}']];
  sheet.getRange('A8:I8').format.borders = { preset: 'inside', style: 'thin', color: '#E1E8F0' };
  sheet.getRange('F8:G40').format.numberFormat = '#,##0.00';
  sheet.getRange('A:I').format.columnWidth = 14;
  sheet.getRange('B:B').format.columnWidth = 24;
  sheet.getRange('D:D').format.columnWidth = 24;
  sheet.getRange('F:F').format.columnWidth = 20;
  sheet.getRange('H:I').format.columnWidth = 22;
  sheet.freezePanes.freezeRows(7);
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(`${outputDir}/haizhi-placeholder-template.xlsx`);
  return workbook;
}

async function saveOrdinaryTemplate() {
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add('配单明细');
  sheet.showGridLines = false;
  sheet.mergeCells('A1:H1');
  sheet.getRange('A1').values = [['项目设备与服务清单']];
  sheet.getRange('A1:H1').format = titleFormat;
  sheet.getRange('A3:D5').values = [
    ['项目名称', null, '客户名称', null],
    ['项目地区', null, '业务场景', null],
    ['编制说明', null, null, null],
  ];
  sheet.getRange('A3:D5').format.borders = { preset: 'inside', style: 'thin', color: '#D6E1EC' };
  sheet.getRange('A3:A5').format = sectionFormat;
  sheet.getRange('C3:C4').format = sectionFormat;
  sheet.getRange('A7:H7').values = [['序号', '设备名称', '规格型号', '数量', '单位', '单价', '用途', '备注']];
  sheet.getRange('A7:H7').format = headerFormat;
  sheet.getRange('A8:H8').values = [[null, null, null, null, null, null, null, null]];
  sheet.getRange('A8:H8').format.borders = { preset: 'inside', style: 'thin', color: '#E1E8F0' };
  sheet.getRange('F8:F40').format.numberFormat = '#,##0.00';
  sheet.getRange('A:H').format.columnWidth = 15;
  sheet.getRange('B:B').format.columnWidth = 36;
  sheet.getRange('D:D').format.columnWidth = 24;
  sheet.getRange('G:G').format.columnWidth = 22;
  sheet.getRange('H:H').format.columnWidth = 26;
  sheet.freezePanes.freezeRows(7);
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(`${outputDir}/haizhi-ordinary-template.xlsx`);
  return workbook;
}

const placeholder = await savePlaceholderTemplate();
const ordinary = await saveOrdinaryTemplate();
for (const [name, workbook] of [['placeholder', placeholder], ['ordinary', ordinary]]) {
  const inspected = await workbook.inspect({ kind: 'table', range: name === 'placeholder' ? '项目配单!A1:I8' : '配单明细!A1:H8', include: 'values,formulas', tableMaxRows: 12, tableMaxCols: 10 });
  console.log(name, inspected.ndjson);
  const errors = await workbook.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A', options: { useRegex: true, maxResults: 50 }, summary: `${name} formula scan` });
  console.log(errors.ndjson);
  const preview = await workbook.render({ sheetName: name === 'placeholder' ? '项目配单' : '配单明细', autoCrop: 'all', scale: 2, format: 'png' });
  await fs.writeFile(`${outputDir}/${name}-template-preview.png`, new Uint8Array(await preview.arrayBuffer()));
}
