#!/usr/bin/env python3
"""로고 포함 기술스택 카드 생성기.

stack/stack-card.svg(점 방식)와 별개로, 칩 안에 simple-icons 로고가 들어간
stack/stack-card-logos.svg 를 만든다. 실행: python3 scripts/generate_stack_card.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "scripts" / "icons"
OUT = ROOT / "stack" / "stack-card-logos.svg"

# 행: (카테고리 라벨, [(slug, 표기명, 다크 배경 기준 색)])
ROWS = [
    ("FRONTEND", [
        ("react",           "React",       "#61DAFB"),
        ("javascript",      "JavaScript",  "#F7DF1E"),
        ("vite",            "Vite",        "#8a90ff"),
    ]),
    ("BACKEND", [
        ("openjdk",         "Java",        "#EC8B2F"),
        ("springboot",      "Spring Boot", "#6DB33F"),
        ("hibernate",       "JPA",         "#BC85E3"),
    ]),
    ("DATABASE", [
        ("mysql",           "MySQL",       "#6cb6ff"),
        ("postgresql",      "PostgreSQL",  "#7a9bff"),
        ("supabase",        "Supabase",    "#3FCF8E"),
    ]),
    ("INFRA·TOOLS", [
        ("docker",          "Docker",      "#2496ED"),
        ("vercel",          "Vercel",      "#FFFFFF"),
        ("git",             "Git",         "#F05032"),
        ("googleanalytics", "GA4",         "#E37400"),
    ]),
]

FONT = "Pretendard, -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif"
CHIP_H, CHIP_LOGO, CHIP_FS = 28, 14, 13
PAD_L, GAP, PAD_R, CHIP_GAP = 11, 7, 12, 10
CHIPS_X = 170          # 모든 행의 칩 시작 기준선
ROW_Y = [76, 128, 180, 232]
NARROW = set("ijltf.r ")


def text_width(label):
    return round(sum(0.55 if ch in NARROW else 1.0 for ch in label) * 7.6)


def icon_path(slug):
    svg = (ICONS / f"{slug}.svg").read_text()
    return re.search(r'<path d="([^"]+)"', svg).group(1)


def chip(x, y, slug, label, color):
    w = PAD_L + CHIP_LOGO + GAP + text_width(label) + PAD_R
    ly = y + (CHIP_H - CHIP_LOGO) // 2
    baseline = y + 19
    body = f'''      <rect x="{x}" y="{y}" width="{w}" height="{CHIP_H}" rx="{CHIP_H // 2}" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-opacity="0.5"/>
      <g transform="translate({x + PAD_L},{ly}) scale({CHIP_LOGO / 24:.4f})"><path d="{icon_path(slug)}" fill="{color}"/></g>
      <text x="{x + PAD_L + CHIP_LOGO + GAP}" y="{baseline}">{label}</text>'''
    return body, w


def build():
    parts = [f'''<svg viewBox="0 0 900 310" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">
  <defs>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#79c0ff"/>
      <stop offset="100%" stop-color="#d2a8ff"/>
    </linearGradient>
    <linearGradient id="border" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#30363d"/>
      <stop offset="50%" stop-color="#58a6ff" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#30363d"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>

  <g filter="url(#softShadow)">
    <rect x="20" y="14" width="860" height="282" rx="12" fill="#0d1117" stroke="url(#border)"/>
  </g>

  <text x="44" y="48" font-size="18" font-weight="700" fill="#e6edf3">Tech Stack</text>
  <rect x="44" y="56" height="3" rx="1.5" fill="url(#accent)" width="0">
    <animate attributeName="width" begin="0.2s" dur="0.6s" values="0;96" fill="freeze"/>
  </rect>

  <line x1="158" y1="72" x2="158" y2="272" stroke="#21262d"/>''']

    for i, (category, chips) in enumerate(ROWS):
        y = ROW_Y[i]
        begin = 0.4 + i * 0.3
        rows = []
        x = CHIPS_X
        for slug, label, color in chips:
            body, w = chip(x, y, slug, label, color)
            rows.append(body)
            x += w + CHIP_GAP
        parts.append(f'''
  <g opacity="0">
    <animate attributeName="opacity" begin="{begin}s" dur="0.5s" values="0;1" fill="freeze"/>
    <text x="44" y="{y + 19}" font-size="12" letter-spacing="2" fill="#8b949e">{category}</text>
    <g font-size="{CHIP_FS}" font-weight="600" fill="#e6edf3">
{chr(10).join(rows)}
    </g>
  </g>''')

    parts.append("</svg>\n")
    OUT.write_text("".join(parts))
    print(f"{OUT.relative_to(ROOT)} 생성")


if __name__ == "__main__":
    build()
