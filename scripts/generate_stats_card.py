#!/usr/bin/env python3
"""GitHub 통계 카드 자체 제작기 (정적 스냅샷 버전).

GitHub REST API(공개, 인증 불필요)로 리포지토리 수 · 총 스타 · 팔로워 ·
언어 비중을 가져와 stats/stats-card.svg 를 굽는다.

※ github-readme-stats처럼 "볼 때마다 실시간 갱신"되게 하려면 매 요청마다
   SVG를 만들어주는 서버(Vercel 서버리스 함수 등)가 배포되어 있어야 한다.
   이 스크립트는 그 전 단계로, 실행 시점의 스냅샷을 정적 파일로 굽는다.
   최신 상태를 유지하려면 종종 재실행 후 커밋하면 된다.

실행: python3 scripts/generate_stats_card.py <github-username>
"""
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "stats" / "stats-card.svg"
FONT = "Pretendard, -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif"

LANG_COLOR = {
    "Java": "#EC8B2F", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6", "Python": "#3776AB",
    "HTML": "#E34F26", "CSS": "#1572B6", "Vue": "#4FC08D", "Kotlin": "#7F52FF",
    "C": "#A8B9CC", "C++": "#00599C", "Go": "#00ADD8", "Shell": "#89e051",
    "Dockerfile": "#2496ED",
}


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}",
                                  headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def fetch(username):
    user = api(f"/users/{username}")
    repos = []
    page = 1
    while True:
        batch = api(f"/users/{username}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos += batch
        page += 1

    total_stars = sum(r["stargazers_count"] for r in repos)
    langs = Counter(r["language"] for r in repos if r["language"])
    top_langs = langs.most_common(5)
    total_lang = sum(c for _l, c in top_langs) or 1

    return {
        "name": user.get("name") or username,
        "username": username,
        "public_repos": user["public_repos"],
        "followers": user["followers"],
        "total_stars": total_stars,
        "top_langs": [(lang, count / total_lang) for lang, count in top_langs],
    }


def stat_block(x, label, value):
    return f'''  <g transform="translate({x},0)">
    <text x="0" y="0" font-size="26" font-weight="700" fill="#e6edf3">{value}</text>
    <text x="0" y="20" font-size="12" fill="#8b949e">{label}</text>
  </g>'''


def lang_bar(langs):
    segs = []
    x = 0
    width = 732
    for i, (lang, ratio) in enumerate(langs):
        w = ratio * width
        color = LANG_COLOR.get(lang, "#8b949e")
        segs.append(f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="8" fill="{color}"/>')
        x += w
    bar = "".join(segs)

    legend = []
    lx = 0
    for lang, ratio in langs:
        color = LANG_COLOR.get(lang, "#8b949e")
        pct = round(ratio * 100)
        label = f"{lang} {pct}%"
        legend.append(
            f'<circle cx="{lx+4}" cy="4" r="4" fill="{color}"/>'
            f'<text x="{lx+14}" y="8" font-size="12" fill="#c9d1d9">{label}</text>'
        )
        lx += 16 + len(label) * 6.6 + 18
    return bar, "".join(legend)


def build(data):
    bar, legend = lang_bar(data["top_langs"])
    svg = f'''<svg viewBox="0 0 820 220" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">
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
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.32"/>
    </filter>
  </defs>

  <g filter="url(#shadow)">
    <rect x="10" y="8" width="800" height="204" rx="12" fill="#0d1117" stroke="url(#border)"/>
  </g>

  <text x="44" y="46" font-size="18" font-weight="700" fill="#e6edf3">GitHub Stats</text>
  <text x="776" y="45" text-anchor="end" font-size="12" fill="#8b949e">@{data['username']}</text>
  <rect x="44" y="56" height="2" rx="1" fill="url(#accent)" width="0">
    <animate attributeName="width" begin="0.2s" dur="0.6s" values="0;96" fill="freeze"/>
  </rect>

  <g transform="translate(44,102)">
{stat_block(0, "Public Repos", data["public_repos"])}
{stat_block(180, "Followers", data["followers"])}
{stat_block(340, "Total Stars", data["total_stars"])}
  </g>

  <text x="44" y="152" font-size="12" letter-spacing="1" fill="#8b949e">TOP LANGUAGES</text>
  <g transform="translate(44,164)">
    <rect x="0" y="0" width="732" height="8" rx="4" fill="#21262d"/>
    <g style="clip-path:inset(0 round 4px)">{bar}</g>
  </g>
  <g transform="translate(44,192)">{legend}</g>
</svg>
'''
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(svg)
    print(f"stats/stats-card.svg 생성 ({data['username']} 스냅샷)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 scripts/generate_stats_card.py <github-username>")
        sys.exit(1)
    build(fetch(sys.argv[1]))
