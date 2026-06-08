/**
 * rebuild_all_pages.js
 * Complete rebuild of all barcode generator pages.
 * 
 * Fixes:
 *  - Removes inline <style> blocks (replaced by style.css)
 *  - Removes injected site-chrome header/footer
 *  - Replaces ALL Japanese UI text with English
 *  - Fixes broken tabs/tool HTML structure
 *  - Tool is first after page title
 *  - Consistent English header, footer, and buttons
 *  - Links external style.css properly
 * 
 * Run: node rebuild_all_pages.js
 */

const fs   = require('fs');
const path = require('path');
const DIR  = __dirname;

// Pages to skip
const SKIP = new Set([
  'index.html',
  'sitemap.html','privacy.html','terms.html','contact-us.html',
  'about-us.html','team.html','editorial-guidelines.html',
  'barcode-basics.html','barcode-format-guide.html','barcode-generator-guide.html',
  'barcode-printing-guide.html','barcode-size-guide.html','barcode-standards-guide.html',
  'barcode-tech-trends-guide.html','barcode-types-guide.html','barcode-types.html',
  'barcode-use-cases.html','barcode-usecase-guide.html','bulk-custom-barcode-guide.html',
  'code128-vs-code39.html','ean-vs-upc.html','what-is-barcode.html',
  'how-to-create-barcode.html','search.html','google8a2939e9b7d79b04.html',
]);

