import json
import os
import re
from difflib import SequenceMatcher
from html import unescape
from itertools import combinations


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(ROOT, "reports")
REPORT_PATH = os.path.join(REPORT_DIR, "site_audit.json")
TOPICAL_REPORT_PATH = os.path.join(REPORT_DIR, "topical-authority-audit.md")

PLACEHOLDER_MARKERS = [
    "placeholder",
    "coming soon",
    "section content goes here",
    "to be added",
]

UTILITY_PAGES = {
    "about-us.html",
    "contact-us.html",
    "editorial-guidelines.html",
    "google8a2939e9b7d79b04.html",
    "index.php",
    "privacy.html",
    "search.html",
    "sitemap.html",
    "team.html",
    "terms.html",
}

CORE_GUIDE_PAGES = {
    "barcode-format-guide.html",
    "barcode-size-guide.html",
    "barcode-types.html",
    "barcode-use-cases.html",
    "how-to-create-barcode.html",
    "what-is-barcode.html",
}

TOPICAL_PILLARS = [
    {
        "name": "Barcode Fundamentals and Education",
        "status": "partial",
        "priority": 1,
        "current_assets": [
            "what-is-barcode.html",
            "how-to-create-barcode.html",
            "barcode-types.html",
            "barcode-format-guide.html",
            "barcode-use-cases.html",
        ],
        "gaps": [
            "barcode scanner types and how they decode symbols",
            "barcode verification vs validation vs generation",
            "check digits, quiet zones, and sizing fundamentals",
            "decision guides for 1D vs 2D vs QR vs Data Matrix",
        ],
    },
    {
        "name": "Symbologies and Encoding Rules",
        "status": "partial",
        "priority": 2,
        "current_assets": [
            "symbologies/ultimate-barcode-type-guide/index.html",
            "symbologies/code-128/index.html",
            "symbologies/upc-a/index.html",
            "symbologies/data-matrix/index.html",
            "symbologies/qr-code/index.html",
        ],
        "gaps": [
            "expand thin child pages into full spec-grade references",
            "add missing deep dives for UPC-E, EAN-8, Codabar, ISBN, and ISSN",
            "cover Micro QR, MaxiCode, and composite GS1 symbologies where relevant",
            "publish more comparison pages beyond ean-vs-upc and code128-vs-code39",
        ],
    },
    {
        "name": "GS1, Standards, and Compliance",
        "status": "partial",
        "priority": 3,
        "current_assets": [
            "compliance/industry-barcode-standards-guide/index.html",
            "compliance/amazon-fba-barcode-requirements/index.html",
            "compliance/gs1-company-prefix-guide/index.html",
            "compliance/healthcare-hibcc-gs1-standards/index.html",
        ],
        "gaps": [
            "GTIN allocation rules, SSCC, GLN, and GS1 application identifiers",
            "ISO/IEC 15415, 15416, and 29158 verification standards",
            "UDI, DSCSA, EU FMD, and sector-specific compliance workflows",
            "carrier and retailer label requirements beyond Amazon FBA",
        ],
    },
    {
        "name": "Printing, Scanning, and Verification",
        "status": "weak",
        "priority": 4,
        "current_assets": [
            "production/perfect-barcode-print-optimization-guide/index.html",
            "production/thermal-printer-calibration/index.html",
            "production/scannability-troubleshooting/index.html",
        ],
        "gaps": [
            "scanner hardware selection and laser vs imager guidance",
            "barcode verifier grading workflows and troubleshooting SOPs",
            "label materials, adhesives, substrates, and placement rules",
            "print QA checklists by printer type and environment",
        ],
    },
    {
        "name": "Developer APIs and Integrations",
        "status": "weak",
        "priority": 5,
        "current_assets": [
            "developers/barcode-generation-api-sdk-guide/index.html",
            "developers/rest-api-documentation/index.html",
            "developers/python-barcode-generation/index.html",
            "developers/javascript-barcode-guide/index.html",
        ],
        "gaps": [
            "real request/response examples and validation recipes",
            "auth, rate limits, error catalogs, and retry behavior",
            "SDK quickstarts that are more than thin overviews",
            "platform guides for Shopify, WooCommerce, Excel, Word, ERP, and WMS flows",
        ],
    },
    {
        "name": "Industry Workflows and Use Cases",
        "status": "partial",
        "priority": 6,
        "current_assets": [
            "barcode-use-cases.html",
            "inventory-barcode-generator.html",
            "warehouse-barcode-generator.html",
            "shipping-barcode-generator.html",
        ],
        "gaps": [
            "editorial workflow guides to support generator landing pages",
            "retail, healthcare, publishing, manufacturing, and field-service clusters",
            "labeling SOPs for receiving, picking, packing, and traceability",
            "role-based guides for operations managers, IT teams, and compliance leads",
        ],
    },
    {
        "name": "Enterprise Operations and Governance",
        "status": "partial",
        "priority": 7,
        "current_assets": [
            "enterprise/secure-bulk-barcode-generation/index.html",
            "developers/on-premise-docker-containers/index.html",
        ],
        "gaps": [
            "template governance, approvals, and audit trails",
            "security architecture, PII handling, and on-prem deployment patterns",
            "batch recovery, versioning, and observability for bulk generation",
            "governance content for cross-team barcode ownership",
        ],
    },
    {
        "name": "2D Migration and the Future of Barcodes",
        "status": "partial",
        "priority": 8,
        "current_assets": [
            "future/gs1-sunrise-2027-2d-barcode-migration/index.html",
            "symbologies/gs1-api/index.html",
        ],
        "gaps": [
            "GS1 Digital Link implementation details",
            "POS readiness and coexistence checklists for 1D plus 2D packaging",
            "packaging redesign, governance, and rollout measurement playbooks",
            "merchant adoption roadmaps for brands, retailers, and solution teams",
        ],
    },
]

