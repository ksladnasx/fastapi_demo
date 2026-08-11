import fs from 'node:fs/promises';
import path from 'node:path';

const TOPIC_URL = 'https://yz.chsi.com.cn/kyzx/zt/lnfsx2026.shtml';
const OUT_DIR = path.resolve('tmp/chsi_scores_2026');
const IMG_DIR = path.join(OUT_DIR, 'images');

const headers = {
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36',
  accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
};

function decodeHtml(text) {
  return text
    .replace(/&nbsp;/g, ' ')
    .replace(/&ensp;/g, ' ')
    .replace(/&emsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function htmlToText(html) {
  return decodeHtml(
    html
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<br\s*\/?\s*>/gi, '\n')
      .replace(/<\/p\s*>/gi, '\n')
      .replace(/<\/div\s*>/gi, '\n')
      .replace(/<[^>]+>/g, ' ')
      .replace(/[ \t\f\v]+/g, ' ')
      .replace(/\n\s+/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim(),
  );
}

function extractVarArray(html, variableName) {
  const start = html.indexOf(`var ${variableName} = [`);
  if (start < 0) throw new Error(`Could not find ${variableName}`);
  const arrayStart = html.indexOf('[', start);
  let depth = 0;
  let inString = false;
  let escaped = false;
  for (let i = arrayStart; i < html.length; i += 1) {
    const ch = html[i];
    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }
    if (ch === '"') inString = true;
    else if (ch === '[') depth += 1;
    else if (ch === ']') {
      depth -= 1;
      if (depth === 0) return html.slice(arrayStart, i + 1);
    }
  }
  throw new Error(`Could not parse ${variableName}`);
}

function articleBody(html) {
  const candidates = [
    /<div[^>]+class=["'][^"']*(?:news-content|article-content|content-l|xl-content|article)[^"']*["'][^>]*>([\s\S]*?)<div[^>]+class=["'][^"']*(?:hot|footer|share|copyright)[^"']*["']/i,
    /<div[^>]+class=["'][^"']*(?:news-content|article-content|content-l|xl-content|article)[^"']*["'][^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*<div/i,
  ];
  for (const re of candidates) {
    const match = html.match(re);
    if (match) return match[1];
  }
  const titleIdx = html.indexOf('<h1');
  const hotIdx = html.indexOf('近期热点');
  return html.slice(Math.max(0, titleIdx), hotIdx > titleIdx ? hotIdx : undefined);
}

function extractMeta(html) {
  const title = decodeHtml((html.match(/<title>([\s\S]*?)<\/title>/i)?.[1] || '').trim());
  const text = htmlToText(html);
  const date = text.match(/(20\d{2}年\d{1,2}月\d{1,2}日)/)?.[1] || '';
  const source = text.match(/来源：([^\s]+(?:大学|学院|研究生院|招生网|研招办|办公室)?)/)?.[1] || '';
  return { title, date, source };
}

function extractContent(html) {
  const body = articleBody(html);
  const images = [...body.matchAll(/<img[^>]+src=["']([^"']+)["'][^>]*>/gi)]
    .map((m) => new URL(m[1], TOPIC_URL).href)
    .filter((url) => /\/news\/img\//.test(url));
  let text = htmlToText(body);
  const cut = text.indexOf('近期热点');
  if (cut >= 0) text = text.slice(0, cut).trim();
  text = text.replace(/^\s*首页[\s\S]*?>\s*/m, '').trim();
  return { text, images: [...new Set(images)] };
}

async function fetchText(url) {
  for (let attempt = 1; attempt <= 4; attempt += 1) {
    try {
      const res = await fetch(url, { headers });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${url}`);
      return res.text();
    } catch (error) {
      if (attempt === 4) throw error;
      await new Promise((resolve) => setTimeout(resolve, attempt * 1800));
    }
  }
}

async function downloadImage(url, filePath, referer) {
  for (let attempt = 1; attempt <= 4; attempt += 1) {
    try {
      const res = await fetch(url, { headers: { ...headers, referer } });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${url}`);
      const buf = Buffer.from(await res.arrayBuffer());
      await fs.writeFile(filePath, buf);
      return buf.length;
    } catch (error) {
      if (attempt === 4) throw error;
      await new Promise((resolve) => setTimeout(resolve, attempt * 1800));
    }
  }
}

function summarizeText(text) {
  const lines = text
    .split(/\n+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .filter((s) => !/^20\d{2}年/.test(s) && !/^来源：/.test(s));
  const useful = lines.filter((s) => /专项|说明|复试|初试|学术|专业|要求|计划|加分|少数民族|退役/.test(s));
  return useful.slice(0, 8).join('；').slice(0, 900);
}

await fs.mkdir(IMG_DIR, { recursive: true });

const topicHtml = await fetchText(TOPIC_URL);
await fs.writeFile(path.join(OUT_DIR, 'topic.html'), topicHtml, 'utf8');
const listText = extractVarArray(topicHtml, 'zhxList');
const schools = JSON.parse(listText);

const rows = [];
for (let i = 0; i < schools.length; i += 1) {
  const school = schools[i];
  const item2026 = school.yearList.find((item) => item.year === '2026');
  if (!item2026) continue;
  const html = await fetchText(item2026.url);
  const meta = extractMeta(html);
  const content = extractContent(html);
  const localImages = [];
  for (let j = 0; j < content.images.length; j += 1) {
    const ext = path.extname(new URL(content.images[j]).pathname) || '.png';
    const fileName = `${String(i + 1).padStart(2, '0')}_${school.yxmc}_${j + 1}${ext}`.replace(/[\\/:*?"<>|]/g, '_');
    const filePath = path.join(IMG_DIR, fileName);
    const bytes = await downloadImage(content.images[j], filePath, item2026.url);
    localImages.push({ url: content.images[j], path: filePath, bytes });
  }
  rows.push({
    index: rows.length + 1,
    school: school.yxmc,
    year: 2026,
    title: meta.title,
    publishDate: meta.date,
    source: meta.source,
    articleUrl: item2026.url,
    imageCount: localImages.length,
    imageUrls: localImages.map((x) => x.url).join('\n'),
    localImagePaths: localImages.map((x) => x.path).join('\n'),
    textSummary: summarizeText(content.text),
  });
  console.log(`${rows.length}/${schools.length} ${school.yxmc} images=${localImages.length}`);
  await new Promise((resolve) => setTimeout(resolve, 500));
}

await fs.writeFile(path.join(OUT_DIR, 'schools_2026.json'), JSON.stringify(rows, null, 2), 'utf8');
console.log(`Saved ${rows.length} rows to ${path.join(OUT_DIR, 'schools_2026.json')}`);
