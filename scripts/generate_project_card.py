#!/usr/bin/env python3
"""프로젝트 소개 카드 SVG 생성기.

PROJECTS 리스트에 프로젝트를 추가하면 projects/cards/<slug>.svg 배너가 생성된다.
카드는 제목·기간·역할·한줄소개·스택 로고까지만 담고, ERD/아키텍처/트러블슈팅처럼
분량이 긴 내용은 마크다운의 <details> 접기 블록에 작성한다.
(SVG는 <img>로 삽입되는 순간 클릭 인터랙션이 죽기 때문에, 카드 안에는
 "자세히 보기" 같은 가짜 링크를 넣지 않는다 — 실제 펼치기 버튼은
 카드 아래의 <details> 태그가 담당한다.)

실행: python3 scripts/generate_project_card.py
"""
import re
from pathlib import Path

from textwidth import text_width as _text_width

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "scripts" / "icons"
OUT = ROOT / "projects" / "cards"

FONT = "Pretendard, -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif"
BRAND = {
    "python": "#3776AB", "openjdk": "#EC8B2F", "javascript": "#F7DF1E", "typescript": "#3178C6",
    "react": "#61DAFB", "nextdotjs": "#FFFFFF", "vuedotjs": "#4FC08D", "vite": "#8a90ff",
    "springboot": "#6DB33F", "springsecurity": "#6DB33F", "hibernate": "#BC85E3",
    "jsonwebtokens": "#FFFFFF", "nodedotjs": "#5FA04E", "express": "#FFFFFF", "django": "#44B78B",
    "fastapi": "#1fb8a6", "mysql": "#6cb6ff", "postgresql": "#7a9bff", "mongodb": "#47A248",
    "redis": "#FF4438", "docker": "#2496ED", "amazonwebservices": "#FF9900", "vercel": "#FFFFFF",
    "githubactions": "#2088FF", "supabase": "#3FCF8E", "kubernetes": "#5f8ff5", "nginx": "#2fc06a",
    "prometheus": "#E6522C", "grafana": "#F46800", "cloudinary": "#3448C5",
}

# 프로젝트 하나 = (slug, 제목, 기간, 역할, 한줄소개, [스택 아이콘 slug...])
PROJECTS = [
    (
        "example",
        "프로젝트명을 입력하세요",
        "2026.01 – 2026.03",
        "백엔드 · 담당 영역을 적으세요",
        "이 프로젝트가 어떤 문제를 어떻게 해결했는지 한 줄로 요약하세요",
        ["openjdk", "springboot", "mysql", "docker"],
    ),
    (
        "scommit",
        "SCommit — 개발자 지식 공유 구독 플랫폼",
        "2026.06 – 2026.07",
        "백엔드 · 포스트/댓글/검색, 성능 테스트(k6)·모니터링 담당",
        "구독 등급별 콘텐츠 접근 제어와 SSE 실시간 알림을 제공하는 지식 공유 플랫폼으로, "
        "k6 부하 테스트로 좋아요 API의 DB 락 경합을 규명(p95 529ms→2.5s, 약 5배 저하)하고 개선 방향을 도출함",
        ["openjdk", "springboot", "mysql", "hibernate", "springsecurity",
         "jsonwebtokens", "nextdotjs", "docker", "prometheus", "grafana"],
    ),
]

LINE_H = 19
CARD_CONTENT_WIDTH = 732  # x=44 ~ x=776, 설명 텍스트가 채울 수 있는 최대 폭


def icon_path(slug):
    svg = (ICONS / f"{slug}.svg").read_text()
    return re.search(r'<path d="([^"]+)"', svg).group(1)


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, max_width=CARD_CONTENT_WIDTH):
    """실제 렌더링 폭 기준으로 줄바꿈 — 카드 가로 폭을 최대한 채우고,
    넘칠 때만 다음 줄로 넘어간다 (왼쪽에 짧게 몰리는 것 방지)."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        candidate = f"{cur} {w}".strip()
        if _text_width(candidate, 13) > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = candidate
    if cur:
        lines.append(cur)
    return lines


def build(slug, title, period, role, desc, stack):
    desc_lines = wrap(desc)
    desc_y0 = 92
    desc_tspans = "".join(
        f'<tspan x="44" y="{desc_y0 + i * LINE_H}">{escape(line)}</tspan>'
        for i, line in enumerate(desc_lines)
    )

    accent_y = desc_y0 + (len(desc_lines) - 1) * LINE_H + 20
    icon_y = accent_y + 24
    icon_size = 20
    card_bottom = icon_y + icon_size + 22
    svg_h = card_bottom + 8

    icons = []
    x = 44
    for s in stack:
        color = BRAND.get(s, "#8b949e")
        icons.append(
            f'    <g transform="translate({x},{icon_y}) scale({icon_size/24:.4f})">'
            f'<path d="{icon_path(s)}" fill="{color}"/></g>'
        )
        x += 30

    svg = f'''<svg viewBox="0 0 820 {svg_h}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">
  <defs>
    <linearGradient id="accent-{slug}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#79c0ff"/>
      <stop offset="100%" stop-color="#d2a8ff"/>
    </linearGradient>
    <linearGradient id="border-{slug}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#30363d"/>
      <stop offset="50%" stop-color="#58a6ff" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#30363d"/>
    </linearGradient>
    <filter id="shadow-{slug}" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.32"/>
    </filter>
  </defs>

  <g filter="url(#shadow-{slug})">
    <rect x="10" y="8" width="800" height="{card_bottom - 8}" rx="12" fill="#0d1117" stroke="url(#border-{slug})"/>
  </g>

  <text x="44" y="46" font-size="20" font-weight="700" fill="#e6edf3">{escape(title)}</text>
  <text x="776" y="45" text-anchor="end" font-size="12" fill="#8b949e">{escape(period)}</text>

  <text x="44" y="68" font-size="12" font-weight="600" letter-spacing="1" fill="#79c0ff">{escape(role)}</text>

  <text font-size="13" fill="#c9d1d9">{desc_tspans}</text>

  <rect x="44" y="{accent_y}" height="2" rx="1" fill="url(#accent-{slug})" width="0">
    <animate attributeName="width" begin="0.2s" dur="0.5s" values="0;732" fill="freeze"/>
  </rect>

{chr(10).join(icons)}
</svg>
'''
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.svg").write_text(svg)
    print(f"projects/cards/{slug}.svg 생성 ({svg_h}px)")


if __name__ == "__main__":
    for p in PROJECTS:
        build(*p)
