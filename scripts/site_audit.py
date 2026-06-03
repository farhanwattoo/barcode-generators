import json
import os
import re
from html import unescape


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(ROOT, "reports")
REPORT_PATH = os.path.join(REPORT_DIR, "site_audit.json")

PLACEHOLDER_MARKERS = [
    "placeholder",
    "coming soon",
    "section content goes here",
    "to be added",
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
SCRIPT_JSON_RE = re.compile(
    r'<script[^>]*type\s*=\s*"application/ld\+json"[^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
IMG_RASTER_RE = re.compile(r'<img[^>]+src\s*=\s*"[^"]+\.(png|jpe?g)"', re.IGNORECASE)


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


def main():
    html_files = list_html_files()
    broken_links, missing_titles, unlabeled_inputs = check_internal_links(html_files)
    report = {
        "summary": {
            "html_pages_checked": len(html_files),
            "broken_internal_link_count": len(broken_links),
            "missing_title_count": len(missing_titles),
            "pages_with_unlabeled_inputs": len(unlabeled_inputs),
        },
        "broken_internal_links": broken_links,
        "missing_titles": missing_titles,
        "unlabeled_inputs": unlabeled_inputs,
        "pillar_audit": audit_pillars(),
        "technical_truths": audit_technical_truths(),
        "asset_checks": audit_assets(),
        "legacy_redirects": audit_legacy_redirects(),
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("WROTE", os.path.relpath(REPORT_PATH, ROOT))
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
