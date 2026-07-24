#!/usr/bin/env python3
"""개별 기술 뱃지 SVG 생성기.

scripts/icons/ 의 simple-icons(CC0) 로고 패스를 읽어
badges/dark/<slug>.svg, badges/clean/<slug>.svg 두 스타일과
갤러리 문서(badges/README.md)를 만든다.
실행: python3 scripts/generate_badges.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "scripts" / "icons"
OUT = ROOT / "badges"

# 카테고리별 (아이콘 slug, 표기 이름, 브랜드 컬러, 다크 배경용 보정색 — 어둡거나 검정인 브랜드만)
CATEGORIES = [
    ("Language", [
        ("python",            "Python",         "#3776AB", "#5da9e8"),
        ("c",                 "C",              "#A8B9CC", None),
        ("cplusplus",         "C++",            "#00599C", "#4a9fe0"),
        ("openjdk",           "Java",           "#EC8B2F", None),
        ("kotlin",            "Kotlin",         "#7F52FF", "#9d7bff"),
        ("javascript",        "JavaScript",     "#F7DF1E", None),
        ("typescript",        "TypeScript",     "#3178C6", "#5f9ee8"),
        ("go",                "Go",             "#00ADD8", None),
        ("rust",              "Rust",           "#000000", "#FFFFFF"),
        ("ruby",              "Ruby",           "#CC342D", None),
        ("swift",             "Swift",          "#F05138", None),
        ("dart",              "Dart",           "#0175C2", "#40a8e8"),
        ("php",               "PHP",            "#777BB4", None),
    ]),
    ("Frontend", [
        ("html5",             "HTML5",          "#E34F26", None),
        ("css3",              "CSS3",           "#1572B6", "#4a9fe0"),
        ("react",             "React",          "#61DAFB", None),
        ("nextdotjs",         "Next.js",        "#000000", "#FFFFFF"),
        ("vuedotjs",          "Vue.js",         "#4FC08D", None),
        ("angular",           "Angular",        "#0F0F11", "#FFFFFF"),
        ("svelte",            "Svelte",         "#FF3E00", None),
        ("vite",              "Vite",           "#646CFF", "#8a90ff"),
        ("tailwindcss",       "Tailwind CSS",   "#06B6D4", None),
        ("bootstrap",         "Bootstrap",      "#7952B3", "#9d78d2"),
        ("sass",              "Sass",           "#CC6699", None),
        ("redux",             "Redux",          "#764ABC", "#9a72d8"),
        ("jquery",            "jQuery",         "#0769AD", "#3fa0dc"),
    ]),
    ("Backend / Framework", [
        ("springboot",        "Spring Boot",    "#6DB33F", None),
        ("hibernate",         "Hibernate",      "#59666C", "#BC85E3"),
        ("nodedotjs",         "Node.js",        "#5FA04E", None),
        ("express",           "Express",        "#000000", "#FFFFFF"),
        ("nestjs",            "NestJS",         "#E0234E", None),
        ("django",            "Django",         "#092E20", "#44B78B"),
        ("flask",             "Flask",          "#000000", "#FFFFFF"),
        ("fastapi",           "FastAPI",        "#009688", "#1fb8a6"),
        ("laravel",           "Laravel",        "#FF2D20", None),
        ("dotnet",            ".NET",           "#512BD4", "#7a5cf0"),
        ("graphql",           "GraphQL",        "#E10098", None),
        ("socketdotio",       "Socket.io",      "#010101", "#FFFFFF"),
        ("jsonwebtokens",     "JWT",            "#000000", "#FFFFFF"),
        ("apachekafka",       "Apache Kafka",   "#231F20", "#FFFFFF"),
        ("rabbitmq",          "RabbitMQ",       "#FF6600", None),
        ("apachetomcat",      "Apache Tomcat",  "#F8DC75", None),
        ("gradle",            "Gradle",         "#02303A", "#6fd8c0"),
        ("nginx",             "Nginx",          "#009639", "#2fc06a"),
    ]),
    ("Mobile", [
        ("flutter",           "Flutter",        "#02569B", "#54C5F8"),
        ("android",           "Android",        "#3DDC84", None),
    ]),
    ("Database", [
        ("mysql",             "MySQL",          "#4479A1", "#6cb6ff"),
        ("postgresql",        "PostgreSQL",     "#4169E1", "#7a9bff"),
        ("mongodb",           "MongoDB",        "#47A248", None),
        ("redis",             "Redis",          "#FF4438", None),
        ("mariadb",           "MariaDB",        "#003545", "#5fd0c0"),
        ("sqlite",            "SQLite",         "#003B57", "#6cb6ff"),
        ("firebase",          "Firebase",       "#DD2C00", "#FFA000"),
        ("elasticsearch",     "Elasticsearch",  "#005571", "#35bcd0"),
        ("supabase",          "Supabase",       "#3FCF8E", None),
    ]),
    ("Infra / DevOps", [
        ("docker",            "Docker",         "#2496ED", None),
        ("kubernetes",        "Kubernetes",     "#326CE5", "#5f8ff5"),
        ("amazonwebservices", "AWS",            "#232F3E", "#FF9900"),
        ("googlecloud",       "Google Cloud",   "#4285F4", None),
        ("vercel",            "Vercel",         "#000000", "#FFFFFF"),
        ("netlify",           "Netlify",        "#00C7B7", None),
        ("cloudflare",        "Cloudflare",     "#F38020", None),
        ("ubuntu",            "Ubuntu",         "#E95420", None),
        ("linux",             "Linux",          "#FCC624", None),
        ("jenkins",           "Jenkins",        "#D24939", None),
        ("terraform",         "Terraform",      "#844FBA", "#a07be0"),
        ("grafana",           "Grafana",        "#F46800", None),
        ("prometheus",        "Prometheus",     "#E6522C", None),
        ("npm",               "npm",            "#CB3837", None),
        ("yarn",              "Yarn",           "#2C8EBB", None),
        ("pnpm",              "pnpm",           "#F69220", None),
        ("git",               "Git",            "#F05032", None),
        ("github",            "GitHub",         "#181717", "#FFFFFF"),
        ("githubactions",     "GitHub Actions", "#2088FF", None),
        ("gitlab",            "GitLab",         "#FC6D26", None),
    ]),
    ("Testing / API", [
        ("junit5",            "JUnit5",         "#25A162", None),
        ("pytest",            "pytest",         "#0A9EDC", None),
        ("k6",                "k6",             "#7D64FF", "#9d8bff"),
        ("swagger",           "Swagger",        "#85EA2D", None),
        ("postman",           "Postman",        "#FF6C37", None),
    ]),
    ("Tools / Collaboration", [
        ("intellijidea",      "IntelliJ IDEA",  "#000000", "#FFFFFF"),
        ("figma",             "Figma",          "#F24E1E", None),
        ("googleanalytics",   "GA4",            "#E37400", None),
        ("slack",             "Slack",          "#4A154B", "#e296f0"),
        ("notion",            "Notion",         "#000000", "#FFFFFF"),
        ("jira",              "Jira",           "#0052CC", "#4c8ff5"),
        ("confluence",        "Confluence",     "#172B4D", "#4c8ff5"),
        ("zoom",              "Zoom",           "#0B5CFF", None),
        ("discord",           "Discord",        "#5865F2", "#7289fa"),
    ]),
]

RAW_BASE = "https://raw.githubusercontent.com/Mungwani/README-assets/main/badges"

# 모든 뱃지 공통 규격: 높이 32 고정, 로고 16(24×24 정규화 박스 → 동일 스케일)
HEIGHT = 32
LOGO = 16
PAD_L, GAP, PAD_R = 10, 7, 11
BASELINE = 21  # 13px 텍스트를 높이 32 기준 세로 중앙에

# 폰트: Pretendard 우선(설치된 환경), 폴백은 동일 계열 시스템 산세리프.
# GitHub 이미지 프록시(camo)가 외부 폰트 로드를 차단하므로 웹폰트 @import는 불가.
FONT = "Pretendard, -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif"

# 스타일: 다크(포인트 강조) / 클린(밝은 배경·회색 테두리로 통일된 기업 문서 느낌)
STYLES = {
    "dark": {
        "font": FONT,
        "font_size": 13, "font_weight": 700, "letter_spacing": 0.2, "char_w": 7.6,
        "bg": "#0d1117", "text": "#e6edf3",
        # 테두리·틴트·로고 모두 브랜드 컬러(어두운 브랜드는 보정색)
        "brand_border": True, "tint_opacity": 0.08, "border_opacity": 0.55,
        "use_dark_fix": True,
    },
    "clean": {
        "font": FONT,
        "font_size": 13, "font_weight": 600, "letter_spacing": 0.2, "char_w": 7.4,
        "bg": "#ffffff", "text": "#24292f",
        # 테두리는 회색으로 통일, 색은 로고에만 (원래 브랜드 컬러 그대로)
        "brand_border": False, "border": "#d0d7de",
        "use_dark_fix": False,
    },
}

TEMPLATE = """<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg"
     font-family="{font}">
  <rect x="0.5" y="0.5" width="{iw}" height="{ih}" rx="8" fill="{bg}"/>
{tint}  <rect x="0.5" y="0.5" width="{iw}" height="{ih}" rx="8" fill="none"
        stroke="{border}"{border_op}/>
  <g transform="translate({lx},{ly}) scale({scale})">
    <path d="{path}" fill="{logo_color}"/>
  </g>
  <text x="{tx}" y="{baseline}" font-size="{fs}" font-weight="{fw}" letter-spacing="{ls}" fill="{text}">{label}</text>
