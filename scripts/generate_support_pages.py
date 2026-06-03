from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

BASE_STYLE = """
  <style>
    body{font-family:Arial,Helvetica,sans-serif;max-width:980px;margin:24px auto;padding:0 18px;color:#1f2937;line-height:1.68}
    h1,h2,h3{color:#0f3d6e}
    .eyebrow{font-size:.9rem;font-weight:700;color:#0f3d6e;text-transform:uppercase;letter-spacing:.04em}
    .crumbs,.related{background:#f7fafc;border:1px solid #dbe5f0;border-radius:12px;padding:14px 16px;margin:16px 0}
    .tool{background:#eef6ff;border:1px solid #cfe0f6;border-radius:12px;padding:16px;margin:18px 0}
    table{width:100%;border-collapse:collapse;margin:14px 0}
    th,td{border:1px solid #dbe5f0;padding:8px;text-align:left;vertical-align:top}
    th{background:#f2f7fc}
    pre{background:#0f172a;color:#eef2ff;padding:14px;border-radius:12px;overflow:auto}
    code{font-family:Consolas,monospace}
    svg{max-width:100%;height:auto;display:block;margin:12px 0}
    a{color:#0b4a7a;text-decoration:none}
    a:hover{text-decoration:underline}
  </style>
""".strip()


