const fs = require("fs");
const path = require("path");
const cheerio = require("cheerio");

const ROOT = path.resolve(__dirname, "..");
const posix = path.posix;

const SKIP_FILES = new Set(["google8a2939e9b7d79b04.html"]);
const SKIP_DIRS = new Set([".git", "node_modules"]);
const SKIP_TEXT_PARENTS = new Set([
  "script",
  "style",
  "svg",
  "path",
  "code",
  "pre",
  "noscript",
]);

const EXACT_TRANSLATIONS = new Map([
  ["About Us / Our Story", "私たちについて"],
  ["About Us / Our Story | Barcode-Generators.com", "私たちについて | Barcode-Generators.com"],
  ["Who We Are", "私たちについて"],
  ["Our Story", "沿革"],
  ["Contact Us", "お問い合わせ"],
  ["Contact Us | Barcode-Generators.com", "お問い合わせ | Barcode-Generators.com"],
  ["Search Results", "検索結果"],
  ["Search Results | Barcode-Generators.com", "検索結果 | Barcode-Generators.com"],
  ["HTML Sitemap", "HTMLサイトマップ"],
  ["HTML Sitemap | Barcode-Generators.com", "HTMLサイトマップ | Barcode-Generators.com"],
  ["Compliance Hub", "コンプライアンスハブ"],
  ["Compliance Guides", "コンプライアンスガイド"],
  ["Developer Docs", "開発者向けドキュメント"],
  ["Future of Barcode Logistics Hub", "バーコード物流の未来ハブ"],
  ["Privacy Policy", "プライバシーポリシー"],
  ["Terms of Service", "利用規約"],
  ["プライバシーポリシー (Privacy Policy)", "プライバシーポリシー"],
  ["利用規約 (Terms of Service)", "利用規約"],
  ["Supporting Compliance Guides", "関連するコンプライアンスガイド"],
  ["FAQ for Developers", "開発者向けFAQ"],
  ["plain English", "わかりやすい説明"],
  ["Compliance Hub — Barcode Generators", "コンプライアンスハブ | Barcode Generators"],
  ["Developer Docs | Barcode Generators", "開発者向けドキュメント | Barcode Generators"],
  ["Future of Barcode Logistics Hub | Barcode Generators", "バーコード物流の未来ハブ | Barcode Generators"],
  ["Enterprise Barcode Security & Scale Hub | Barcode Generators", "エンタープライズ向けバーコード運用ハブ | Barcode Generators"],
]);

const CLEANUP_REPLACEMENTS = [
  [/Privacy Policy/gi, "プライバシーポリシー"],
  [/Terms of Service/gi, "利用規約"],
  [/Search Results/gi, "検索結果"],
  [/Contact Us/gi, "お問い合わせ"],
  [/About Us/gi, "私たちについて"],
  [/Our Story/gi, "沿革"],
  [/Who We Are/gi, "私たちについて"],
  [/Compliance Guides/gi, "コンプライアンスガイド"],
  [/Developer Docs/gi, "開発者向けドキュメント"],
  [/Future of Barcode Logistics Hub/gi, "バーコード物流の未来ハブ"],
];

const CHROME_STYLE = `
<style data-site-chrome>
  .jp-site-fixed > header:not(.site-chrome) {
    display: none !important;
  }

  .jp-site-fixed .top-nav,
  .jp-site-fixed .modern-footer {
    display: none !important;
  }

  .jp-site-fixed > footer:not(.site-footer) {
    display: none !important;
  }

  .site-chrome {
    position: sticky;
    top: 0;
    z-index: 3000;
    background: rgba(255, 255, 255, 0.95);
    border-bottom: 1px solid #d9dee8;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
  }

  .site-chrome__inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.9rem 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .site-brand {
    color: #0f172a !important;
    text-decoration: none !important;
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    white-space: nowrap;
  }

  .site-nav {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0.6rem;
  }

  .site-nav a {
    color: #334155 !important;
    text-decoration: none !important;
    padding: 0.5rem 0.8rem;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.94rem;
    transition: background-color 0.2s ease, color 0.2s ease;
  }

  .site-nav a:hover,
  .site-nav a:focus {
    background: #e8eefc;
    color: #1d4ed8 !important;
    outline: none;
  }

  .site-footer {
    margin-top: 4rem;
    background: #0f172a;
    color: #dbe4f3;
  }

  .site-footer__inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2.5rem 1.25rem 1.5rem;
  }

  .site-footer__grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.5rem;
  }

  .site-footer h2,
  .site-footer h3 {
    color: #ffffff;
    margin: 0 0 0.85rem;
    font-size: 0.98rem;
    font-weight: 700;
  }

  .site-footer p {
    margin: 0;
    line-height: 1.65;
    color: #cbd5e1;
    font-size: 0.95rem;
  }

  .site-footer ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .site-footer li + li {
    margin-top: 0.45rem;
  }

  .site-footer a {
    color: #dbe4f3 !important;
    text-decoration: none !important;
  }

  .site-footer a:hover,
  .site-footer a:focus {
    color: #93c5fd !important;
    text-decoration: underline !important;
    outline: none;
  }

  .site-footer__meta {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(148, 163, 184, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    font-size: 0.9rem;
  }

  @media (max-width: 900px) {
    .site-chrome__inner {
      flex-direction: column;
      align-items: flex-start;
    }

    .site-nav {
      justify-content: flex-start;
    }

    .site-footer__grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 560px) {
    .site-footer__grid {
      grid-template-columns: 1fr;
    }

    .site-nav a {
      padding-inline: 0.7rem;
      font-size: 0.9rem;
    }
  }
</style>
`;