</svg>
"""

NARROW = set("ijltf.r ")  # 폭이 좁은 글자는 절반 폭으로 계산해 오른쪽 여백을 핏하게


def text_width(label, char_w):
    units = sum(0.55 if ch in NARROW else 1.0 for ch in label)
    return round(units * char_w)


def icon_path(slug):
    svg = (ICONS / f"{slug}.svg").read_text()
    m = re.search(r'<path d="([^"]+)"', svg)
    if not m:
        raise ValueError(f"path not found in {slug}.svg")
    return m.group(1)


def build(style_name, style, slug, label, color, dark_fix):
    effective = (dark_fix or color) if style["use_dark_fix"] else color
    text_w = text_width(label, style["char_w"])
    w = PAD_L + LOGO + GAP + text_w + PAD_R

    if style["brand_border"]:
        border = effective
        border_op = f' stroke-opacity="{style["border_opacity"]}"'
        tint = (f'  <rect x="0.5" y="0.5" width="{w-1}" height="{HEIGHT-1}" rx="8"'
                f' fill="{effective}" fill-opacity="{style["tint_opacity"]}"/>\n')
    else:
        border = style["border"]
        border_op = ""
        tint = ""

    svg = TEMPLATE.format(
        w=w, h=HEIGHT, iw=w - 1, ih=HEIGHT - 1,
        font=style["font"], bg=style["bg"], tint=tint,
        border=border, border_op=border_op,
        lx=PAD_L, ly=(HEIGHT - LOGO) // 2, scale=LOGO / 24,
        path=icon_path(slug), logo_color=effective,
        baseline=BASELINE,
        tx=PAD_L + LOGO + GAP, fs=style["font_size"], fw=style["font_weight"],
        ls=style["letter_spacing"], text=style["text"], label=label,
    )
    out = OUT / style_name / f"{slug}.svg"
    out.write_text(svg)


def gen_gallery():
    """badges/README.md — 전체 뱃지 갤러리 문서를 생성한다."""
    total = sum(len(b) for _c, b in CATEGORIES)
    lines = [
        "# Badges",
        "",
        "<!-- 이 문서는 scripts/generate_badges.py 가 자동 생성합니다. 직접 수정하지 마세요. -->",
        "",
        f"개별 기술 뱃지 {total}종. `clean/`(밝은 문서 톤)과 `dark/`(GitHub 다크 톤) 두 스타일로 제공됩니다.",
        "",
        "사용할 뱃지의 마크다운을 그대로 복사해 README에 붙여넣으세요:",
        "",
        "```markdown",
        f"![Spring Boot]({RAW_BASE}/clean/springboot.svg)",
        "```",
        "",
    ]
    for category, badges in CATEGORIES:
        lines += [f"## {category}", "", "| 기술 | Clean | Dark | slug |", "|---|---|---|---|"]
        for slug, label, _color, _fix in badges:
            lines.append(
                f"| {label} | ![{label}](clean/{slug}.svg) | ![{label}](dark/{slug}.svg) | `{slug}` |"
            )
        lines.append("")
    lines += [
        "## 새 뱃지 추가하기",
        "",
        "1. [simpleicons.org](https://simpleicons.org)에서 slug 확인 후 로고 다운로드:",
        "   `curl -o scripts/icons/<slug>.svg https://cdn.jsdelivr.net/npm/simple-icons@13/icons/<slug>.svg`",
        "2. `scripts/generate_badges.py`의 `CATEGORIES`에 `(slug, 표기명, 브랜드컬러, 다크보정색|None)` 추가",
        "3. `python3 scripts/generate_badges.py` 실행 → 두 스타일 뱃지와 이 문서가 함께 재생성됨",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines))
    print("badges/README.md 생성")


if __name__ == "__main__":
    total = 0
    for style_name, style in STYLES.items():
        (OUT / style_name).mkdir(parents=True, exist_ok=True)
        for _category, badges in CATEGORIES:
            for badge in badges:
                build(style_name, style, *badge)
                total += 1
        print(f"badges/{style_name}/: 생성 완료")
    gen_gallery()
    print(f"총 {total}개")