// Per-page config: default barcode type, sample value, and English page title
const PAGE_CONFIG = {
  'barcode-generator.html':           { type:'EAN13',   sample:'4901234567894', title:'Barcode Generator',                    sub:'Free online barcode generator. Create EAN-13, Code 128, QR and more. Export PNG, SVG, or bulk PDF.' },
  'online-barcode-generator.html':    { type:'EAN13',   sample:'4901234567894', title:'Online Barcode Generator',             sub:'Generate barcodes online — no signup, no install. PNG and SVG download included.' },
  'free-barcode-generator.html':      { type:'EAN13',   sample:'4901234567894', title:'Free Barcode Generator',               sub:'100% free barcode generator for commercial and personal use.' },
  'barcode-maker.html':               { type:'EAN13',   sample:'4901234567894', title:'Barcode Maker',                        sub:'Make professional barcodes in seconds. Download as PNG, SVG, or PDF.' },
  'barcode-creator.html':             { type:'EAN13',   sample:'4901234567894', title:'Barcode Creator',                      sub:'Create retail, logistics and custom barcodes instantly.' },
  'barcode-label-generator.html':     { type:'CODE128', sample:'ABC-12345',     title:'Barcode Label Generator',              sub:'Generate print-ready barcode labels. Supports all major formats.' },
  'barcode-image-generator.html':     { type:'EAN13',   sample:'4901234567894', title:'Barcode Image Generator',              sub:'Generate high-resolution barcode images — PNG and SVG output.' },
  'ean-13-barcode-generator.html':    { type:'EAN13',   sample:'4901234567894', title:'EAN-13 Barcode Generator',             sub:'Generate EAN-13 / JAN barcodes for international retail. PNG, SVG export.' },
  'ean-8-barcode-generator.html':     { type:'EAN8',    sample:'12345670',      title:'EAN-8 Barcode Generator',              sub:'Generate compact EAN-8 barcodes for small product packaging.' },
  'upc-a-barcode-generator.html':     { type:'UPC',     sample:'012345678905',  title:'UPC-A Barcode Generator',              sub:'Create UPC-A barcodes for North American retail and POS systems.' },
  'upc-e-barcode-generator.html':     { type:'UPCE',    sample:'01234565',      title:'UPC-E Barcode Generator',              sub:'Generate compressed UPC-E barcodes for small packaging.' },
  'itf-14-barcode-generator.html':    { type:'ITF14',   sample:'00012345678905',title:'ITF-14 Barcode Generator',             sub:'Create ITF-14 barcodes for case/pallet logistics and GS1 shipping.' },
  'code-128-barcode-generator.html':  { type:'CODE128', sample:'ABC-12345',     title:'Code 128 Barcode Generator',           sub:'Generate Code 128 barcodes — alphanumeric, high-density, shipping labels.' },
  'code-39-barcode-generator.html':   { type:'CODE39',  sample:'HELLO-WORLD',   title:'Code 39 Barcode Generator',            sub:'Generate Code 39 barcodes for industrial and asset tracking.' },
  'codabar-barcode-generator.html':   { type:'codabar', sample:'A12345B',       title:'Codabar Barcode Generator',            sub:'Create Codabar barcodes for libraries, healthcare, and blood banks.' },
  'gs1-128-barcode-generator.html':   { type:'CODE128', sample:'00012345678905',title:'GS1-128 Barcode Generator',            sub:'Generate GS1-128 barcodes for supply chain and logistics compliance.' },
  'isbn-barcode-generator.html':      { type:'EAN13',   sample:'9781234567897', title:'ISBN Barcode Generator',               sub:'Create ISBN barcodes for books and publications. EAN-13 compatible.' },
  'issn-barcode-generator.html':      { type:'EAN13',   sample:'9770000000000', title:'ISSN Barcode Generator',               sub:'Generate ISSN barcodes for magazines and periodicals.' },
  'pdf417-barcode-generator.html':    { type:'CODE128', sample:'PDF-12345',     title:'PDF417 Barcode Generator',             sub:'Create PDF417 2D barcodes for IDs, transportation, and documents.' },
  'data-matrix-barcode-generator.html':{ type:'CODE128',sample:'DM-12345',      title:'Data Matrix Barcode Generator',        sub:'Generate Data Matrix barcodes for small items and electronics.' },
  'aztec-barcode-generator.html':     { type:'CODE128', sample:'AZ-12345',      title:'Aztec Code Barcode Generator',         sub:'Create Aztec barcodes used in transit tickets and mobile apps.' },
  '1d-barcode-generator.html':        { type:'CODE128', sample:'ABC-12345',     title:'1D Barcode Generator',                 sub:'Generate 1D linear barcodes: Code 128, EAN, UPC, Code 39 and more.' },
  '2d-barcode-generator.html':        { type:'QR',      sample:'https://barcode-generators.com', title:'2D Barcode Generator', sub:'Create 2D barcodes including QR codes, Data Matrix, and PDF417.' },
  'product-barcode-generator.html':   { type:'EAN13',   sample:'4901234567894', title:'Product Barcode Generator',            sub:'Generate product barcodes for retail, POS, and inventory systems.' },
  'inventory-barcode-generator.html': { type:'CODE128', sample:'INV-12345',     title:'Inventory Barcode Generator',          sub:'Create barcodes for inventory management and stock tracking.' },
  'sku-barcode-generator.html':       { type:'CODE128', sample:'SKU-12345',     title:'SKU Barcode Generator',                sub:'Generate SKU barcodes for retail product management.' },
  'warehouse-barcode-generator.html': { type:'CODE128', sample:'WH-BIN-001',    title:'Warehouse Barcode Generator',          sub:'Create location and bin barcodes for warehouse management systems.' },
  'shipping-barcode-generator.html':  { type:'CODE128', sample:'SHIP-12345',    title:'Shipping Barcode Generator',           sub:'Generate shipping and logistics barcodes for parcels and freight.' },
  'package-barcode-generator.html':   { type:'ITF14',   sample:'00012345678905',title:'Package Barcode Generator',            sub:'Create package-level barcodes for cartons and cases.' },
  'asset-barcode-generator.html':     { type:'CODE128', sample:'ASSET-0001',    title:'Asset Barcode Generator',              sub:'Generate asset tracking barcodes for equipment and IT assets.' },
  'book-barcode-generator.html':      { type:'EAN13',   sample:'9781234567897', title:'Book Barcode Generator',               sub:'Create ISBN / EAN-13 barcodes for book publishing and retail.' },
  'library-barcode-generator.html':   { type:'codabar', sample:'A12345B',       title:'Library Barcode Generator',            sub:'Generate library barcodes for books, cards, and media items.' },
  'ticket-barcode-generator.html':    { type:'CODE128', sample:'TKT-98765',     title:'Ticket Barcode Generator',             sub:'Create event and transit ticket barcodes for scanning at entry.' },
  'event-barcode-generator.html':     { type:'CODE128', sample:'EVT-2026-001',  title:'Event Barcode Generator',              sub:'Generate barcodes for event entry, registration, and passes.' },
  'coupon-barcode-generator.html':    { type:'EAN13',   sample:'5012345678900', title:'Coupon Barcode Generator',             sub:'Create coupon barcodes compatible with retail POS systems.' },
  'id-barcode-generator.html':        { type:'CODE128', sample:'ID-EMP-1234',   title:'ID Card Barcode Generator',            sub:'Generate barcodes for employee ID cards and access control.' },
  'serial-number-barcode-generator.html':{ type:'CODE128', sample:'SN-2026-001', title:'Serial Number Barcode Generator',     sub:'Create serial number barcodes for products and assets.' },
  'barcode-generator-png.html':       { type:'EAN13',   sample:'4901234567894', title:'Barcode Generator — PNG Output',       sub:'Generate barcodes and download as high-resolution PNG images.' },
  'barcode-generator-svg.html':       { type:'EAN13',   sample:'4901234567894', title:'Barcode Generator — SVG / Vector',     sub:'Generate vector SVG barcodes for print and design workflows.' },
  'barcode-generator-jpg.html':       { type:'EAN13',   sample:'4901234567894', title:'Barcode Generator — JPG Output',       sub:'Generate barcodes and save as JPG image files.' },
  'barcode-generator-pdf.html':       { type:'EAN13',   sample:'4901234567894', title:'Barcode Generator — PDF Output',       sub:'Generate and print barcodes as PDF for labels and documents.' },
  'barcode-generator-vector.html':    { type:'EAN13',   sample:'4901234567894', title:'Vector Barcode Generator',             sub:'Create lossless vector barcodes (SVG) suitable for any print size.' },
  'high-resolution-barcode-generator.html':{ type:'EAN13', sample:'4901234567894', title:'High Resolution Barcode Generator', sub:'Generate high-DPI barcodes for professional print production.' },
  'printable-barcode-generator.html': { type:'EAN13',   sample:'4901234567894', title:'Printable Barcode Generator',          sub:'Create print-ready barcodes optimized for label and sheet printing.' },
  'bulk-barcode-generator.html':      { type:'EAN13',   sample:'4901234567894', title:'Bulk Barcode Generator',               sub:'Generate hundreds of barcodes at once. Paste a list, export as PDF.' },
  'multiple-barcode-generator.html':  { type:'EAN13',   sample:'4901234567894', title:'Multiple Barcode Generator',           sub:'Create multiple barcodes simultaneously from a list of values.' },
  'custom-barcode-generator.html':    { type:'CODE128', sample:'CUSTOM-001',    title:'Custom Barcode Generator',             sub:'Generate custom barcodes with your own data, colors, and format.' },
  'barcode-generator-with-text.html': { type:'CODE128', sample:'TEXT-001',      title:'Barcode Generator with Text',          sub:'Create barcodes with custom text labels displayed below the symbol.' },
  'barcode-generator-with-number.html':{ type:'EAN13',  sample:'4901234567894', title:'Barcode Generator with Number',        sub:'Generate barcodes with numeric values for retail and logistics.' },
  'barcode-generator-with-logo.html': { type:'QR',      sample:'https://barcode-generators.com', title:'Barcode Generator with Logo', sub:'Embed a logo in your QR code for branded barcode output.' },
  'scannable-barcode-generator.html': { type:'EAN13',   sample:'4901234567894', title:'Scannable Barcode Generator',          sub:'Generate barcodes verified for scanner compatibility and readability.' },
  'barcode-generator-for-excel.html': { type:'CODE128', sample:'EXCEL-001',     title:'Barcode Generator for Excel',          sub:'Create barcodes to use in Excel spreadsheets and reports.' },
  'barcode-generator-for-word.html':  { type:'CODE128', sample:'WORD-001',      title:'Barcode Generator for Word',           sub:'Generate barcodes for use in Microsoft Word documents.' },
  'barcode-generator-for-shopify.html':{ type:'EAN13',  sample:'4901234567894', title:'Barcode Generator for Shopify',        sub:'Create Shopify-compatible product barcodes for your store.' },
  'barcode-generator-for-woocommerce.html':{ type:'EAN13', sample:'4901234567894', title:'Barcode Generator for WooCommerce', sub:'Generate WooCommerce product barcodes for inventory management.' },
  'barcode-generator-for-amazon.html':{ type:'EAN13',   sample:'4901234567894', title:'Barcode Generator for Amazon',         sub:'Create Amazon-compatible GTINs and barcodes for product listings.' },
  'barcode-generator-for-pos.html':   { type:'EAN13',   sample:'4901234567894', title:'Barcode Generator for POS',            sub:'Generate POS-compatible barcodes for retail checkout systems.' },
};