def article_page(title, desc, canonical, h1, parent_url, parent_text, body, related=None, schema_type="Article", faq=None):
    related_html = ""
    if related:
        related_items = " | ".join(f'<a href="{href}">{label}</a>' for label, href in related)
        related_html = f'<div class="related"><strong>Related:</strong> {related_items}</div>'

    faq_html = ""
    faq_schema = ""
    if faq:
        faq_items = []
        faq_json = []
        for question, answer in faq:
            faq_items.append(f"<h3>{question}</h3><p>{answer}</p>")
            faq_json.append(
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
            )
        faq_html = '<section id="faq"><h2>FAQ</h2>' + "".join(faq_items) + "</section>"
        faq_schema = (
            '\n  <script type="application/ld+json">\n'
            + json.dumps(
                {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": faq_json,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n  </script>"
        )

    article_schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "headline": h1,
        "description": desc,
        "author": {"@type": "Organization", "name": "Barcode Generators"},
        "publisher": {"@type": "Organization", "name": "Barcode Generators"},
        "dateModified": "2026-05-31",
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="canonical" href="{canonical}" />
{BASE_STYLE}
</head>
<body>
  <article>
    <p class="eyebrow">Supporting Guide</p>
    <div class="crumbs"><a href="{parent_url}">{parent_text}</a></div>
    <h1>{h1}</h1>
{body}
{faq_html}
{related_html}
  </article>
  <script type="application/ld+json">
{json.dumps(article_schema, ensure_ascii=False, indent=2)}
  </script>{faq_schema}
</body>
</html>
"""


def code_sample(code):
    return f"<pre><code>{code}</code></pre>"


def write_page(rel_path, html):
    (ROOT / rel_path).write_text(html, encoding="utf-8")


sym_pages = {
    "symbologies/code-128/index.html": {
        "title": "Code 128: Subsets A, B, and C with Modulo-103 Validation",
        "desc": "Deep dive into Code 128 subsets, density optimization, and Modulo-103 checksum behavior for enterprise labels.",
        "h1": "Code 128: Subsets A, B, and C with Modulo-103 Validation",
        "body": """
    <p>Code 128 is the workhorse linear symbology for logistics because it packs a lot of information into a relatively narrow footprint while supporting a broad character set. The crucial implementation detail is that Code 128 is really three encoding modes living inside one standard: Subset A, Subset B, and Subset C. A generator that treats it as one undifferentiated alphabet usually leaves density on the table.</p>
    <p>Subset A is optimized for uppercase characters and control codes, Subset B covers the printable ASCII range most business systems need, and Subset C compresses numeric data by encoding two digits per symbol. That Subset C behavior is why long numeric strings such as SSCC fragments, dates, and shipment IDs become dramatically shorter when the encoder switches modes intelligently.</p>
    <table>
      <tr><th>Subset</th><th>Best for</th><th>Notes</th></tr>
      <tr><td>A</td><td>Uppercase + control characters</td><td>Useful when non-printable controls or scanner commands are involved.</td></tr>
      <tr><td>B</td><td>Mixed business text</td><td>Common default for names, SKUs, and human-oriented payloads.</td></tr>
      <tr><td>C</td><td>Dense numeric strings</td><td>Encodes two digits per symbol for maximum compression.</td></tr>
    </table>
    <h2>Checksum behavior</h2>
    <p>Every valid Code 128 symbol ends with a Modulo-103 check digit. The encoder starts with the numeric value of the selected start code, multiplies each following symbol by its position weight, sums the result, and takes the remainder when divided by 103. If your page or API claims to emit Code 128 without recalculating that check digit after subset switches, it is not a reliable encoder.</p>
    <h2>Implementation guidance</h2>
    <ul>
      <li>Prefer vector output so quiet zones and module widths stay exact during print scaling.</li>
      <li>Reserve at least 10 × X quiet zones on both sides.</li>
      <li>Switch to Subset C whenever long even-length numeric runs appear.</li>
      <li>Validate scanner behavior after any logo, label, or BWR change.</li>
    </ul>
    <div class="tool"><strong>Tool handoff:</strong> Open the <a href="/code-128-barcode-generator.html">live Code 128 generator</a> to test payload length, human-readable text, and SVG export settings.</div>
""",
        "faq": [
            (
                "Why is Code 128 shorter than Code 39 for the same payload?",
                "Because Code 128 has a denser encoding model and can use Subset C to compress numeric data into paired symbols.",
            ),
            (
                "When should I force Subset B instead of auto mode?",
                "Force Subset B when you know the payload is mixed printable text and you want predictable symbol structure for debugging or validation.",
            ),
        ],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("Code 128 Generator", "/code-128-barcode-generator.html"),
        ],
    },
    "symbologies/upc-a/index.html": {
        "title": "UPC-A: 12 Numeric Digits, Modulo-10 Check Digit, and POS Rules",
        "desc": "UPC-A technical guide covering its exact 12-digit structure, numeric-only constraints, and Modulo-10 check digit logic.",
        "h1": "UPC-A: 12 Numeric Digits, Modulo-10 Check Digit, and POS Rules",
        "body": """
    <p>UPC-A remains the foundational North American retail barcode because checkout lanes are tuned for its strict data model. UPC-A accepts exactly 12 digits, is numeric-only, and uses a Modulo-10 check digit. Those three facts are non-negotiable. If a generator lets you pass letters or the wrong digit count while still presenting the output as UPC-A, the result is not standards-compliant.</p>
    <p>The 12 digits are typically discussed as number system, manufacturer code, product code, and check digit. Retail systems use those digits to look up pricing and inventory, not to carry free-form text. That is why UPC-A remains extremely interoperable but intentionally narrow in scope.</p>
    <table>
      <tr><th>Attribute</th><th>UPC-A rule</th></tr>
      <tr><td>Character set</td><td>Numeric only</td></tr>
      <tr><td>Length</td><td>Exactly 12 digits</td></tr>
      <tr><td>Integrity check</td><td>Modulo-10 weighted checksum</td></tr>
      <tr><td>Primary use</td><td>Retail point of sale in North America</td></tr>
    </table>
    <h2>Check digit reminder</h2>
    <p>The Modulo-10 calculation multiplies alternating digit groups differently and computes the final digit needed to reach a multiple of ten. This protects against common entry or print errors. It is also the easiest sanity check to run before a barcode ever reaches packaging artwork.</p>
    <h2>Operational rules</h2>
    <ul>
      <li>Do not trim leading zeroes unless you fully understand the numbering-system implications.</li>
      <li>Protect quiet zones so the scanner can detect the symbol boundary before the guard bars.</li>
      <li>Use vector exports for packaging and shelf-ready artwork.</li>
    </ul>
    <div class="tool"><strong>Tool handoff:</strong> Validate a real 12-digit payload in the <a href="/upc-a-barcode-generator.html">UPC-A generator</a> and compare it with the retail rules in the parent guide.</div>
""",
        "faq": [
            ("Can UPC-A contain letters?", "No. UPC-A is numeric-only by design and retail scanners expect exactly 12 digits."),
            ("Is the check digit optional?", "No. UPC-A symbols are validated with a Modulo-10 check digit and production assets should include the full 12-digit value."),
        ],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("UPC-A Generator", "/upc-a-barcode-generator.html"),
        ],
    },
    "symbologies/ean-13/index.html": {
        "title": "EAN-13: International Retail Numbering and Parity Structure",
        "desc": "EAN-13 guide covering the 13-digit retail structure, parity behavior, and practical print rules.",
        "h1": "EAN-13: International Retail Numbering and Parity Structure",
        "body": """
    <p>EAN-13 extends the retail numbering model used by UPC-A into the broader international ecosystem. It encodes 13 numeric digits and uses a weighted Modulo-10 check digit, but the left-side parity structure also carries information that helps the scanner interpret the leading digit correctly.</p>
    <p>For packaging teams, EAN-13 is often less about theory and more about disciplined execution: correct digit count, correct checksum, predictable magnification, and quiet zones that survive prepress scaling. It is highly interoperable, but only when the numeric structure and print geometry are treated as fixed rules.</p>
    <table>
      <tr><th>Characteristic</th><th>EAN-13 behavior</th></tr>
      <tr><td>Length</td><td>13 digits</td></tr>
      <tr><td>Character set</td><td>Numeric only</td></tr>
      <tr><td>Check digit</td><td>Modulo-10</td></tr>
      <tr><td>Common use</td><td>International retail packaging</td></tr>
    </table>
    <h2>Why parity matters</h2>
    <p>The first digit is not printed inside the main bar structure in the same way as the following digits. Instead, the encoder uses left-side parity patterns to signal it. That is one reason hand-built or poorly implemented encoders create bad retail symbols even when the human-readable digits look right.</p>
    <div class="tool"><strong>Tool handoff:</strong> Compare international retail payloads in the <a href="/ean-13-barcode-generator.html">EAN-13 generator</a> before exporting final packaging artwork.</div>
""",
        "faq": [("Can EAN-13 and UPC-A coexist on the same package?", "Yes, but the artwork should be intentional so one retail identifier remains primary and scanner confusion is avoided.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("EAN-13 Generator", "/ean-13-barcode-generator.html"),
        ],
    },
    "symbologies/data-matrix/index.html": {
        "title": "Data Matrix: ECC 200, the L-Shaped Finder Pattern, and Small-Part Marking",
        "desc": "Data Matrix deep dive covering ECC 200, the L-shaped finder pattern, direct part marking, and industrial sizing choices.",
        "h1": "Data Matrix: ECC 200, the L-Shaped Finder Pattern, and Small-Part Marking",
        "body": """
    <p>Data Matrix is one of the most important industrial 2D symbologies because it stays readable at very small sizes and survives real manufacturing abuse. The standard most teams mean when they say “Data Matrix” today is ECC 200. That matters because ECC 200 defines the modern error-correction model and is the variant expected by most current industrial scanners and software workflows.</p>
    <p>One of the easiest visual signatures to verify is the solid L-shaped finder pattern. Two sides of the symbol form that solid border, while the opposite sides use alternating timing cells. If a page describing Data Matrix never mentions ECC 200 or the L-shaped finder pattern, it is missing the two fastest ways to distinguish the symbology technically.</p>
    <table>
      <tr><th>Attribute</th><th>Data Matrix note</th></tr>
      <tr><td>Error correction</td><td>ECC 200</td></tr>
      <tr><td>Finder</td><td>Solid L-shaped border</td></tr>
      <tr><td>Strength</td><td>Very small symbols and direct part marking</td></tr>
      <tr><td>Typical use</td><td>Medical, aerospace, electronics, serialized parts</td></tr>
    </table>
    <h2>Why it wins in tight spaces</h2>
    <p>Because the symbol stores data in two dimensions and is backed by strong error correction, it can carry serialized identifiers in footprints that would be impractical for most linear codes. That makes it especially attractive on surgical tools, electronics housings, and other space-constrained surfaces.</p>
    <div class="tool"><strong>Tool handoff:</strong> Use the <a href="/data-matrix-barcode-generator.html">Data Matrix generator</a> to test serialized payloads, then compare production constraints against the parent symbology guide.</div>
""",
        "faq": [("Can a laser line scanner read Data Matrix?", "No. Data Matrix requires a 2D imager because the symbol is a matrix, not a linear reflectance pattern.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("Data Matrix Generator", "/data-matrix-barcode-generator.html"),
        ],
    },
    "symbologies/qr-code/index.html": {
        "title": "QR Code: Consumer Scanning, Error Correction, and Payload Tradeoffs",
        "desc": "QR Code guide covering finder patterns, ECC levels, and the balance between scan resilience and payload density.",
        "h1": "QR Code: Consumer Scanning, Error Correction, and Payload Tradeoffs",
        "body": """
    <p>QR Code dominates consumer scanning because modern phone cameras already understand it and because its error-correction model supports real-world packaging abuse better than many teams expect. The tradeoff is that higher error-correction levels consume capacity, so every design decision is a balance between resilience, payload size, and visual density.</p>
    <p>The three large finder squares make QR easy to recognize and orient quickly. That visual familiarity is part of why it has become the preferred 2D carrier for consumer engagement and increasingly for GS1-based retail migration projects.</p>
    <table>
      <tr><th>ECC Level</th><th>General use</th></tr>
      <tr><td>L</td><td>Highest capacity, lowest recovery</td></tr>
      <tr><td>M</td><td>Balanced default for many web links</td></tr>
      <tr><td>Q</td><td>Better resilience for rough packaging</td></tr>
      <tr><td>H</td><td>Highest recovery, lowest raw capacity</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> Test consumer-facing payloads in the <a href="/2d-barcode-generator.html">2D barcode generator</a> and the <a href="/future/gs1-sunrise-2027-2d-barcode-migration/">GS1 Sunrise 2027 guide</a>.</div>
""",
        "faq": [("Is QR Code always the right 2D choice?", "No. QR is excellent for consumer interactions, but Data Matrix is often better for tiny industrial marks or dense structured identifiers.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("2D Barcode Generator", "/2d-barcode-generator.html"),
        ],
    },
    "symbologies/code-39/index.html": {
        "title": "Code 39: Wide Characters, Full ASCII Extensions, and Legacy Logistics",
        "desc": "Code 39 guide covering its classic character set, Full ASCII extensions, and why it still appears in legacy supply chains.",
        "h1": "Code 39: Wide Characters, Full ASCII Extensions, and Legacy Logistics",
        "body": """
    <p>Code 39 survives because it is simple, well understood, and widely supported in legacy industrial environments. Its downside is width. Every character consumes more horizontal space than denser symbologies such as Code 128, so long payloads quickly become awkward on small labels.</p>
    <p>The base symbology supports uppercase letters, digits, and a small set of punctuation. Full ASCII extensions exist, but they expand the printed length even further because some characters are represented through multi-character combinations.</p>
    <table>
      <tr><th>Strength</th><th>Constraint</th></tr>
      <tr><td>Simple legacy support</td><td>Large footprint</td></tr>
      <tr><td>Readable on older hardware</td><td>Limited native character set</td></tr>
      <tr><td>Useful for industrial IDs</td><td>Inefficient for long data</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> Compare Code 39 width against Code 128 in the <a href="/code-39-barcode-generator.html">Code 39 generator</a> and <a href="/code128-vs-code39.html">comparison page</a>.</div>
""",
        "faq": [("Why does Code 39 look longer than Code 128?", "Because Code 39 is a less dense symbology and encodes each character with a wider pattern.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("Code 39 Generator", "/code-39-barcode-generator.html"),
        ],
    },
    "symbologies/itf-14/index.html": {
        "title": "ITF-14: Carton-Level GTIN-14 Encoding and Bearer Bar Rules",
        "desc": "ITF-14 support page covering interleaved pairs, bearer bars, and corrugated print rules for master cartons.",
        "h1": "ITF-14: Carton-Level GTIN-14 Encoding and Bearer Bar Rules",
        "body": """
    <p>ITF-14 is built for outer-case logistics, not consumer checkout. It encodes GTIN-14 values through paired interleaving and is intentionally tolerant of rougher packaging materials such as corrugated stock. That makes it a practical choice for cartons and distribution handling where retail aesthetics are secondary to scan reliability.</p>
    <p>The most important visual protection feature is the bearer bar. These thick bars above and below the symbol reduce the risk of partial scans and are especially useful on uneven corrugated surfaces.</p>
    <table>
      <tr><th>Core rule</th><th>Why it matters</th></tr>
      <tr><td>Numeric-only GTIN-14</td><td>Matches carton identification workflows</td></tr>
      <tr><td>Bearer bars</td><td>Reduce short scans on rough surfaces</td></tr>
      <tr><td>Larger X-dimensions</td><td>Better tolerance on corrugated stock</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> Validate carton identifiers in the <a href="/itf-14-barcode-generator.html">ITF-14 generator</a> before applying them to outer-case layouts.</div>
""",
        "faq": [("Should ITF-14 replace UPC on retail products?", "No. ITF-14 is intended for cartons and outer packaging, while UPC or EAN remains the retail point-of-sale identifier.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("ITF-14 Generator", "/itf-14-barcode-generator.html"),
        ],
    },
    "symbologies/pdf417/index.html": {
        "title": "PDF417: Stacked 2D Transport for IDs, Documents, and Long Payloads",
        "desc": "PDF417 guide covering stacked rows, error-correction choices, and document-oriented payload design.",
        "h1": "PDF417: Stacked 2D Transport for IDs, Documents, and Long Payloads",
        "body": """
    <p>PDF417 sits between compact matrix codes and long linear formats. It uses stacked rows of codewords, which makes it useful for transport documents, IDs, boarding passes, and situations where a lot of structured data must be carried in a printable symbol without moving to a full database lookup.</p>
    <p>Because PDF417 can be tuned by row and column counts, the design conversation is usually about balancing density, aspect ratio, and scanner compatibility. It is powerful, but it is rarely the right answer when a shorter identifier and backend lookup would do the job more cleanly.</p>
    <table>
      <tr><th>Best fit</th><th>Watch out for</th></tr>
      <tr><td>Long document payloads</td><td>Oversized symbols on small labels</td></tr>
      <tr><td>Travel and credentialing</td><td>Aspect ratio mistakes</td></tr>
      <tr><td>Readable with imagers</td><td>Inconsistent printer scaling</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> Use the <a href="/pdf417-barcode-generator.html">PDF417 generator</a> for document-style payload experiments, then validate output size before print deployment.</div>
""",
        "faq": [("Is PDF417 smaller than QR Code for the same data?", "Not always. PDF417 is flexible for long structured data, but QR or Data Matrix can be more compact for many payloads.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("PDF417 Generator", "/pdf417-barcode-generator.html"),
        ],
    },
    "symbologies/aztec/index.html": {
        "title": "Aztec Code: Center Finder Geometry and Compact Ticketing Payloads",
        "desc": "Aztec Code guide covering its central finder pattern, space efficiency, and common ticketing use cases.",
        "h1": "Aztec Code: Center Finder Geometry and Compact Ticketing Payloads",
        "body": """
    <p>Aztec Code is a 2D symbology known for its bullseye-style center finder. That geometry means the symbol does not need the same surrounding quiet zone expectations as some other 2D carriers, which can be useful in tickets, transport documents, and constrained layouts.</p>
    <p>It is not as universally familiar to consumers as QR Code, but it remains attractive in closed-system transport and mobile-ticket workflows where scanners are already tuned for it.</p>
    <table>
      <tr><th>Strength</th><th>Typical use</th></tr>
      <tr><td>Compact with minimal border demands</td><td>Ticketing and transport</td></tr>
      <tr><td>Distinct center finder</td><td>Controlled scanning workflows</td></tr>
      <tr><td>Good resilience</td><td>Mobile boarding or event passes</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> For hands-on testing, open the <a href="/aztec-barcode-generator.html">Aztec generator</a> and compare symbol behavior with QR and PDF417 alternatives.</div>
""",
        "faq": [("Why is Aztec less common on retail packaging?", "Retail packaging and smartphone behaviors have standardized more heavily around QR and Data Matrix, while Aztec remains strong in controlled ticketing environments.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("Aztec Generator", "/aztec-barcode-generator.html"),
        ],
    },
    "symbologies/gs1-128/index.html": {
        "title": "GS1-128: Application Identifiers, FNC1, and Structured Supply-Chain Data",
        "desc": "GS1-128 guide covering AI syntax, FNC1 handling, and structured logistics payloads such as SSCC and expiry data.",
        "h1": "GS1-128: Application Identifiers, FNC1, and Structured Supply-Chain Data",
        "body": """
    <p>GS1-128 is not a separate bar pattern from Code 128 so much as a structured data discipline layered on top of it. The important implementation detail is that the payload uses GS1 Application Identifiers and FNC1 handling rules so scanners know where each field starts and ends.</p>
    <p>That is why teams implementing healthcare, warehouse, or carton labels usually spend more time validating field structure than choosing a rendering library. The bars are only half the problem. The data syntax is the other half.</p>
    <table>
      <tr><th>Component</th><th>Role</th></tr>
      <tr><td>Application Identifier</td><td>Declares the meaning and length behavior of each field</td></tr>
      <tr><td>FNC1</td><td>Separates variable-length fields when needed</td></tr>
      <tr><td>Code 128 engine</td><td>Provides the actual bar/space encoding</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> Use the <a href="/gs1-128-barcode-generator.html">GS1-128 generator</a> for AI payload trials and compare examples against the <a href="/compliance/healthcare-hibcc-gs1-standards/">healthcare compliance guide</a>.</div>
""",
        "faq": [("Why does GS1-128 need FNC1?", "Because variable-length GS1 fields must be separated clearly so scanners can parse the structured payload correctly.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("GS1-128 Generator", "/gs1-128-barcode-generator.html"),
        ],
    },
    "symbologies/dpm-best-practices/index.html": {
        "title": "Direct Part Marking Best Practices: Surviving Heat, Abrasion, and Tiny Surfaces",
        "desc": "DPM best practices for material selection, verifier settings, and tiny high-value industrial marks.",
        "h1": "Direct Part Marking Best Practices: Surviving Heat, Abrasion, and Tiny Surfaces",
        "body": """
    <p>Direct part marking lives in harsher conditions than paper labels. Marks may be etched, peened, lasered, or chemically applied to metal, plastic, or composite parts that later face abrasion, sterilization, oils, and aggressive lighting. That is why DPM is not just “print a smaller code.” It is a material and verification discipline.</p>
    <table>
      <tr><th>Challenge</th><th>DPM response</th></tr>
      <tr><td>Low contrast surfaces</td><td>Tune illumination and symbol size for the actual imager</td></tr>
      <tr><td>Heat or chemicals</td><td>Validate permanence after real process exposure</td></tr>
      <tr><td>Tiny marking area</td><td>Prefer Data Matrix with disciplined module sizing</td></tr>
    </table>
    <p>Always verify the mark after the manufacturing process, not just immediately after it is applied. Good marks can degrade once coatings, sterilization, or handling begins.</p>
    <div class="tool"><strong>Tool handoff:</strong> Start with the parent symbology guide, then compare compact matrix behavior in the <a href="/data-matrix-barcode-generator.html">Data Matrix generator</a>.</div>
""",
        "faq": [("Why is Data Matrix common in DPM?", "Because it provides strong ECC 200 recovery in a very compact footprint and is widely supported by industrial imagers.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("Data Matrix Generator", "/data-matrix-barcode-generator.html"),
        ],
    },
    "symbologies/gs1-api/index.html": {
        "title": "GS1 APIs and Digital Link: Structured Product Data Beyond the Symbol",
        "desc": "Guide to GS1-aware APIs, Digital Link resolution, and how structured identifiers map into web services.",
        "h1": "GS1 APIs and Digital Link: Structured Product Data Beyond the Symbol",
        "body": """
    <p>Once a barcode identifier leaves packaging and enters software, the question shifts from symbology to data exchange. GS1-aware APIs typically need to validate AI structure, preserve GTIN semantics, and increasingly support GS1 Digital Link URIs so the same identifier can participate in web-native workflows.</p>
    <p>This is where the barcode layer meets resolver services, product data stores, and traceability systems. A symbol on its own is only the capture mechanism. The surrounding API design determines whether the captured identifier becomes operationally useful.</p>
    <table>
      <tr><th>API concern</th><th>Why it matters</th></tr>
      <tr><td>AI validation</td><td>Rejects malformed GS1 payloads before they reach production systems</td></tr>
      <tr><td>Digital Link support</td><td>Allows web-native identifier resolution and richer consumer workflows</td></tr>
      <tr><td>Metadata mapping</td><td>Connects identifiers to product, lot, and serial records cleanly</td></tr>
    </table>
    <div class="tool"><strong>Tool handoff:</strong> Pair this page with the <a href="/developers/barcode-generation-api-sdk-guide/">developer API hub</a> and the <a href="/future/gs1-sunrise-2027-2d-barcode-migration/">GS1 Sunrise guide</a> when planning Digital Link flows.</div>
""",
        "faq": [("Is GS1 Digital Link only for QR codes?", "No. It is a web-native identifier model that can be encoded in supported 2D carriers, but the key idea is the standards-based URI structure.")],
        "related": [
            ("Ultimate Barcode Symbology Guide", "/symbologies/ultimate-barcode-type-guide/"),
            ("Developer API Hub", "/developers/barcode-generation-api-sdk-guide/"),
        ],
    },
}

PYTHON_SNIPPET = """import urllib.request
import urllib.parse

def fetch_svg(payload, symbology="code128"):
    base = "https://api.barcode-generators.com/v1/generate"
    query = urllib.parse.urlencode({"data": payload, "type": symbology, "format": "svg"})
    req = urllib.request.Request(f"{base}?{query}", headers={"Authorization": "Bearer YOUR_API_KEY"})
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")"""

JS_SNIPPET = """fetch(url, {headers:{Authorization:"Bearer YOUR_API_KEY"}})
  .then(r => r.text())
  .then(svg => document.getElementById("preview").innerHTML = svg);"""

PHP_SNIPPET = """$svg = file_get_contents($url, false, stream_context_create(["http" => ["header" => "Authorization: Bearer YOUR_API_KEY\\r\\n"]]));
file_put_contents("label.svg", $svg);"""

JAVA_SNIPPET = """WebClient client = WebClient.builder()
  .defaultHeader("Authorization", "Bearer YOUR_API_KEY")
  .build();
String svg = client.get().uri(uriBuilder -> uriBuilder.path("/v1/generate").queryParam("data", payload).queryParam("type", "code128").queryParam("format", "svg").build()).retrieve().bodyToMono(String.class).block();"""

CSHARP_SNIPPET = """using var client = new HttpClient();
client.DefaultRequestHeaders.Add("Authorization", "Bearer YOUR_API_KEY");
var svg = await client.GetStringAsync($"https://api.barcode-generators.com/v1/generate?data={Uri.EscapeDataString(payload)}&type=datamatrix&format=svg");"""

RUBY_SNIPPET = """response = Faraday.get("https://api.barcode-generators.com/v1/generate", {data: payload, type: "code128", format: "svg"}) do |req|
  req.headers["Authorization"] = "Bearer YOUR_API_KEY"
end
File.write("label.svg", response.body)"""

VBA_SNIPPET = """Sub FetchBarcode()
  Dim req As Object
  Set req = CreateObject("MSXML2.ServerXMLHTTP")
  req.Open "GET", "https://api.barcode-generators.com/v1/generate?data=" & Range("A2").Value & "&type=code128&format=svg", False
  req.setRequestHeader "Authorization", "Bearer YOUR_API_KEY"
  req.send
End Sub"""

DOCKER_SNIPPET = """docker run --rm -p 8080:8080 \\
  -e BARCODE_API_MODE=offline \\
  -e LOG_LEVEL=info \\
  barcode-generators/engine:latest"""

dev_pages = {
    "developers/python-barcode-generation/index.html": {
        "title": "Python Barcode Generation: Stream SVGs and Validate Payloads",
        "desc": "Python integration notes for barcode rendering pipelines, validation, and stream-safe exports.",
        "h1": "Python Barcode Generation: Stream SVGs and Validate Payloads",
        "body": f"""
    <p>Python is a good fit for barcode automation when you need batch processing, ETL integration, or quiet server-side workers that emit SVG and PDF assets into existing pipelines. The main discipline is to validate payload rules before you render, then stream the result to storage without unnecessary image conversion.</p>
    {code_sample(PYTHON_SNIPPET)}
    <h2>Checklist</h2><ul><li>Validate GTIN length, GS1 AI structure, or linear-code character rules locally.</li><li>Prefer SVG for print fidelity and easier downstream PDF composition.</li><li>Keep barcode generation stateless so retry logic stays predictable.</li></ul>
    <div class="tool"><strong>Next step:</strong> Return to the <a href="/developers/barcode-generation-api-sdk-guide/">Programmatic Barcode Generation API &amp; SDK Guide</a> for multi-language examples and shared API rules.</div>
""",
    },
    "developers/javascript-barcode-guide/index.html": {
        "title": "JavaScript Barcode Guide: Browser Rendering Without Geometry Drift",
        "desc": "JavaScript guidance for inline SVG rendering, barcode validation, and browser-safe export flows.",
        "h1": "JavaScript Barcode Guide: Browser Rendering Without Geometry Drift",
        "body": f"""
    <p>JavaScript is convenient for instant previews, but browser rendering can become dangerous if you scale raster exports, clip quiet zones, or hide validation rules behind permissive UI states. The safest pattern is to validate first, render to SVG second, and export with exact dimensions rather than responsive guesswork.</p>
    {code_sample(JS_SNIPPET)}
    <p>Use client-side rendering for previews and low-risk utility flows. Use server-side rendering when the output becomes a production label artifact.</p>
""",
    },
    "developers/php-barcode-pipelines/index.html": {
        "title": "PHP Barcode Pipelines: Queue-Safe Label Generation for Laravel and CMS Workflows",
        "desc": "PHP guidance for queue-backed barcode generation, file delivery, and validation in web applications.",
        "h1": "PHP Barcode Pipelines: Queue-Safe Label Generation for Laravel and CMS Workflows",
        "body": f"""
    <p>PHP-based commerce systems often need barcode generation at the moment an order, shipment, or pick ticket is created. The main architectural rule is to keep generation out of the user-facing request whenever payload volume or document composition grows.</p>
    {code_sample(PHP_SNIPPET)}
    <ul><li>Push heavy jobs onto queues.</li><li>Stream SVG or PDF responses instead of building giant in-memory blobs.</li><li>Validate GS1 fields before dispatching the job.</li></ul>
""",
    },
    "developers/java-spring-barcode-setup/index.html": {
        "title": "Java Spring Barcode Setup: Service Boundaries, Timeouts, and Queue Control",
        "desc": "Java and Spring guidance for barcode APIs, retry discipline, and service boundaries.",
        "h1": "Java Spring Barcode Setup: Service Boundaries, Timeouts, and Queue Control",
        "body": f"""
    <p>Spring services are a strong fit for enterprise barcode pipelines because they make it easy to separate validation, rendering requests, and downstream document packaging. The most important choice is where the job stops being synchronous and becomes queued background work.</p>
    {code_sample(JAVA_SNIPPET)}
    <p>Set explicit timeouts, surface 422 validation errors clearly, and do not let barcode retries issue duplicate sequential IDs without upstream state control.</p>
""",
    },
    "developers/csharp-datamatrix-generation/index.html": {
        "title": "C# Data Matrix Generation: Strongly Typed Payload Validation for Industrial Apps",
        "desc": "C# integration guidance for Data Matrix and structured barcode payloads in .NET services.",
        "h1": "C# Data Matrix Generation: Strongly Typed Payload Validation for Industrial Apps",
        "body": f"""
    <p>.NET teams usually benefit from strongly typed request models that validate payload length, serialization rules, and export format choices before the render request is even made. That approach is especially useful for Data Matrix work, where unit-level identifiers and industrial traceability fields often need tighter controls than consumer QR flows.</p>
    {code_sample(CSHARP_SNIPPET)}
""",
    },
    "developers/ruby-rails-barcode-integration/index.html": {
        "title": "Ruby on Rails Barcode Integration: Background Jobs and Attachment Strategy",
        "desc": "Rails guidance for barcode jobs, Active Storage, and controlled export workflows.",
        "h1": "Ruby on Rails Barcode Integration: Background Jobs and Attachment Strategy",
        "body": f"""
    <p>Rails barcode workflows are usually cleaner when the request creates a job record, a background worker renders the asset, and the result is attached or streamed only after validation passes. This avoids tying controller latency to image generation and document packaging.</p>
    {code_sample(RUBY_SNIPPET)}
""",
    },
    "developers/excel-barcode-integration/index.html": {
        "title": "Excel Barcode Integration: Controlled Imports, VBA, and Safer Bulk Exports",
        "desc": "Excel integration guidance for barcode generation, VBA automation, and safer spreadsheet handoffs.",
        "h1": "Excel Barcode Integration: Controlled Imports, VBA, and Safer Bulk Exports",
        "body": f"""
    <p>Excel remains a practical front door for many barcode workflows even when it is not the system of record. The safest pattern is to let business users prepare rows in a controlled template, then run validation before any barcode assets are generated.</p>
    {code_sample(VBA_SNIPPET)}
    <p>Use spreadsheets for review and intake. Use structured validation and queued generation for production output.</p>
""",
    },
    "developers/rest-api-documentation/index.html": {
        "title": "REST API Documentation: Endpoint Shape, Validation Behavior, and Error Handling",
        "desc": "Concise REST API documentation for barcode generation requests, responses, and validation errors.",
        "h1": "REST API Documentation: Endpoint Shape, Validation Behavior, and Error Handling",
        "body": """
    <p>The barcode API surface should stay intentionally small: one generation endpoint, predictable validation errors, and a clear contract for output formats. That keeps client SDKs easier to test and makes operational telemetry easier to interpret.</p>
    <table>
      <tr><th>Field</th><th>Meaning</th></tr>
      <tr><td>data</td><td>Raw payload to encode after client-side validation</td></tr>
      <tr><td>type</td><td>Symbology selector such as code128, upca, ean13, datamatrix, qr, or pdf417</td></tr>
      <tr><td>format</td><td>Preferred output such as svg, png, pdf, or eps</td></tr>
    </table>
    <pre><code>GET /v1/generate?data=012345678905&type=upca&format=svg
Authorization: Bearer YOUR_API_KEY</code></pre>
    <p>Return 422 for invalid payload structure, 429 for throttling, and content-type-specific success bodies for the requested format.</p>
""",
    },
    "developers/debugging-invalid-payloads/index.html": {
        "title": "Debugging Invalid Payloads: Why Good-Looking Strings Still Fail Barcode Rules",
        "desc": "Troubleshooting guide for payload validation errors, subset mismatches, and GS1 field issues.",
        "h1": "Debugging Invalid Payloads: Why Good-Looking Strings Still Fail Barcode Rules",
        "body": """
    <p>Most barcode rendering failures are not renderer bugs. They are payload mismatches: the wrong digit count for UPC-A, an unsupported character in a linear symbology, or a GS1 field sequence that breaks AI parsing rules. Debugging gets faster when you classify errors by rule family instead of by library.</p>
    <ul>
      <li>Length errors: wrong GTIN size, missing check digit, truncated serials.</li>
      <li>Character-set errors: lowercase or punctuation in restricted symbologies.</li>
      <li>Structured-data errors: missing FNC1 behavior or broken AI boundaries.</li>
    </ul>
    <p>Start by validating the raw string before you inspect output geometry. In enterprise systems, payload errors should never make it to the render stage unclassified.</p>
""",
    },
    "developers/on-premise-docker-containers/index.html": {
        "title": "On-Premise Docker Containers: Private Barcode Rendering Without a Public Upload Flow",
        "desc": "On-premise deployment notes for containerized barcode rendering in private-cloud and regulated environments.",
        "h1": "On-Premise Docker Containers: Private Barcode Rendering Without a Public Upload Flow",
        "body": f"""
    <p>Containerized barcode rendering is useful when identifiers cannot leave a private network or when plants operate with intermittent connectivity. The real design question is not whether the image renderer fits in a container. It is how secrets, logs, upgrades, and temporary job data behave once the engine is inside the customer boundary.</p>
    {code_sample(DOCKER_SNIPPET)}
    <ul><li>Bind secrets through approved secret stores, not hard-coded environment values in compose files.</li><li>Document whether temporary objects are written to disk or kept in memory.</li><li>Separate rendering workers from public ingress when multi-tenant policies matter.</li></ul>
""",
    },
}

prod_svg = '<svg viewBox="0 0 220 72" xmlns="http://www.w3.org/2000/svg" aria-label="vector barcode example"><rect width="220" height="72" fill="#fff"/><rect x="14" y="10" width="4" height="52" fill="#111"/><rect x="24" y="10" width="8" height="52" fill="#111"/><rect x="40" y="10" width="3" height="52" fill="#111"/><rect x="52" y="10" width="7" height="52" fill="#111"/><rect x="66" y="10" width="4" height="52" fill="#111"/><rect x="78" y="10" width="10" height="52" fill="#111"/><rect x="96" y="10" width="4" height="52" fill="#111"/><rect x="108" y="10" width="6" height="52" fill="#111"/><rect x="122" y="10" width="3" height="52" fill="#111"/><rect x="134" y="10" width="8" height="52" fill="#111"/><rect x="148" y="10" width="4" height="52" fill="#111"/><rect x="160" y="10" width="7" height="52" fill="#111"/><rect x="174" y="10" width="5" height="52" fill="#111"/></svg>'

prod_pages = {
    "production/color-contrast-optimization/index.html": {
        "title": "Color Contrast Optimization: Why Red Fails Many Laser Barcode Scanners",
        "desc": "Color and wavelength guidance for barcode print contrast, including red-laser limits around 630-670 nm.",
        "h1": "Color Contrast Optimization: Why Red Fails Many Laser Barcode Scanners",
        "body": f"""
    <p>Color choice is not decorative in barcode work. Many commercial laser scanners emit red light in roughly the 630-670 nm range, so red bars or low-contrast warm tones can reflect that wavelength back poorly and collapse the edge transitions the scanner needs. That is why a barcode that looks stylish to a designer can still fail at the hardware level.</p>
    {prod_svg}
    <table>
      <tr><th>Safe pattern</th><th>Risky pattern</th></tr>
      <tr><td>Black or dark blue bars on white</td><td>Red bars, orange bars, or glossy reflective backgrounds</td></tr>
      <tr><td>Matte high contrast</td><td>Low-contrast tint-on-tint combinations</td></tr>
    </table>
    <p>Always test on representative hardware rather than approving color combinations from screen appearance alone.</p>
""",
    },
    "production/ink-bleed-compensation-bwr/index.html": {
        "title": "Ink Bleed Compensation and BWR: Keeping Bars from Closing Up",
        "desc": "Practical Bar Width Reduction guidance for flexo, thermal transfer, and other barcode print workflows.",
        "h1": "Ink Bleed Compensation and BWR: Keeping Bars from Closing Up",
        "body": f"""
    <p>Ink spread turns good digital geometry into bad printed geometry. Bar Width Reduction, or BWR, counteracts that spread by shrinking bars slightly before print so the final physical mark lands closer to the intended width.</p>
    {prod_svg}
    <ul><li>Start with conservative compensation and verify on the real substrate.</li><li>Measure printed bars, not just press settings.</li><li>Revalidate after ink, speed, stock, or darkness changes.</li></ul>
""",
    },
    "production/minimum-dimension-scaling/index.html": {
        "title": "Minimum Dimension Scaling: Matching X-Dimension to Printer DPI",
        "desc": "Guide to choosing X-dimensions and module sizes that survive real printer DPI limits.",
        "h1": "Minimum Dimension Scaling: Matching X-Dimension to Printer DPI",
        "body": f"""
    <p>Barcode quality starts with sizing that the printer can actually reproduce. If the selected X-dimension resolves into awkward fractional dots or anti-aliased scaling, the printed mark will drift from the intended geometry.</p>
    {prod_svg}
    <table>
      <tr><th>Printer DPI</th><th>Common starting point</th></tr>
      <tr><td>203</td><td>10-12 mil for many linear labels</td></tr>
      <tr><td>300</td><td>7-10 mil when substrate and scanner allow</td></tr>
      <tr><td>600</td><td>Fine-detail work with careful validation</td></tr>
    </table>
    <p>Use integer-dot thinking where possible and validate the physical result instead of trusting CSS scaling.</p>
""",
    },
    "production/scannability-troubleshooting/index.html": {
        "title": "Scannability Troubleshooting: Diagnosing Quiet Zones, Contrast, and Geometry Failures",
        "desc": "Troubleshooting guide for the most common production barcode scan failures.",
        "h1": "Scannability Troubleshooting: Diagnosing Quiet Zones, Contrast, and Geometry Failures",
        "body": f"""
    <p>When a barcode stops scanning, the failure usually falls into one of four buckets: bad data, damaged geometry, weak contrast, or hardware mismatch. The fastest troubleshooting path is to isolate which bucket you are dealing with before changing everything at once.</p>
    {prod_svg}
    <table>
      <tr><th>Symptom</th><th>Likely cause</th></tr>
      <tr><td>Phone scans, laser does not</td><td>Contrast or wavelength mismatch</td></tr>
      <tr><td>Intermittent reads on conveyor</td><td>Quiet zone or truncation issues</td></tr>
      <tr><td>Only some batches fail</td><td>Press, darkness, or substrate drift</td></tr>
    </table>
""",
    },
    "production/thermal-printer-calibration/index.html": {
        "title": "Thermal Printer Calibration: Darkness, Speed, and Proofing Discipline",
        "desc": "Thermal printer calibration guide for label output that stays within barcode tolerances.",
        "h1": "Thermal Printer Calibration: Darkness, Speed, and Proofing Discipline",
        "body": f"""
    <p>Thermal printers fail barcode quality most often through over-darkness, feed-speed mismatches, and neglected cleaning. Calibration is less about a magic setting than about repeatable proofing after every meaningful process change.</p>
    {prod_svg}
    <ol><li>Clean the head and rollers.</li><li>Print a proof ladder at multiple darkness levels.</li><li>Validate the chosen setting with the target scanner or verifier.</li><li>Lock the profile by stock and use case.</li></ol>
""",
    },
    "production/vector-vs-raster-barcode-formats/index.html": {
        "title": "Vector vs Raster Barcode Formats: Why SVG Wins for Production Geometry",
        "desc": "Guide to vector and raster barcode formats with inline SVG proofing and print workflow notes.",
        "h1": "Vector vs Raster Barcode Formats: Why SVG Wins for Production Geometry",
        "body": f"""
    <p>Vector barcode assets preserve geometry mathematically. Raster files store a grid of pixels and are therefore sensitive to DPI, interpolation, and scaling mistakes. If your workflow involves packaging, labels, or document composition, SVG or other vector formats are usually the safest choice.</p>
    <h2>Inline vector proof</h2>
    {prod_svg}
    <p>The example above is rendered directly as inline SVG using rectangles, not as a PNG or JPEG. That matters because the browser can scale it without inventing new edge pixels.</p>
    <table>
      <tr><th>Format</th><th>Best use</th></tr>
      <tr><td>SVG</td><td>Web previews, archival geometry, print handoff</td></tr>
      <tr><td>PDF/EPS</td><td>Print-native workflows and composed documents</td></tr>
      <tr><td>PNG</td><td>Limited proofs when DPI is tightly controlled</td></tr>
      <tr><td>JPG</td><td>Avoid for production barcodes because compression damages edges</td></tr>
    </table>
""",
    },
}


def main():
    for rel, cfg in sym_pages.items():
        write_page(
            rel,
            article_page(
                cfg["title"],
                cfg["desc"],
                "https://barcode-generators.com/" + rel.replace("index.html", ""),
                cfg["h1"],
                "/symbologies/ultimate-barcode-type-guide/",
                "Barcode Symbologies Guide",
                cfg["body"],
                related=cfg["related"],
                schema_type="Article",
                faq=cfg["faq"],
            ),
        )

    for rel, cfg in dev_pages.items():
        write_page(
            rel,
            article_page(
                cfg["title"],
                cfg["desc"],
                "https://barcode-generators.com/" + rel.replace("index.html", ""),
                cfg["h1"],
                "/developers/barcode-generation-api-sdk-guide/",
                "Programmatic Barcode Generation API & SDK Guide",
                cfg["body"],
                related=[
                    ("Developer Hub", "/developers/"),
                    ("API & SDK Guide", "/developers/barcode-generation-api-sdk-guide/"),
                ],
                schema_type="Article",
            ),
        )

    for rel, cfg in prod_pages.items():
        write_page(
            rel,
            article_page(
                cfg["title"],
                cfg["desc"],
                "https://barcode-generators.com/" + rel.replace("index.html", ""),
                cfg["h1"],
                "/production/perfect-barcode-print-optimization-guide/",
                "Barcode Print Calibration Guide",
                cfg["body"],
                related=[
                    ("Production Hub", "/production/perfect-barcode-print-optimization-guide/"),
                    ("Print Guide", "/barcode-printing-guide.html"),
                ],
                schema_type="Article",
            ),
        )

    favicon_bytes = bytes.fromhex(
        "00000100010010100000010020006804000016000000280000001000000020000000010020000000000040040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000112233001122330011223300112233001122330011223300112233001122330011223300112233001122330011223300112233001122330011223300112233001122330011223300FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF11223300FF3366FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFF3366FFFF3366FFFF3366FFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFF3366FFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FFFFFFFFFF3366FF11223300FF3366FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF3366FF11223300FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF3366FF1122330000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    )
    (ROOT / "favicon.ico").write_bytes(favicon_bytes)
    print("Generated support pages and favicon.")


if __name__ == "__main__":
    main()