const HEADER_HTML = `
<header class="site-chrome" aria-label="サイトヘッダー">
  <div class="site-chrome__inner">
    <a class="site-brand" href="/">バーコード作成プロ</a>
    <nav class="site-nav" aria-label="主要ナビゲーション">
      <a href="/">ホーム</a>
      <a href="/barcode-generator.html">バーコード作成</a>
      <a href="/qr-code-generator.html">QRコード作成</a>
      <a href="/symbologies/ultimate-barcode-type-guide/">種類ガイド</a>
      <a href="/compliance/industry-barcode-standards-guide/">規格と運用</a>
      <a href="/developers/barcode-generation-api-sdk-guide/">開発者向け</a>
      <a href="/search.html">検索</a>
    </nav>
  </div>
</header>
`;

const FOOTER_HTML = `
<footer class="site-footer">
  <div class="site-footer__inner">
    <div class="site-footer__grid">
      <section>
        <h2>バーコード作成</h2>
        <p>日本語で使えるバーコード作成・比較・運用ガイドをまとめたサイトです。</p>
      </section>
      <section>
        <h3>主要ツール</h3>
        <ul>
          <li><a href="/barcode-generator.html">バーコード作成ツール</a></li>
          <li><a href="/qr-code-generator.html">QRコード作成ツール</a></li>
          <li><a href="/bulk-barcode-generator.html">一括バーコード作成</a></li>
          <li><a href="/barcode-generator-png.html">PNG出力</a></li>
          <li><a href="/barcode-generator-svg.html">SVG出力</a></li>
        </ul>
      </section>
      <section>
        <h3>ガイド</h3>
        <ul>
          <li><a href="/what-is-barcode.html">バーコードとは</a></li>
          <li><a href="/how-to-create-barcode.html">作成方法</a></li>
          <li><a href="/barcode-types.html">バーコードの種類</a></li>
          <li><a href="/barcode-format-guide.html">ファイル形式ガイド</a></li>
          <li><a href="/production/perfect-barcode-print-optimization-guide/">印字最適化ガイド</a></li>
        </ul>
      </section>
      <section>
        <h3>サイト情報</h3>
        <ul>
          <li><a href="/about-us.html">私たちについて</a></li>
          <li><a href="/contact-us.html">お問い合わせ</a></li>
          <li><a href="/privacy.html">プライバシーポリシー</a></li>
          <li><a href="/terms.html">利用規約</a></li>
          <li><a href="/sitemap.html">サイトマップ</a></li>
        </ul>
      </section>
    </div>
    <div class="site-footer__meta">
      <span>© 2026 バーコード作成プロ</span>
      <span><a href="/developers/">開発者向け</a> ・ <a href="/compliance/">コンプライアンス</a> ・ <a href="/future/">将来動向</a></span>
    </div>
  </div>
</footer>
`;

function listHtmlFiles(dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  let files = [];

  for (const entry of entries) {
    if (SKIP_DIRS.has(entry.name)) {
      continue;
    }

    const absolute = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(listHtmlFiles(absolute));
      continue;
    }

    if (entry.isFile() && entry.name.toLowerCase().endsWith(".html")) {
      files.push(absolute);
    }
  }

  return files;
}

function relPath(absolutePath) {
  return path.relative(ROOT, absolutePath).replace(/\\/g, "/");
}

function isRedirectPage(text) {
  const lowered = text.toLowerCase();
  return (
    lowered.includes('http-equiv="refresh"') ||
    lowered.includes("location.replace(") ||
    lowered.includes("window.location")
  );
}