const DEFAULT_CFG = { type:'EAN13', sample:'4901234567894', title:'Barcode Generator', sub:'Free online barcode generator. PNG, SVG, and bulk PDF output.' };

// ── Build a clean HTML page ──────────────────────────────────
function buildPage(filename, cfg, originalContentSection) {
  const isBulk = filename.includes('bulk') || filename.includes('multiple');

  const options = [
    ['EAN13','JAN / EAN-13'], ['EAN8','EAN-8'], ['UPC','UPC-A'], ['UPCE','UPC-E'],
    ['ITF14','ITF-14'], ['CODE128','Code 128'], ['CODE39','Code 39'],
    ['codabar','Codabar'], ['QR','QR Code'],
  ].map(([v,l]) => `<option value="${v}"${v===cfg.type?' selected':''}>${l}</option>`).join('\n                            ');

  const canon = `https://barcode-generators.com/${filename}`;

  return `<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${cfg.title} — Free, No Signup | barcode-generators.com</title>
    <meta name="description" content="${cfg.sub}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="${canon}">
    <meta property="og:title" content="${cfg.title} — barcode-generators.com">
    <meta property="og:description" content="${cfg.sub}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="${canon}">
    <meta property="og:image" content="https://barcode-generators.com/og-image.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,600;9..40,700;9..40,800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.6/dist/JsBarcode.all.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <link rel="icon" href="favicon.ico">
    <link rel="stylesheet" href="style.css">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebApplication","name":"${cfg.title}","url":"${canon}","applicationCategory":"BusinessApplication","operatingSystem":"All","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}}</script>
</head>
<body>

    <header>
        <a href="index.html" class="logo">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 5v14"/><path d="M8 5v14"/><path d="M12 5v14"/><path d="M17 5v14"/><path d="M21 5v14"/></svg>
            Barcode Generators
        </a>
        <button class="toggle-btn" id="theme-toggle">🌙 Dark Mode</button>
    </header>

    <main>
        <div class="page-title">
            <h1>${cfg.title}</h1>
            <p>${cfg.sub}</p>
        </div>

        <section class="tool-container">
            <div class="tabs">
                <div class="tab${isBulk ? '' : ' active'}" data-mode="single" id="tab-single">Single Mode</div>
                <div class="tab${isBulk ? ' active' : ''}" data-mode="bulk" id="tab-bulk">Bulk / Print Mode</div>
            </div>

            <div class="grid-layout">
                <div class="input-panel">
                    <div class="input-group">
                        <label>Barcode Format</label>
                        <select id="barcode-type">
                            ${options}
                        </select>
                    </div>
                    <div class="input-group" id="container-single"${isBulk ? ' style="display:none;"' : ''}>
                        <label>Value / Data</label>
                        <input type="text" id="barcode-input" placeholder="e.g. ${cfg.sample}" value="${cfg.sample}">
                    </div>
                    <div class="input-group" id="container-bulk"${isBulk ? '' : ' style="display:none;"'}>
                        <label>Bulk Data (one value per line)</label>
                        <textarea id="barcode-textarea" placeholder="${cfg.sample}"></textarea>
                    </div>
                    <div class="advanced-options">
                        <div class="color-group">
                            <label>Bar Color</label>
                            <input type="color" id="color-bar" value="#000000">
                        </div>
                        <div class="color-group">
                            <label>Background</label>
                            <input type="color" id="color-bg" value="#ffffff">
                        </div>
                    </div>
                    <div id="error-msg" class="error-message"></div>
                    <div class="button-group">
                        <button class="btn btn-primary" id="btn-generate">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                            Generate Barcode
                        </button>
                        <button class="btn btn-secondary" id="btn-clear">Clear</button>
                    </div>
                    <div class="history-section">
                        <div class="history-title">
                            <span>Recent History</span>
                            <button class="toggle-btn" style="padding:4px 12px;font-size:13px;" onclick="clearHistory()">Clear</button>
                        </div>
                        <div class="history-list" id="history-list">
                            <p style="color:var(--text-muted);font-size:13px;padding:8px 0;">No history yet.</p>
                        </div>
                    </div>
                </div>

                <div class="preview-section">
                    <div id="preview-placeholder" class="preview-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 5v14"/><path d="M8 5v14"/><path d="M12 5v14"/><path d="M17 5v14"/><path d="M21 5v14"/></svg>
                        <p>Your barcode will appear here</p>
                    </div>
                    <div id="barcode-canvas-container">
                        <svg id="barcode-svg" style="max-width:100%;display:block;"></svg>
                        <div id="qrcode-container" style="border-radius:8px;overflow:hidden;"></div>
                    </div>
                    <div id="bulk-output"></div>
                    <div class="actions-group" id="actions-group">
                        <button class="btn btn-secondary" onclick="downloadImage('png')" id="btn-png"${isBulk ? ' style="display:none;"' : ''}>
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                            Save PNG
                        </button>
                        <button class="btn btn-secondary" onclick="downloadImage('svg')" id="btn-svg"${isBulk ? ' style="display:none;"' : ''}>
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                            Save SVG
                        </button>
                        <button class="btn btn-primary" onclick="printBulkPDF()" id="btn-print"${isBulk ? '' : ' style="display:none;"'}>
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                            Print / PDF
                        </button>
                    </div>
                </div>
            </div>
        </section>

${originalContentSection}

    </main>

    <footer class="modern-footer">
        <div class="footer-top">
            <div class="footer-brand">
                <a href="index.html" class="logo">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 5v14"/><path d="M8 5v14"/><path d="M12 5v14"/><path d="M17 5v14"/><path d="M21 5v14"/></svg>
                    Barcode Generators
                </a>
                <p>Free professional barcode generator. Vector output, bulk printing, zero data collection.</p>
            </div>
            <div class="footer-nav">
                <div class="link-col">
                    <h4>Core Tools</h4>
                    <div class="link-list">
                        <a href="barcode-generator.html">Barcode Generator</a>
                        <a href="online-barcode-generator.html">Online Generator</a>
                        <a href="free-barcode-generator.html">Free Generator</a>
                        <a href="bulk-barcode-generator.html">Bulk Generator</a>
                        <a href="custom-barcode-generator.html">Custom Generator</a>
                        <a href="barcode-label-generator.html">Label Generator</a>
                    </div>
                </div>
                <div class="link-col">
                    <h4>By Format</h4>
                    <div class="link-list">
                        <a href="ean-13-barcode-generator.html">EAN-13 / JAN</a>
                        <a href="ean-8-barcode-generator.html">EAN-8</a>
                        <a href="upc-a-barcode-generator.html">UPC-A</a>
                        <a href="upc-e-barcode-generator.html">UPC-E</a>
                        <a href="itf-14-barcode-generator.html">ITF-14</a>
                        <a href="code-128-barcode-generator.html">Code 128</a>
                        <a href="code-39-barcode-generator.html">Code 39</a>
                        <a href="gs1-128-barcode-generator.html">GS1-128</a>
                        <a href="pdf417-barcode-generator.html">PDF417</a>
                        <a href="data-matrix-barcode-generator.html">Data Matrix</a>
                        <a href="aztec-barcode-generator.html">Aztec</a>
                        <a href="codabar-barcode-generator.html">Codabar</a>
                        <a href="isbn-barcode-generator.html">ISBN</a>
                        <a href="issn-barcode-generator.html">ISSN</a>
                    </div>
                </div>
                <div class="link-col">
                    <h4>By Use Case</h4>
                    <div class="link-list">
                        <a href="product-barcode-generator.html">Product</a>
                        <a href="inventory-barcode-generator.html">Inventory</a>
                        <a href="shipping-barcode-generator.html">Shipping</a>
                        <a href="warehouse-barcode-generator.html">Warehouse</a>
                        <a href="asset-barcode-generator.html">Asset Tracking</a>
                        <a href="book-barcode-generator.html">Books</a>
                        <a href="library-barcode-generator.html">Library</a>
                        <a href="ticket-barcode-generator.html">Tickets</a>
                        <a href="event-barcode-generator.html">Events</a>
                        <a href="coupon-barcode-generator.html">Coupons</a>
                        <a href="serial-number-barcode-generator.html">Serial Numbers</a>
                        <a href="sku-barcode-generator.html">SKU</a>
                    </div>
                </div>
                <div class="link-col">
                    <h4>Output Format</h4>
                    <div class="link-list">
                        <a href="barcode-generator-png.html">PNG</a>
                        <a href="barcode-generator-svg.html">SVG / Vector</a>
                        <a href="barcode-generator-jpg.html">JPG</a>
                        <a href="barcode-generator-pdf.html">PDF</a>
                        <a href="high-resolution-barcode-generator.html">High Resolution</a>
                        <a href="printable-barcode-generator.html">Printable</a>
                    </div>
                </div>
                <div class="link-col">
                    <h4>Integrations</h4>
                    <div class="link-list">
                        <a href="barcode-generator-for-excel.html">Excel</a>
                        <a href="barcode-generator-for-word.html">Word</a>
                        <a href="barcode-generator-for-shopify.html">Shopify</a>
                        <a href="barcode-generator-for-woocommerce.html">WooCommerce</a>
                        <a href="barcode-generator-for-amazon.html">Amazon</a>
                        <a href="barcode-generator-for-pos.html">POS</a>
                    </div>
                </div>
                <div class="link-col">
                    <h4>Guides</h4>
                    <div class="link-list">
                        <a href="barcode-types.html">Barcode Types</a>
                        <a href="what-is-barcode.html">What is a Barcode?</a>
                        <a href="how-to-create-barcode.html">How to Create</a>
                        <a href="barcode-size-guide.html">Size Guide</a>
                        <a href="barcode-format-guide.html">Format Guide</a>
                        <a href="ean-vs-upc.html">EAN vs UPC</a>
                        <a href="code128-vs-code39.html">Code 128 vs 39</a>
                        <a href="barcode-use-cases.html">Use Cases</a>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer-company-info">
            <div>
                <strong>Barcode Generators LLC</strong><br>
                Professional barcode generation &amp; bulk printing platform.<br>
                <span style="display:inline-block;margin-top:5px;padding:2px 8px;background:var(--surface-2);border:1px solid var(--border);border-radius:4px;font-size:0.72rem;font-weight:700;">DMCA PROTECTED</span>
            </div>
            <div>Email: contact@barcode-generators.com</div>
            <div class="footer-socials">
                <a href="https://twitter.com/barcodegens">🐦 Twitter</a>
                <a href="https://facebook.com/barcodegens">📘 Facebook</a>
                <a href="https://linkedin.com/company/barcodegens">💼 LinkedIn</a>
                <a href="https://youtube.com/@barcodegens">▶️ YouTube</a>
            </div>
        </div>

        <div class="footer-eeat-links">
            <a href="about-us.html">About Us</a>
            <a href="team.html">Team</a>
            <a href="contact-us.html">Contact</a>
            <a href="editorial-guidelines.html">Editorial Guidelines</a>
            <a href="sitemap.html">Sitemap</a>
            <a href="rss.xml">RSS</a>
        </div>

        <div class="footer-bottom">
            <p>&copy; 2026 Barcode Generators LLC. All Rights Reserved.</p>
            <div class="footer-legal">
                <a href="privacy.html">Privacy Policy</a>
                <a href="terms.html">Terms of Use</a>
            </div>
        </div>
    </footer>

    <div id="toast" class="toast"></div>
    <button id="backToTop" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>

    <script>
        const barcodeType=document.getElementById('barcode-type'),barcodeInput=document.getElementById('barcode-input'),barcodeTextarea=document.getElementById('barcode-textarea'),colorBar=document.getElementById('color-bar'),colorBg=document.getElementById('color-bg'),btnGenerate=document.getElementById('btn-generate'),btnClear=document.getElementById('btn-clear'),errorMsg=document.getElementById('error-msg'),containerSingle=document.getElementById('container-single'),containerBulk=document.getElementById('container-bulk'),previewPlaceholder=document.getElementById('preview-placeholder'),canvasContainer=document.getElementById('barcode-canvas-container'),bulkOutput=document.getElementById('bulk-output'),barcodeSvg=document.getElementById('barcode-svg'),qrcodeContainer=document.getElementById('qrcode-container'),actionsGroup=document.getElementById('actions-group'),btnPng=document.getElementById('btn-png'),btnSvg=document.getElementById('btn-svg'),btnPrint=document.getElementById('btn-print'),themeToggle=document.getElementById('theme-toggle');
        let currentMode=document.querySelector('.tab.active')?.dataset.mode||'single';
        document.addEventListener('DOMContentLoaded',()=>{renderHistory();});
        document.querySelectorAll('.tab').forEach(tab=>{tab.addEventListener('click',e=>{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));e.target.classList.add('active');currentMode=e.target.getAttribute('data-mode');if(currentMode==='single'){containerSingle.style.display='block';containerBulk.style.display='none';if(btnPng)btnPng.style.display='inline-flex';if(btnSvg)btnSvg.style.display='inline-flex';if(btnPrint)btnPrint.style.display='none';}else{containerSingle.style.display='none';containerBulk.style.display='block';if(btnPng)btnPng.style.display='none';if(btnSvg)btnSvg.style.display='none';if(btnPrint)btnPrint.style.display='inline-flex';}resetView();});});
        [barcodeType,colorBar,colorBg].forEach(el=>{el.addEventListener('change',()=>{if(canvasContainer.style.display==='block'||bulkOutput.style.display==='grid')generateBarcode();});});
        btnGenerate.addEventListener('click',generateBarcode);
        btnClear.addEventListener('click',()=>{barcodeInput.value='';barcodeTextarea.value='';colorBar.value='#000000';colorBg.value='#ffffff';resetView();});
        if(themeToggle){themeToggle.addEventListener('click',()=>{const html=document.documentElement,dark=html.getAttribute('data-theme')==='dark';html.setAttribute('data-theme',dark?'light':'dark');themeToggle.textContent=dark?'🌙 Dark Mode':'☀️ Light Mode';});}
        function showToast(msg){const t=document.getElementById('toast');if(!t)return;t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3000);}
        function showError(msg){errorMsg.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'+msg;errorMsg.style.display='flex';resetView(true);}
        function resetView(k=false){if(!k)errorMsg.style.display='none';canvasContainer.style.display='none';bulkOutput.style.display='none';actionsGroup.style.display='none';previewPlaceholder.style.display='block';}
        function generateBarcode(){errorMsg.style.display='none';if(currentMode==='single')processSingle();else processBulk();}
        function processSingle(){const value=barcodeInput.value.trim(),type=barcodeType.value;if(!value){showError('Please enter a value.');return;}previewPlaceholder.style.display='none';bulkOutput.style.display='none';canvasContainer.style.display='block';actionsGroup.style.display='flex';barcodeSvg.style.display='none';qrcodeContainer.style.display='none';if(btnSvg)btnSvg.style.display=(type==='QR')?'none':'inline-flex';if(type==='QR'){qrcodeContainer.style.display='block';qrcodeContainer.innerHTML='';try{new QRCode(qrcodeContainer,{text:value,width:220,height:220,colorDark:colorBar.value,colorLight:colorBg.value,correctLevel:QRCode.CorrectLevel.H});saveToHistory(type,value);}catch(e){showError('Failed to generate QR code.');}}else{barcodeSvg.style.display='block';try{JsBarcode('#barcode-svg',value,{format:type,lineColor:colorBar.value,background:colorBg.value,width:2.2,height:110,displayValue:true,fontSize:18,margin:12});saveToHistory(type,value);}catch(e){showError('Invalid value for format: '+type);}}}
        function processBulk(){const lines=barcodeTextarea.value.split('\\n').map(l=>l.trim()).filter(Boolean),type=barcodeType.value;if(!lines.length){showError('Enter at least one value.');return;}if(lines.length>500){showError('Maximum 500 items per batch.');return;}previewPlaceholder.style.display='none';canvasContainer.style.display='none';bulkOutput.innerHTML='';bulkOutput.style.display='grid';actionsGroup.style.display='flex';lines.forEach(val=>{const wrap=document.createElement('div');wrap.className='bulk-item';if(type==='QR'){const qw=document.createElement('div');try{new QRCode(qw,{text:val,width:100,height:100,colorDark:colorBar.value,colorLight:colorBg.value});wrap.appendChild(qw);const lbl=document.createElement('div');lbl.textContent=val;lbl.style.cssText='margin-top:6px;font-size:11px;font-weight:600;word-break:break-all;';wrap.appendChild(lbl);}catch(e){};}else{const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');try{JsBarcode(svg,val,{format:type,lineColor:colorBar.value,background:colorBg.value,width:1.5,height:50,displayValue:true,fontSize:13,margin:5});wrap.appendChild(svg);}catch(e){wrap.innerHTML='<span style="color:var(--error);font-size:11px;font-weight:700;">Invalid: '+val+'</span>';}}bulkOutput.appendChild(wrap);});}
        function saveToHistory(type,value){let hist=JSON.parse(localStorage.getItem('barcodeHist')||'[]');hist=hist.filter(h=>h.value!==value);hist.unshift({type,value});localStorage.setItem('barcodeHist',JSON.stringify(hist.slice(0,6)));renderHistory();}
        function renderHistory(){const histList=document.getElementById('history-list');const hist=JSON.parse(localStorage.getItem('barcodeHist')||'[]');if(!hist.length){histList.innerHTML='<p style="color:var(--text-muted);font-size:13px;padding:8px 0;">No history yet.</p>';return;}histList.innerHTML='';hist.forEach(item=>{const div=document.createElement('div');div.className='history-item';div.innerHTML='<div class="history-desc"><span class="badge">'+item.type+'</span><strong style="font-family:DM Mono,monospace;font-size:14px;">'+item.value+'</strong></div>';div.title='Click to restore';div.addEventListener('click',()=>{document.getElementById('tab-single').click();barcodeInput.value=item.value;barcodeType.value=item.type;generateBarcode();});histList.appendChild(div);});}
        function clearHistory(){localStorage.removeItem('barcodeHist');renderHistory();showToast('History cleared.');}
        function downloadImage(format){const type=barcodeType.value,filename='barcode_'+type+'_'+Date.now()+'.'+format;if(type==='QR'){const canvas=qrcodeContainer.querySelector('canvas');if(!canvas)return;const a=document.createElement('a');a.download=filename;a.href=canvas.toDataURL('image/png');a.click();showToast('PNG saved!');}else{const svg=document.getElementById('barcode-svg');const s=new XMLSerializer();let src=s.serializeToString(svg);if(!src.match(/xmlns=/))src=src.replace('<svg','<svg xmlns="http://www.w3.org/2000/svg"');src='<?xml version="1.0" standalone="no"?>\\r\\n'+src;if(format==='svg'){const a=document.createElement('a');a.download=filename;a.href='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(src);a.click();showToast('SVG saved!');}else{const img=new Image();img.onload=function(){const c=document.createElement('canvas');c.width=img.width*2;c.height=img.height*2;const ctx=c.getContext('2d');ctx.fillStyle=colorBg.value;ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(img,0,0,c.width,c.height);const a=document.createElement('a');a.download=filename;a.href=c.toDataURL('image/png');a.click();showToast('PNG saved!');};img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(src)));}}}
        function printBulkPDF(){const win=window.open('','','width=900,height=800');win.document.write('<html><head><title>Barcode Print</title><style>body{font-family:sans-serif;padding:1rem}.bulk-item{display:inline-block;margin:6px;padding:8px;border:1px solid #ccc;text-align:center;}svg{max-width:150px;}</style></head><body>'+document.getElementById('bulk-output').innerHTML+'<script>setTimeout(()=>{window.print();window.close();},400);<\\/script></body></html>');win.document.close();}
    </script>
    <script>
        document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('.modern-footer .link-col h4').forEach(h=>{h.addEventListener('click',function(){if(window.innerWidth<=600)this.parentElement.classList.toggle('active');});});});
        window.addEventListener('scroll',function(){const btn=document.getElementById('backToTop');if(btn)btn.style.display=window.scrollY>300?'block':'none';});
    </script>

</body>
</html>`;
}