LEGACY_REDIRECTS = {
    "barcode-types-guide.html": "/symbologies/ultimate-barcode-type-guide/",
    "barcode-standards-guide.html": "/compliance/industry-barcode-standards-guide/",
    "barcode-printing-guide.html": "/production/perfect-barcode-print-optimization-guide/",
    "bulk-custom-barcode-guide.html": "/enterprise/secure-bulk-barcode-generation/",
    "barcode-tech-trends-guide.html": "/future/gs1-sunrise-2027-2d-barcode-migration/",
    "barcode-usecase-guide.html": "/barcode-use-cases.html",
    "barcode-generator-guide.html": "/barcode-generator.html",
    "barcode-basics.html": "/what-is-barcode.html",
}

PILLARS = {
    "symbologies": {
        "hub": "symbologies/ultimate-barcode-type-guide/index.html",
        "hub_url": "/symbologies/ultimate-barcode-type-guide/",
        "schema": ["TechArticle", "FAQPage"],
        "children": [
            "symbologies/code-128/index.html",
            "symbologies/upc-a/index.html",
            "symbologies/ean-13/index.html",
            "symbologies/data-matrix/index.html",
            "symbologies/qr-code/index.html",
            "symbologies/code-39/index.html",
            "symbologies/itf-14/index.html",
            "symbologies/pdf417/index.html",
            "symbologies/aztec/index.html",
            "symbologies/gs1-128/index.html",
            "symbologies/dpm-best-practices/index.html",
            "symbologies/gs1-api/index.html",
        ],
        "widget_ids": ["multi-symbology-tester", "tester-run", "action-panel"],
    },
    "compliance": {
        "hub": "compliance/industry-barcode-standards-guide/index.html",
        "hub_url": "/compliance/industry-barcode-standards-guide/",
        "schema": ["Article", "FAQPage"],
        "children": [
            "compliance/amazon-fba-barcode-requirements/index.html",
            "compliance/gs1-company-prefix-guide/index.html",
            "compliance/healthcare-hibcc-gs1-standards/index.html",
            "compliance/isbn-publishing-guide/index.html",
            "compliance/avoiding-retail-chargebacks/index.html",
            "compliance/outer-case-packaging-rules/index.html",
            "compliance/label-tolerance-testing/index.html",
            "compliance/gs1-coupon-code-architecture/index.html",
        ],
        "widget_ids": ["compliance-validator", "cv-run"],
    },
    "developers": {
        "hub": "developers/barcode-generation-api-sdk-guide/index.html",
        "hub_url": "/developers/barcode-generation-api-sdk-guide/",
        "schema": ["Article", "FAQPage", "HowTo"],
        "children": [
            "developers/python-barcode-generation/index.html",
            "developers/javascript-barcode-guide/index.html",
            "developers/php-barcode-pipelines/index.html",
            "developers/java-spring-barcode-setup/index.html",
            "developers/csharp-datamatrix-generation/index.html",
            "developers/ruby-rails-barcode-integration/index.html",
            "developers/excel-barcode-integration/index.html",
            "developers/rest-api-documentation/index.html",
            "developers/debugging-invalid-payloads/index.html",
            "developers/on-premise-docker-containers/index.html",
        ],
        "widget_ids": ["tabs", "snippet", "test"],
    },
    "production": {
        "hub": "production/perfect-barcode-print-optimization-guide/index.html",
        "hub_url": "/production/perfect-barcode-print-optimization-guide/",
        "schema": ["Article", "FAQPage", "HowTo"],
        "children": [
            "production/thermal-printer-calibration/index.html",
            "production/vector-vs-raster-barcode-formats/index.html",
            "production/ink-bleed-compensation-bwr/index.html",
            "production/minimum-dimension-scaling/index.html",
            "production/scannability-troubleshooting/index.html",
            "production/color-contrast-optimization/index.html",
        ],
        "widget_ids": ["dpi-tool", "calc"],
    },
    "enterprise": {
        "hub": "enterprise/secure-bulk-barcode-generation/index.html",
        "hub_url": "/enterprise/secure-bulk-barcode-generation/",
        "schema": ["Article", "FAQPage"],
        "children": [],
        "widget_ids": ["bulk-input", "csv-file", "run-sim"],
    },
    "future": {
        "hub": "future/gs1-sunrise-2027-2d-barcode-migration/index.html",
        "hub_url": "/future/gs1-sunrise-2027-2d-barcode-migration/",
        "schema": ["Article", "FAQPage"],
        "children": [],
        "widget_ids": ["build-link", "qr-preview", "uri-output"],
    },
}