function ensureQrPage() {
  const qrPath = path.join(ROOT, "qr-code-generator.html");
  const sourcePath = path.join(ROOT, "2d-barcode-generator.html");

  if (!fs.existsSync(sourcePath)) {
    throw new Error("2d-barcode-generator.html が見つかりません。");
  }

  let content = fs.readFileSync(sourcePath, "utf8");

  const replacements = [
    ["2次元 (QR等)バーコード作成ツール", "QRコード作成ツール"],
    ["【2026年最新・完全無料】2次元 (QR等)バーコード作成ツール", "【2026年最新・完全無料】QRコード作成ツール"],
    ["2d-barcode-generator.html", "qr-code-generator.html"],
    ["2次元 (QR等)バーコード作成ツールの作成", "QRコード作成ツールの作成"],
    ["2D Barcode Generator", "QRコード作成ツール"],
    ["2D 2D decision grid", "QRコードの判断基準"],
  ];

  for (const [from, to] of replacements) {
    content = content.split(from).join(to);
  }

  content = content.replace(
    '<option value="QR">QRコード</option>',
    '<option value="QR" selected>QRコード</option>'
  );

  content = content.replace(
    /placeholder="例: 4901234567894" value="4901234567894"/,
    'placeholder="例: https://example.jp/item/4901234567894" value="https://example.jp/item/4901234567894"'
  );

  content = content.replace(
    /placeholder="4901234567894&#10;4901234567895&#10;4901234567896"/,
    'placeholder="https://example.jp/item/4901234567894&#10;https://example.jp/item/4901234567895&#10;https://example.jp/item/4901234567896"'
  );

  fs.writeFileSync(qrPath, content, "utf8");
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function hasLatinText(value) {
  return /[A-Za-z]{2,}/.test(value);
}

function shouldSkipTranslation(value) {
  const text = value.trim();
  if (!text || !hasLatinText(text)) {
    return true;
  }

  if (/^(https?:|mailto:|tel:|#|\/)/i.test(text)) {
    return true;
  }

  if (/[{}<>]=|function\s*\(|=>|const\s|let\s|var\s|document\.|window\.|<\w+/.test(text)) {
    return true;
  }

  if (/^[A-Z0-9_\-./: ]+$/.test(text) && !/\s[a-z]/.test(text)) {
    return true;
  }

  if (text.length > 600) {
    return true;
  }

  return false;
}

function preserveWhitespace(original, translated) {
  const leading = original.match(/^\s*/)?.[0] ?? "";
  const trailing = original.match(/\s*$/)?.[0] ?? "";
  return `${leading}${translated}${trailing}`;
}

function extractParts(href) {
  const hashIndex = href.indexOf("#");
  const queryIndex = href.indexOf("?");

  let pathEnd = href.length;
  if (queryIndex !== -1) {
    pathEnd = Math.min(pathEnd, queryIndex);
  }
  if (hashIndex !== -1) {
    pathEnd = Math.min(pathEnd, hashIndex);
  }

  return {
    pathname: href.slice(0, pathEnd),
    search: queryIndex !== -1 ? href.slice(queryIndex, hashIndex !== -1 ? hashIndex : undefined) : "",
    hash: hashIndex !== -1 ? href.slice(hashIndex) : "",
  };
}

function normalizeTarget(relTarget) {
  let target = relTarget.replace(/\\/g, "/").replace(/^\/+/, "");
  if (!target || target === ".") {
    return "index.html";
  }
  if (target.endsWith("/")) {
    return `${target}index.html`;
  }
  if (!posix.extname(target)) {
    return `${target}/index.html`;
  }
  return posix.normalize(target);
}

function resolveTarget(sourceRel, rawPathname) {
  if (!rawPathname) {
    return "index.html";
  }

  const pathname = rawPathname.replace(/\\/g, "/");
  const directCandidates = [];

  if (pathname.startsWith("/")) {
    directCandidates.push(normalizeTarget(pathname.slice(1)));
  } else {
    const sourceDir = posix.dirname(sourceRel);
    directCandidates.push(normalizeTarget(posix.join(sourceDir, pathname)));
    directCandidates.push(normalizeTarget(pathname));
  }

  if (pathname === "qr-code-generator.html") {
    directCandidates.unshift("qr-code-generator.html");
  }

  const seen = new Set();
  for (const candidate of directCandidates) {
    if (seen.has(candidate)) {
      continue;
    }
    seen.add(candidate);

    if (fs.existsSync(path.join(ROOT, candidate))) {
      return candidate;
    }
  }

  return null;
}

function toCanonicalHref(targetRel, search, hash) {
  let pathname = "/";
  if (targetRel !== "index.html") {
    pathname = targetRel.endsWith("/index.html")
      ? `/${targetRel.slice(0, -"index.html".length)}`
      : `/${targetRel}`;
  }
  return `${pathname}${search}${hash}`;
}

function normalizeInternalLinks($, sourceRel) {
  $("a[href], link[href]").each((_, element) => {
    const currentHref = $(element).attr("href");
    if (!currentHref) {
      return;
    }

    if (
      currentHref.startsWith("http://") ||
      currentHref.startsWith("https://") ||
      currentHref.startsWith("mailto:") ||
      currentHref.startsWith("tel:") ||
      currentHref.startsWith("javascript:") ||
      currentHref.startsWith("data:")
    ) {
      return;
    }

    const parts = extractParts(currentHref);
    if (!parts.pathname || parts.pathname.startsWith("#")) {
      return;
    }

    const resolved = resolveTarget(sourceRel, parts.pathname);
    if (!resolved) {
      return;
    }

    $(element).attr("href", toCanonicalHref(resolved, parts.search, parts.hash));
  });
}

function ensureLangAndChrome($, sourceRel, originalText) {
  const html = $("html").first();
  if (html.length) {
    html.attr("lang", "ja");
  }

  if (isRedirectPage(originalText) || SKIP_FILES.has(sourceRel)) {
    return;
  }

  const head = $("head").first();
  if (head.length && !$('style[data-site-chrome]').length) {
    head.append(`\n${CHROME_STYLE}\n`);
  }

  const body = $("body").first();
  if (!body.length) {
    return;
  }

  const bodyClass = body.attr("class");
  if (!bodyClass || !bodyClass.includes("jp-site-fixed")) {
    body.attr("class", bodyClass ? `${bodyClass} jp-site-fixed` : "jp-site-fixed");
  }

  if (!$("header.site-chrome").length) {
    body.prepend(`\n${HEADER_HTML}\n`);
  }

  if (!$("footer.site-footer").length) {
    body.append(`\n${FOOTER_HTML}\n`);
  }
}

function collectTranslatableStrings($, sourceRel, originalText, bag) {
  if (SKIP_FILES.has(sourceRel) || isRedirectPage(originalText)) {
    return;
  }

  $("title").each((_, element) => {
    const text = $(element).text();
    if (!shouldSkipTranslation(text)) {
      bag.add(text);
    }
  });

  $('meta[name="description"], meta[property="og:title"], meta[property="og:description"], meta[name="twitter:title"], meta[name="twitter:description"]').each((_, element) => {
    const text = $(element).attr("content");
    if (text && !shouldSkipTranslation(text)) {
      bag.add(text);
    }
  });

  $("[placeholder],[title],[aria-label],[alt]").each((_, element) => {
    for (const attr of ["placeholder", "title", "aria-label", "alt"]) {
      const text = $(element).attr(attr);
      if (text && !shouldSkipTranslation(text)) {
        bag.add(text);
      }
    }
  });

  $("body *")
    .contents()
    .each((_, node) => {
      if (node.type !== "text") {
        return;
      }

      const parentName = node.parent?.name?.toLowerCase?.() ?? "";
      if (SKIP_TEXT_PARENTS.has(parentName)) {
        return;
      }

      const value = node.data;
      if (!shouldSkipTranslation(value)) {
        bag.add(value);
      }
    });
}

async function fetchBatchTranslations(texts) {
  const separator = "\n[[[BG_SPLIT]]]\n";
  const payload = texts.join(separator);
  const encoded = encodeURIComponent(payload);
  const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ja&dt=t&q=${encoded}`;
  const response = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0",
    },
  });

  if (!response.ok) {
    throw new Error(`Translate API error: ${response.status}`);
  }

  const data = await response.json();
  if (!Array.isArray(data) || !Array.isArray(data[0])) {
    return texts;
  }

  const translated = data[0]
    .map((part) => (Array.isArray(part) ? part[0] : ""))
    .join("")
    .trim();

  const parts = (translated || payload).split(separator);
  if (parts.length !== texts.length) {
    return texts;
  }

  return parts;
}

async function buildTranslationMap(strings) {
  const map = new Map();
  const unique = Array.from(strings);
  const pending = [];

  for (const text of unique) {
    const trimmed = text.trim();
    if (EXACT_TRANSLATIONS.has(trimmed)) {
      map.set(text, preserveWhitespace(text, EXACT_TRANSLATIONS.get(trimmed)));
    } else {
      pending.push({ original: text, trimmed });
    }
  }

  const batches = [];
  let currentBatch = [];
  let currentLength = 0;

  for (const item of pending) {
    const projectedLength = currentLength + item.trimmed.length + 32;
    if (currentBatch.length && projectedLength > 2400) {
      batches.push(currentBatch);
      currentBatch = [];
      currentLength = 0;
    }
    currentBatch.push(item);
    currentLength += item.trimmed.length + 32;
  }

  if (currentBatch.length) {
    batches.push(currentBatch);
  }

  console.log(`Translating ${pending.length} strings in ${batches.length} batches.`);

  for (const batch of batches) {
    try {
      const translated = await fetchBatchTranslations(batch.map((item) => item.trimmed));
      batch.forEach((item, index) => {
        map.set(item.original, preserveWhitespace(item.original, translated[index] || item.trimmed));
      });
    } catch (error) {
      console.error(`TRANSLATE_BATCH_FAILED :: ${error.message}`);
      batch.forEach((item) => {
        map.set(item.original, item.original);
      });
    }
  }

  return map;
}

function applyTranslations($, sourceRel, originalText, translationMap) {
  if (SKIP_FILES.has(sourceRel) || isRedirectPage(originalText)) {
    return;
  }

  $("title").each((_, element) => {
    const original = $(element).text();
    if (translationMap.has(original)) {
      $(element).text(translationMap.get(original));
    }
  });

  $('meta[name="description"], meta[property="og:title"], meta[property="og:description"], meta[name="twitter:title"], meta[name="twitter:description"]').each((_, element) => {
    const original = $(element).attr("content");
    if (original && translationMap.has(original)) {
      $(element).attr("content", translationMap.get(original));
    }
  });

  $("[placeholder],[title],[aria-label],[alt]").each((_, element) => {
    for (const attr of ["placeholder", "title", "aria-label", "alt"]) {
      const original = $(element).attr(attr);
      if (original && translationMap.has(original)) {
        $(element).attr(attr, translationMap.get(original));
      }
    }
  });

  $("body *")
    .contents()
    .each((_, node) => {
      if (node.type !== "text") {
        return;
      }

      const parentName = node.parent?.name?.toLowerCase?.() ?? "";
      if (SKIP_TEXT_PARENTS.has(parentName)) {
        return;
      }

      const original = node.data;
      if (translationMap.has(original)) {
        node.data = translationMap.get(original);
      }
    });
}

function cleanupHtmlString(html) {
  let result = html;
  for (const [pattern, replacement] of CLEANUP_REPLACEMENTS) {
    result = result.replace(pattern, replacement);
  }
  result = result.replace(/（\s*プライバシーポリシー\s*）/g, "");
  result = result.replace(/（\s*利用規約\s*）/g, "");
  result = result.replace(/\(\s*プライバシーポリシー\s*\)/g, "");
  result = result.replace(/\(\s*利用規約\s*\)/g, "");
  result = result.replace(/>\s*QR Code\s*</g, ">QRコード<");
  result = result.replace(/>\s*Barcode Generators\s*</g, ">バーコード作成プロ<");
  return result;
}

async function main() {
  ensureQrPage();

  const htmlFiles = listHtmlFiles(ROOT)
    .filter((absolutePath) => !SKIP_FILES.has(relPath(absolutePath)))
    .sort();

  const pages = htmlFiles.map((absolutePath) => {
    const sourceRel = relPath(absolutePath);
    const originalText = fs.readFileSync(absolutePath, "utf8");
    const $ = cheerio.load(originalText, {
      decodeEntities: false,
      scriptingEnabled: false,
    });

    normalizeInternalLinks($, sourceRel);
    ensureLangAndChrome($, sourceRel, originalText);

    return { absolutePath, sourceRel, originalText, $ };
  });

  const strings = new Set();
  for (const page of pages) {
    collectTranslatableStrings(page.$, page.sourceRel, page.originalText, strings);
  }

  console.log(`Collected ${strings.size} unique translatable strings.`);
  const translationMap = await buildTranslationMap(strings);

  let changedCount = 0;

  for (const page of pages) {
    applyTranslations(page.$, page.sourceRel, page.originalText, translationMap);
    const hadDoctype = /^\s*<!doctype/i.test(page.originalText);
    let finalHtml = cleanupHtmlString(page.$.html());
    if (hadDoctype && !/^\s*<!doctype/i.test(finalHtml)) {
      finalHtml = `<!DOCTYPE html>\n${finalHtml}`;
    }
    if (finalHtml !== page.originalText) {
      fs.writeFileSync(page.absolutePath, finalHtml, "utf8");
      changedCount += 1;
      console.log(`UPDATED ${page.sourceRel}`);
    }
  }

  console.log(`Updated ${changedCount} HTML files.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