// ── Extract English content section if present ───────────────
function extractContentSection(html) {
  // Look for the English content section (has id="heading-1" and class="content-section")
  const match = html.match(/<section class="content-section[^"]*"[^>]*>([\s\S]*?)<\/section>\s*(?=\s*<\/main>)/);
  if (!match) return '';
  const content = match[0];
  // Only keep if it's mostly English (not Japanese)
  const japaneseChars = (content.match(/[\u3000-\u9fff]/g) || []).length;
  const totalChars = content.length;
  if (japaneseChars / totalChars > 0.05) return ''; // skip if >5% Japanese
  return '\n        ' + content;
}

// ── Process all files ────────────────────────────────────────
const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html') && !SKIP.has(f));
let count = 0;

for (const file of files) {
  const fullPath = path.join(DIR, file);
  let html;
  try { html = fs.readFileSync(fullPath, 'utf8'); } catch(e) { continue; }
  
  const cfg = PAGE_CONFIG[file] || DEFAULT_CFG;
  const contentSection = extractContentSection(html);
  const newHtml = buildPage(file, cfg, contentSection);
  
  fs.writeFileSync(fullPath, newHtml, 'utf8');
  count++;
  process.stdout.write(`✓ ${file}\n`);
}

console.log(`\n✅ Rebuilt ${count} pages cleanly.`);
console.log('All pages now:');
console.log('  - Use external style.css (no inline styles)');
console.log('  - Are fully in English');
console.log('  - Have tool at the top (above content)');
console.log('  - Have consistent header & footer');