TECHNICAL_TRUTHS = {
    "upc_a_facts": {
        "file": "symbologies/upc-a/index.html",
        "must_include": ["12", "numeric", "modulo-10"],
    },
    "code_128_facts": {
        "file": "symbologies/code-128/index.html",
        "must_include": ["subset a", "subset b", "subset c", "modulo-103"],
    },
    "data_matrix_facts": {
        "file": "symbologies/data-matrix/index.html",
        "must_include": ["ecc 200", "l-shaped"],
    },
    "color_wavelength_facts": {
        "file": "production/color-contrast-optimization/index.html",
        "must_include": ["630", "670", "red laser"],
    },
}

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
HREF_RE = re.compile(r'href\s*=\s*"([^"]+)"', re.IGNORECASE)
LABEL_FOR_RE = re.compile(r'<label[^>]*for\s*=\s*"([^"]+)"', re.IGNORECASE)
INPUT_RE = re.compile(r"<input[^>]*>", re.IGNORECASE)
ID_RE = re.compile(r'id\s*=\s*"([^"]+)"', re.IGNORECASE)
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"', re.IGNORECASE)
OG_URL_RE = re.compile(r'<meta property="og:url" content="([^"]+)"', re.IGNORECASE)
HTML_LANG_RE = re.compile(r"<html[^>]+lang=\"([^\"]+)\"", re.IGNORECASE)
EMPTY_ANCHOR_RE = re.compile(r'<a\b[^>]*href\s*=\s*"[^"]+"[^>]*>\s*</a>', re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
SCRIPT_JSON_RE = re.compile(
    r'<script[^>]*type\s*=\s*"application/ld\+json"[^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
IMG_RASTER_RE = re.compile(r'<img[^>]+src\s*=\s*"[^"]+\.(png|jpe?g)"', re.IGNORECASE)
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SEO_SECTION_RE = re.compile(
    r'<section class="content-section seo-optimized-content" style="margin-top: 3rem;">[\s\S]*?</section>',
    re.IGNORECASE,
)
HERO_SECTION_RE = re.compile(r'<section class="hero-section">[\s\S]*?</section>', re.IGNORECASE)


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return handle.read()


def list_html_files():
    html_files = []
    for dirpath, _, filenames in os.walk(ROOT):
        for filename in filenames:
            if filename.lower().endswith(".html"):
                html_files.append(os.path.join(dirpath, filename))
    return sorted(html_files)


def strip_html(text):
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(text).lower()


def word_count(text):
    return len(WORD_RE.findall(strip_html(text)))


def normalized_visible_text(text):
    return re.sub(r"\s+", " ", strip_html(text)).strip()


def is_redirect_page(text):
    lowered = text.lower()
    return (
        'http-equiv="refresh"' in lowered
        or "location.replace(" in lowered
        or "window.location" in lowered
    )


def page_section(rel_path):
    return rel_path.split("/", 1)[0] if "/" in rel_path else "(root)"


def page_intent(rel_path, text=None):
    if rel_path in UTILITY_PAGES:
        return "utility"
    if rel_path in LEGACY_REDIRECTS:
        return "redirect"
    if text and is_redirect_page(text):
        return "redirect"
    if rel_path == "index.html":
        return "homepage"
    if rel_path in CORE_GUIDE_PAGES or "-vs-" in rel_path or rel_path.endswith("-guide.html"):
        return "guide"
    if "/" not in rel_path and (
        "generator" in rel_path or rel_path in {"barcode-maker.html", "barcode-creator.html"}
    ):
        return "generator"
    if rel_path in {config["hub"] for config in PILLARS.values()}:
        return "pillar_hub"
    if rel_path.count("/") == 1 and rel_path.endswith("/index.html"):
        return "section_hub"
    if rel_path.endswith("/index.html"):
        return "support_article"
    return "page"


def internal_href(href):
    if not href or href.startswith("#"):
        return False
    href = href.strip()
    return not any(
        href.startswith(prefix)
        for prefix in ("http://", "https://", "mailto:", "tel:", "javascript:")
    )


def resolve_target(source_rel, href):
    href = href.split("#", 1)[0]
    if href.startswith("/"):
        base = href.lstrip("/")
    else:
        base = os.path.normpath(os.path.join(os.path.dirname(source_rel), href)).replace("\\", "/")
    if base in ("", "."):
        return "index.html"
    if base.endswith("/"):
        return base + "index.html"
    if os.path.splitext(base)[1]:
        return base
    return base + "/index.html"


def has_schema_type(text, schema_type):
    return f'"@type":"{schema_type}"' in compact_jsonld(text) or f'"@type": "{schema_type}"' in text


def compact_jsonld(text):
    blocks = []
    for block in SCRIPT_JSON_RE.findall(text):
        blocks.append(re.sub(r"\s+", "", block))
    return " ".join(blocks)


def page_has_widget_ids(text, widget_ids):
    return all(f'id="{widget_id}"' in text for widget_id in widget_ids)


def audit_metadata_and_navigation(html_files):
    og_url_mismatches = []
    empty_h1_pages = []
    pages_with_empty_anchors = []
    missing_hreflang_pages = []

    for absolute_path in html_files:
        rel = os.path.relpath(absolute_path, ROOT).replace("\\", "/")
        text = read_file(absolute_path)
        canonical = CANONICAL_RE.search(text)
        og_url = OG_URL_RE.search(text)
        h1 = H1_RE.search(text)
        html_lang = HTML_LANG_RE.search(text)

        if canonical and og_url and canonical.group(1) != og_url.group(1):
            og_url_mismatches.append(
                {
                    "path": rel,
                    "canonical": canonical.group(1),
                    "og_url": og_url.group(1),
                }
            )

        if h1 and not re.sub(r"<[^>]+>", "", h1.group(1)).strip():
            empty_h1_pages.append(rel)

        empty_anchor_count = len(EMPTY_ANCHOR_RE.findall(text))
        if empty_anchor_count:
            pages_with_empty_anchors.append(
                {
                    "path": rel,
                    "empty_anchor_count": empty_anchor_count,
                }
            )

        if html_lang and "hreflang=" not in text.lower():
            missing_hreflang_pages.append(
                {
                    "path": rel,
                    "lang": html_lang.group(1),
                }
            )

    return {
        "og_url_mismatches": og_url_mismatches,
        "empty_h1_pages": empty_h1_pages,
        "pages_with_empty_anchors": pages_with_empty_anchors,
        "missing_hreflang_pages": missing_hreflang_pages,
    }


def check_internal_links(html_files):
    broken_links = []
    missing_titles = []
    unlabeled_inputs = {}
    for absolute_path in html_files:
        rel = os.path.relpath(absolute_path, ROOT).replace("\\", "/")
        text = read_file(absolute_path)

        if not TITLE_RE.search(text):
            missing_titles.append(rel)

        labels = set(LABEL_FOR_RE.findall(text))
        for input_tag in INPUT_RE.findall(text):
            input_id = ID_RE.search(input_tag)
            if input_id and input_id.group(1) not in labels:
                unlabeled_inputs.setdefault(rel, []).append(input_id.group(1))

        for href in HREF_RE.findall(text):
            if not internal_href(href):
                continue
            target_rel = resolve_target(rel, href)
            if not os.path.exists(os.path.join(ROOT, target_rel)):
                broken_links.append(
                    {
                        "source": rel,
                        "href": href,
                        "resolved_target": target_rel,
                    }
                )
    return broken_links, missing_titles, unlabeled_inputs


def audit_pillars():
    pillar_report = {}
    for pillar_name, config in PILLARS.items():
        hub_path = os.path.join(ROOT, config["hub"])
        hub_text = read_file(hub_path)
        hub_compact = compact_jsonld(hub_text)
        missing_schema = [
            schema_name
            for schema_name in config["schema"]
            if f'"@type":"{schema_name}"' not in hub_compact
            and f'"@type":"{schema_name}"' not in hub_text.replace(" ", "")
        ]

        missing_widget_ids = [
            widget_id for widget_id in config["widget_ids"] if f'id="{widget_id}"' not in hub_text
        ]

        missing_child_links = []
        child_issues = []
        for child in config["children"]:
            child_url = "/" + child.replace("index.html", "")
            if child_url not in hub_text:
                missing_child_links.append(child_url)

            child_text = read_file(os.path.join(ROOT, child))
            plain = strip_html(child_text)
            if config["hub_url"] not in child_text:
                child_issues.append({"child": child, "issue": "missing_backlink"})
            if any(marker in plain for marker in PLACEHOLDER_MARKERS):
                child_issues.append({"child": child, "issue": "placeholder"})
            child_compact = compact_jsonld(child_text)
            if '"@type":"Article"' not in child_compact and '"@type":"TechArticle"' not in child_compact:
                child_issues.append({"child": child, "issue": "missing_article_schema"})

        pillar_report[pillar_name] = {
            "hub": config["hub"],
            "missing_hub_schema": missing_schema,
            "missing_widget_ids": missing_widget_ids,
            "missing_child_links": missing_child_links,
            "child_issues": child_issues,
        }
    return pillar_report


def audit_technical_truths():
    truth_report = {}
    for check_name, config in TECHNICAL_TRUTHS.items():
        page_text = strip_html(read_file(os.path.join(ROOT, config["file"])))
        missing_terms = [term for term in config["must_include"] if term not in page_text]
        truth_report[check_name] = {
            "file": config["file"],
            "missing_terms": missing_terms,
        }
    return truth_report


def audit_assets():
    production_pages = [
        "production/perfect-barcode-print-optimization-guide/index.html",
        "production/vector-vs-raster-barcode-formats/index.html",
        "production/color-contrast-optimization/index.html",
    ]
    asset_report = {}
    for rel_path in production_pages:
        text = read_file(os.path.join(ROOT, rel_path))
        asset_report[rel_path] = {
            "has_inline_svg": "<svg" in text.lower(),
            "uses_raster_img_tags": bool(IMG_RASTER_RE.search(text)),
        }
    return asset_report


def audit_legacy_redirects():
    redirect_report = {}
    for rel_path, target in LEGACY_REDIRECTS.items():
        text = read_file(os.path.join(ROOT, rel_path))
        redirect_report[rel_path] = {
            "target": target,
            "is_redirect_or_canonicalized": target in text and (
                "http-equiv=\"refresh\"" in text.lower()
                or "location.replace(" in text
                or f'href="{target}"' in text
            ),
        }
    return redirect_report


def audit_topical_authority(html_files):
    section_stats = {}
    intent_counts = {}
    support_articles = []
    editorial_pages = []

    for absolute_path in html_files:
        rel = os.path.relpath(absolute_path, ROOT).replace("\\", "/")
        text = read_file(absolute_path)
        words = word_count(text)
        section = page_section(rel)
        intent = page_intent(rel, text)

        intent_counts[intent] = intent_counts.get(intent, 0) + 1

        if section not in section_stats:
            section_stats[section] = {
                "page_count": 0,
                "generator_pages": 0,
                "editorial_pages": 0,
                "support_article_count": 0,
                "support_articles_under_150_words": 0,
                "support_articles_under_300_words": 0,
                "total_words": 0,
            }

        section_stats[section]["page_count"] += 1
        section_stats[section]["total_words"] += words

        if intent == "generator":
            section_stats[section]["generator_pages"] += 1

        if intent in {"guide", "pillar_hub", "section_hub", "support_article"}:
            section_stats[section]["editorial_pages"] += 1
            editorial_pages.append({"path": rel, "section": section, "word_count": words})

        if intent == "support_article":
            section_stats[section]["support_article_count"] += 1
            if words < 150:
                section_stats[section]["support_articles_under_150_words"] += 1
            if words < 300:
                section_stats[section]["support_articles_under_300_words"] += 1
            support_articles.append({"path": rel, "section": section, "word_count": words})

    for stats in section_stats.values():
        stats["average_words_per_page"] = round(stats["total_words"] / stats["page_count"], 1)
        if stats["support_article_count"]:
            stats["thin_support_share_under_300_words"] = round(
                stats["support_articles_under_300_words"] / stats["support_article_count"], 3
            )
        else:
            stats["thin_support_share_under_300_words"] = 0.0
        del stats["total_words"]

    thin_sections = []
    for section, stats in sorted(section_stats.items()):
        if stats["support_article_count"] and stats["thin_support_share_under_300_words"] >= 0.6:
            thin_sections.append(
                {
                    "section": section,
                    "thin_support_share_under_300_words": stats["thin_support_share_under_300_words"],
                    "support_article_count": stats["support_article_count"],
                }
            )

    editorial_over_1000 = sorted(
        [page for page in editorial_pages if page["word_count"] >= 1000],
        key=lambda page: page["word_count"],
        reverse=True,
    )
    thinnest_support_articles = sorted(support_articles, key=lambda page: page["word_count"])[:20]

    reasons = [
        "The site has broad barcode coverage, but a large share of the root taxonomy is generator-intent rather than deep editorial content.",
        "Only a small set of editorial pages exceed 1,000 words, so many topic branches exist without full depth beneath them.",
    ]
    if thin_sections:
        thin_list = ", ".join(item["section"] for item in thin_sections)
        reasons.append(
            "Several support-content sections are still shallow, especially: " + thin_list + "."
        )

    return {
        "verdict": {
            "covers_100_percent_topical_authority": False,
            "overall_assessment": "broad coverage with shallow support depth",
            "reasons": reasons,
        },
        "content_mix": {
            "root_generator_pages": intent_counts.get("generator", 0),
            "guides_and_editorial_pages": len(editorial_pages),
            "legacy_redirect_pages": intent_counts.get("redirect", 0),
            "utility_pages": intent_counts.get("utility", 0),
            "substantial_editorial_pages_over_1000_words": len(editorial_over_1000),
        },
        "section_depth": section_stats,
        "thin_sections": thin_sections,
        "thinnest_support_articles": thinnest_support_articles,
        "strongest_editorial_pages": editorial_over_1000[:12],
        "recommended_pillars": TOPICAL_PILLARS,
    }


def build_similarity_clusters(pages, threshold):
    parent = {page["path"]: page["path"] for page in pages}

    def find(path):
        while parent[path] != path:
            parent[path] = parent[parent[path]]
            path = parent[path]
        return path

    def union(path_a, path_b):
        root_a = find(path_a)
        root_b = find(path_b)
        if root_a != root_b:
            parent[root_b] = root_a

    pairs = []
    for page_a, page_b in combinations(pages, 2):
        ratio = SequenceMatcher(None, page_a["text"], page_b["text"]).ratio()
        if ratio >= threshold:
            pairs.append(
                {
                    "path_a": page_a["path"],
                    "path_b": page_b["path"],
                    "similarity": round(ratio, 4),
                }
            )
            union(page_a["path"], page_b["path"])

    clusters = {}
    for page in pages:
        clusters.setdefault(find(page["path"]), []).append(page["path"])

    pairs.sort(key=lambda item: item["similarity"], reverse=True)
    sorted_clusters = sorted(
        [sorted(cluster) for cluster in clusters.values() if len(cluster) > 1],
        key=len,
        reverse=True,
    )
    return pairs, sorted_clusters


def normalized_generator_template(text):
    text = SEO_SECTION_RE.sub(" ", text)
    text = HERO_SECTION_RE.sub(" ", text, count=1)
    text = re.sub(r"<title>.*?</title>", "<title></title>", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(
        r'<meta name="description" content="[^"]*" ?/?>',
        '<meta name="description" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<meta name="keywords" content="[^"]*" ?/?>',
        '<meta name="keywords" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<meta property="og:title" content="[^"]*" ?/?>',
        '<meta property="og:title" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<meta property="og:description" content="[^"]*" ?/?>',
        '<meta property="og:description" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<meta property="og:url" content="[^"]*" ?/?>',
        '<meta property="og:url" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<meta name="twitter:title" content="[^"]*" ?/?>',
        '<meta name="twitter:title" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<meta name="twitter:description" content="[^"]*" ?/?>',
        '<meta name="twitter:description" content="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<link rel="canonical" href="[^"]+" ?/?>',
        '<link rel="canonical" href="">',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"<h1[^>]*>.*?</h1>", "<h1></h1>", text, count=1, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", strip_html(text)).strip()


def audit_duplication(html_files):
    generator_pages = []
    editorial_pages = []

    for absolute_path in html_files:
        rel = os.path.relpath(absolute_path, ROOT).replace("\\", "/")
        raw_text = read_file(absolute_path)
        intent = page_intent(rel, raw_text)
        if intent == "generator":
            text = normalized_generator_template(raw_text)
        else:
            text = normalized_visible_text(raw_text)
        page = {"path": rel, "intent": intent, "text": text}

        if intent == "generator":
            generator_pages.append(page)
        elif intent in {"guide", "pillar_hub", "section_hub", "support_article"}:
            editorial_pages.append(page)

    generator_pairs, generator_clusters = build_similarity_clusters(generator_pages, 0.95)
    editorial_pairs, editorial_clusters = build_similarity_clusters(editorial_pages, 0.9)

    reasons = []
    if generator_pairs:
        reasons.append(
            "Generator pages contain large near-duplicate clusters, which creates programmatic-page duplication risk."
        )
    if editorial_pairs:
        reasons.append(
            "A few editorial pages are also highly similar, which suggests some non-generator content is overlapping too closely."
        )

    return {
        "verdict": {
            "has_no_meaningful_duplication": not generator_pairs and not editorial_pairs,
            "overall_assessment": "high duplication risk" if generator_pairs or editorial_pairs else "low duplication risk",
            "reasons": reasons,
        },
        "generator_similarity": {
            "pages_checked": len(generator_pages),
            "near_duplicate_threshold": 0.95,
            "near_duplicate_pair_count": len(generator_pairs),
            "cluster_count": len(generator_clusters),
            "largest_clusters": generator_clusters[:10],
            "sample_pairs": generator_pairs[:25],
        },
        "editorial_similarity": {
            "pages_checked": len(editorial_pages),
            "near_duplicate_threshold": 0.9,
            "near_duplicate_pair_count": len(editorial_pairs),
            "clusters": editorial_clusters[:10],
            "sample_pairs": editorial_pairs[:25],
        },
    }


def render_topical_authority_report(report):
    topical = report["topical_authority"]
    duplication = report["duplication_audit"]
    summary = report["summary"]
    content_mix = topical["content_mix"]
    thin_sections = topical["thin_sections"]
    thinnest_articles = topical["thinnest_support_articles"][:5]
    strongest_pages = topical["strongest_editorial_pages"][:6]
    recommended_pillars = topical["recommended_pillars"][:4]
    verdict = topical["verdict"]
    dup_verdict = duplication["verdict"]
    generator_similarity = duplication["generator_similarity"]
    editorial_similarity = duplication["editorial_similarity"]
    metadata = report["metadata_audit"]

    lines = [
        "# Topical Authority Audit",
        "",
        "## Verdict",
    ]

    if verdict["covers_100_percent_topical_authority"]:
        lines.append("The site currently covers 100% topical authority for the audited barcode scope.")
    else:
        lines.append("The site does not yet cover 100% topical authority for the audited barcode scope.")

    if dup_verdict["has_no_meaningful_duplication"]:
        lines.append(
            "Content quality has improved materially: no thin support sections were detected and the duplication audit currently passes."
        )
    else:
        lines.append(
            "Content quality has improved materially on thin pages, but the generator layer still has major structural duplication."
        )
    lines.extend(
        [
            "",
            "## Audit Signals",
            f"- `{summary['html_pages_checked']}` HTML pages were audited.",
            f"- `{content_mix['root_generator_pages']}` root pages are generator-intent pages.",
            f"- `{content_mix['guides_and_editorial_pages']}` pages count as guides or editorial/supporting content.",
            f"- `{content_mix['legacy_redirect_pages']}` pages are legacy redirects and `{content_mix['utility_pages']}` are utility pages.",
            f"- `{content_mix['substantial_editorial_pages_over_1000_words']}` editorial pages exceed `1,000` words.",
            f"- Generator duplication audit: `{generator_similarity['near_duplicate_pair_count']}` near-duplicate pairs across `{generator_similarity['pages_checked']}` pages.",
            f"- Editorial duplication audit: `{editorial_similarity['near_duplicate_pair_count']}` near-duplicate pairs across `{editorial_similarity['pages_checked']}` pages.",
            "",
            "## Thin Content",
        ]
    )

    if thin_sections:
        for section in thin_sections:
            thin_count = int(round(section["thin_support_share_under_300_words"] * section["support_article_count"]))
            lines.append(
                f"- `{section['section']}`: `{thin_count}/{section['support_article_count']}` support articles remain under `300` words."
            )
    else:
        lines.append("- No section currently exceeds the thin-support threshold.")

    if thinnest_articles:
        lines.append("- The current shortest support pages are:")
        for article in thinnest_articles:
            lines.append(
                f"  - `{article['path']}` at `{article['word_count']}` words."
            )

    lines.extend(
        [
            "",
            "## Structural Signals",
            f"- Pages with mismatched `og:url`: `{len(metadata['og_url_mismatches'])}`.",
            f"- Pages with empty `<h1>` tags: `{len(metadata['empty_h1_pages'])}`.",
            f"- Pages containing empty internal anchors: `{len(metadata['pages_with_empty_anchors'])}`.",
            f"- Pages still missing `hreflang`: `{len(metadata['missing_hreflang_pages'])}`.",
        ]
    )

    lines.extend(
        [
            "",
            "## Duplication",
            f"- The site {'passes' if dup_verdict['has_no_meaningful_duplication'] else 'does not pass'} the no-meaningful-duplication audit.",
            f"- Generator duplicate clusters: `{generator_similarity['cluster_count']}`.",
            f"- Editorial duplicate clusters: `{len(editorial_similarity['clusters'])}`.",
        ]
    )

    if dup_verdict["reasons"]:
        lines.append("- Remaining duplication notes:")
        for reason in dup_verdict["reasons"]:
            lines.append(f"  - {reason}")

    lines.extend(
        [
            "",
            "## Remaining Authority Gaps",
        ]
    )
    for reason in verdict["reasons"]:
        lines.append(f"- {reason}")

    lines.extend(
        [
            "",
            "## Strongest Editorial Assets",
        ]
    )
    for page in strongest_pages:
        lines.append(f"- `{page['path']}` ({page['word_count']} words)")

    lines.extend(
        [
            "",
            "## Recommended Next Pillars",
        ]
    )
    for pillar in recommended_pillars:
        lines.append(f"- `{pillar['name']}` (`{pillar['status']}`)")
        if pillar["gaps"]:
            lines.append(f"  - Next gap to cover: {pillar['gaps'][0]}")

    return "\n".join(lines) + "\n"


def main():
    html_files = list_html_files()
    broken_links, missing_titles, unlabeled_inputs = check_internal_links(html_files)
    metadata_audit = audit_metadata_and_navigation(html_files)
    report = {
        "summary": {
            "html_pages_checked": len(html_files),
            "broken_internal_link_count": len(broken_links),
            "missing_title_count": len(missing_titles),
            "pages_with_unlabeled_inputs": len(unlabeled_inputs),
            "og_url_mismatch_count": len(metadata_audit["og_url_mismatches"]),
            "pages_with_empty_h1": len(metadata_audit["empty_h1_pages"]),
            "pages_with_empty_anchors": len(metadata_audit["pages_with_empty_anchors"]),
            "pages_missing_hreflang": len(metadata_audit["missing_hreflang_pages"]),
        },
        "broken_internal_links": broken_links,
        "missing_titles": missing_titles,
        "unlabeled_inputs": unlabeled_inputs,
        "metadata_audit": metadata_audit,
        "pillar_audit": audit_pillars(),
        "technical_truths": audit_technical_truths(),
        "asset_checks": audit_assets(),
        "legacy_redirects": audit_legacy_redirects(),
        "topical_authority": audit_topical_authority(html_files),
        "duplication_audit": audit_duplication(html_files),
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    with open(TOPICAL_REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write(render_topical_authority_report(report))

    print("WROTE", os.path.relpath(REPORT_PATH, ROOT))
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
