from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_RE = re.compile(r'(<link rel="canonical" href=")([^"]+)(" ?/?>)', re.IGNORECASE)
OG_URL_RE = re.compile(r'(<meta property="og:url" content=")([^"]+)(" ?/?>)', re.IGNORECASE)
TITLE_RE = re.compile(r"(<title>)(.*?)(</title>)", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"(<h1[^>]*>)(.*?)(</h1>)", re.IGNORECASE | re.DOTALL)
HERO_P_RE = re.compile(
    r'(<section class="hero-section">\s*<h1[^>]*>.*?</h1>\s*<p>)(.*?)(</p>)',
    re.IGNORECASE | re.DOTALL,
)

META_PATTERNS = {
    "description": re.compile(r'(<meta name="description" content=")([^"]*)(" ?/?>)', re.IGNORECASE),
    "keywords": re.compile(r'(<meta name="keywords" content=")([^"]*)(" ?/?>)', re.IGNORECASE),
    "og:title": re.compile(r'(<meta property="og:title" content=")([^"]*)(" ?/?>)', re.IGNORECASE),
    "og:description": re.compile(r'(<meta property="og:description" content=")([^"]*)(" ?/?>)', re.IGNORECASE),
    "twitter:title": re.compile(r'(<meta name="twitter:title" content=")([^"]*)(" ?/?>)', re.IGNORECASE),
    "twitter:description": re.compile(r'(<meta name="twitter:description" content=")([^"]*)(" ?/?>)', re.IGNORECASE),
}

EMPTY_LINKS = {
    '<a href="/code128-vs-code39.html"></a>': '<a href="/code128-vs-code39.html">Code 128とCode 39の違い</a>',
    '<a href="/what-is-barcode.html"></a>': '<a href="/what-is-barcode.html">バーコードとは？</a>',
    '<a href="/how-to-create-barcode.html"></a>': '<a href="/how-to-create-barcode.html">バーコードの作り方</a>',
    '<a href="/barcode-size-guide.html"></a>': '<a href="/barcode-size-guide.html">バーコードサイズガイド</a>',
    '<a href="/barcode-format-guide.html"></a>': '<a href="/barcode-format-guide.html">バーコード形式ガイド</a>',
    '<a href="/barcode-use-cases.html"></a>': '<a href="/barcode-use-cases.html">バーコードの活用事例</a>',
}

BROKEN_HERO_COPY = "エンタープライズ品質の鮮明なレンダリング。に対応し、一括A4印刷やベクターデータのエクスポートがブラウザ上で完結します。"

PAGE_FIXES = {
    "barcode-size-guide.html": {
        "title": "【2026年版】バーコードサイズガイド | X寸法・クワイエットゾーン・印刷サイズの決め方",
        "description": "バーコードのサイズ設計を解説。X寸法、クワイエットゾーン、印刷解像度、読取距離を踏まえた適切なサイズの決め方をまとめた実務ガイドです。",
        "keywords": "バーコード サイズ, バーコード サイズガイド, X寸法, クワイエットゾーン, バーコード 印刷",
        "h1": "バーコードサイズガイド",
        "hero": "X寸法、クワイエットゾーン、印刷解像度、読取距離を踏まえたバーコードサイズ設計の実務ガイドです。",
    },
    "code128-vs-code39.html": {
        "title": "【2026年版】Code 128とCode 39の違い | 密度・文字種・ラベル幅の比較ガイド",
        "description": "Code 128とCode 39の違いを比較。データ密度、対応文字、ラベル幅、既存スキャナ環境の観点から選び方を整理した実務ガイドです。",
        "keywords": "Code 128 Code 39 違い, Code 128 比較, Code 39 比較, バーコード 比較, ラベル幅",
        "h1": "Code 128とCode 39の違い",
        "hero": "データ密度、対応文字、ラベル幅、既存スキャナ環境の違いからCode 128とCode 39の選び方を整理した比較ガイドです。",
    },
    "ean-vs-upc.html": {
        "title": "【2026年版】EANとUPCの違い | 小売流通・地域要件・商品コード設計の比較",
        "description": "EANとUPCの違いを比較。販売地域、GTIN運用、パッケージ設計、小売POSの要件を踏まえた選び方を解説します。",
        "keywords": "EAN UPC 違い, EAN UPC 比較, GTIN, 小売 バーコード, JANコード",
        "h1": "EANとUPCの違い",
        "hero": "販売地域、GTIN運用、パッケージ設計、小売POS要件の違いからEANとUPCの選び方を整理した比較ガイドです。",
    },
}


def replace_match(text, pattern, value):
    match = pattern.search(text)
    if not match:
        return text
    return text[: match.start()] + match.group(1) + value + match.group(3) + text[match.end() :]


def update_og_url(text):
    canonical_match = CANONICAL_RE.search(text)
    og_match = OG_URL_RE.search(text)
    if not canonical_match or not og_match:
        return text
    canonical = canonical_match.group(2)
    if og_match.group(2) == canonical:
        return text
    return text[: og_match.start()] + og_match.group(1) + canonical + og_match.group(3) + text[og_match.end() :]


def update_empty_links(text):
    for old, new in EMPTY_LINKS.items():
        text = text.replace(old, new)
    return text


def update_page_fix(rel_path, text):
    fix = PAGE_FIXES.get(rel_path)
    if not fix:
        return text

    text = replace_match(text, TITLE_RE, fix["title"])
    text = replace_match(text, H1_RE, fix["h1"])
    text = replace_match(text, HERO_P_RE, fix["hero"])

    text = replace_match(text, META_PATTERNS["description"], fix["description"])
    text = replace_match(text, META_PATTERNS["keywords"], fix["keywords"])
    text = replace_match(text, META_PATTERNS["og:title"], fix["title"])
    text = replace_match(text, META_PATTERNS["og:description"], fix["description"])
    text = replace_match(text, META_PATTERNS["twitter:title"], fix["title"])
    text = replace_match(text, META_PATTERNS["twitter:description"], fix["description"])
    return text


def update_broken_hero(text):
    if BROKEN_HERO_COPY not in text:
        return text
    h1_match = H1_RE.search(text)
    if not h1_match:
        return text
    h1_text = re.sub(r"<[^>]+>", "", h1_match.group(2)).strip()
    if not h1_text:
        return text
    hero = f"{h1_text}の作成・一括A4印刷・PNG/SVG/PDF出力をブラウザだけで完結できるオンラインツールです。"
    return replace_match(text, HERO_P_RE, hero)


def main():
    changed_files = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        updated = text
        updated = update_og_url(updated)
        updated = update_empty_links(updated)
        updated = update_page_fix(rel, updated)
        updated = update_broken_hero(updated)

        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_files.append(rel)

    print(f"Updated {len(changed_files)} HTML files.")
    for rel in changed_files[:50]:
        print(rel)


if __name__ == "__main__":
    main()
