import fs from 'node:fs/promises';
import path from 'node:path';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const inputDir = path.resolve('tmp/chsi_scores_2026');
const schoolsPath = path.join(inputDir, 'schools_2026.json');
const ocrPath = path.join(inputDir, 'ocr_results.json');
const outputDir = path.resolve('output', 'chsi_scores_2026');
const outputPath = path.join(outputDir, '自划线高校复试分数线_2026.xlsx');
const previewPath = path.join(outputDir, 'preview_summary.png');

const schools = JSON.parse(await fs.readFile(schoolsPath, 'utf8'));
const ocrRows = JSON.parse(await fs.readFile(ocrPath, 'utf8'));

function cleanStatus(value) {
  return value && value.includes('鎴') ? '成功' : value || '';
}

const mergedOcr = new Map();
for (const row of ocrRows) {
  const key = row.school;
  const prefix = `图${row.imageIndex}`;
  const next = `${prefix}：${row.ocrText || ''}`.trim();
  mergedOcr.set(key, mergedOcr.has(key) ? `${mergedOcr.get(key)}\n\n${next}` : next);
}

const workbook = Workbook.create();

const intro = workbook.worksheets.add('说明');
const summary = workbook.worksheets.add('学校汇总');
const ocrSheet = workbook.worksheets.add('OCR明细');

intro.showGridLines = false;
summary.showGridLines = false;
ocrSheet.showGridLines = false;

intro.getRange('A1:F9').values = [
  ['2026年自划线高校复试分数线整理'],
  ['数据来源', '中国研究生招生信息网专题页', '专题页链接', 'https://yz.chsi.com.cn/kyzx/zt/lnfsx2026.shtml', '', ''],
  ['整理范围', '34所自划线高校 2026 年复试分数线页面', '整理日期', '2026-07-30', '', ''],
  ['说明', '研招网官方页面里大量分数线以图片形式发布，本表保留学校汇总、官方链接、图片链接与 OCR 原文，便于筛选与人工校对。', '', '', '', ''],
  ['工作表', '学校汇总', '用途', '按学校查看标题、日期、来源、说明摘要与官方链接', '', ''],
  ['工作表', 'OCR明细', '用途', '按图片查看 OCR 提取文本，适合搜索具体分数线关键词', '', ''],
  ['字段提示', 'OCR文本为机器识别结果，个别字形会有误差；需要最终确认时，请以官方页面和原图为准。', '', '', '', ''],
  ['', '', '', '', '', ''],
  ['', '', '', '', '', ''],
];
intro.getRange('A1:F1').merge();
intro.getRange('A1:F1').format = {
  fill: '#1D4ED8',
  font: { bold: true, color: '#FFFFFF', size: 15 },
  horizontalAlignment: 'center',
  verticalAlignment: 'center',
};
intro.getRange('A2:F7').format = {
  wrapText: true,
  verticalAlignment: 'top',
};
intro.getRange('A2:A7').format.font = { bold: true, color: '#1F2937' };
intro.getRange('C2:C7').format.font = { bold: true, color: '#1F2937' };
intro.getRange('A2:F7').format.borders = { preset: 'all', style: 'thin', color: '#D1D5DB' };
intro.getRange('A1:F7').format.autofitRows();
intro.getRange('A1:F7').format.columnWidth = 22;
intro.getRange('B4:F4').format.columnWidth = 28;

const summaryHeaders = [[
  '序号',
  '学校',
  '年份',
  '标题',
  '发布日期',
  '来源',
  '图片数',
  '说明摘要',
  '官方页面',
]];
summary.getRange('A1:I1').values = summaryHeaders;
const summaryValues = schools.map((row) => [
  row.index,
  row.school,
  row.year,
  row.title,
  row.publishDate,
  row.source,
  row.imageCount,
  row.textSummary,
  row.articleUrl,
]);
summary.getRange(`A2:I${schools.length + 1}`).values = summaryValues;
summary.getRange(`A1:I${schools.length + 1}`).format = {
  verticalAlignment: 'top',
  wrapText: true,
  borders: { preset: 'all', style: 'thin', color: '#E5E7EB' },
};
summary.getRange('A1:I1').format = {
  fill: '#0F766E',
  font: { bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center',
  verticalAlignment: 'center',
};
summary.getRange(`A2:A${schools.length + 1}`).format.horizontalAlignment = 'center';
summary.getRange(`C2:C${schools.length + 1}`).format.horizontalAlignment = 'center';
summary.getRange(`G2:G${schools.length + 1}`).format.horizontalAlignment = 'center';
summary.getRange(`A1:I${schools.length + 1}`).format.autofitRows();
summary.getRange('A:A').format.columnWidth = 8;
summary.getRange('B:B').format.columnWidth = 16;
summary.getRange('C:C').format.columnWidth = 8;
summary.getRange('D:D').format.columnWidth = 34;
summary.getRange('E:E').format.columnWidth = 14;
summary.getRange('F:F').format.columnWidth = 14;
summary.getRange('G:G').format.columnWidth = 8;
summary.getRange('H:H').format.columnWidth = 46;
summary.getRange('I:I').format.columnWidth = 36;
summary.freezePanes.freezeRows(1);

const ocrHeaders = [[
  '学校',
  '年份',
  '图片序号',
  '识别状态',
  '官方页面',
  '图片链接',
  'OCR文本',
]];
ocrSheet.getRange('A1:G1').values = ocrHeaders;
const ocrValues = ocrRows.map((row) => [
  row.school,
  row.year,
  row.imageIndex,
  cleanStatus(row.status),
  row.articleUrl,
  row.imageUrl,
  row.ocrText || '',
]);
ocrSheet.getRange(`A2:G${ocrRows.length + 1}`).values = ocrValues;
ocrSheet.getRange(`A1:G${ocrRows.length + 1}`).format = {
  verticalAlignment: 'top',
  wrapText: true,
  borders: { preset: 'all', style: 'thin', color: '#E5E7EB' },
};
ocrSheet.getRange('A1:G1').format = {
  fill: '#7C3AED',
  font: { bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center',
  verticalAlignment: 'center',
};
ocrSheet.getRange(`B2:C${ocrRows.length + 1}`).format.horizontalAlignment = 'center';
ocrSheet.getRange(`D2:D${ocrRows.length + 1}`).format.horizontalAlignment = 'center';
ocrSheet.getRange(`A1:G${ocrRows.length + 1}`).format.autofitRows();
ocrSheet.getRange('A:A').format.columnWidth = 16;
ocrSheet.getRange('B:B').format.columnWidth = 8;
ocrSheet.getRange('C:C').format.columnWidth = 10;
ocrSheet.getRange('D:D').format.columnWidth = 10;
ocrSheet.getRange('E:E').format.columnWidth = 32;
ocrSheet.getRange('F:F').format.columnWidth = 36;
ocrSheet.getRange('G:G').format.columnWidth = 96;
ocrSheet.freezePanes.freezeRows(1);

await fs.mkdir(outputDir, { recursive: true });

const preview = await workbook.render({
  sheetName: '学校汇总',
  range: `A1:H6`,
  scale: 1,
  format: 'png',
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(outputPath);

console.log(JSON.stringify({ outputPath, previewPath, schools: schools.length, ocrRows: ocrRows.length }));
