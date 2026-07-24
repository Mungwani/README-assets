# Project Cards

레포 README의 "프로젝트" 섹션용 카드 + 상세 정보 시스템.

## 왜 SVG 카드만으로 "자세히 보기"가 안 되는가

GitHub README의 `![]()` 이미지는 `<img>` 태그로 삽입되는데, 이 순간 SVG 내부에
클릭 이벤트를 넣어도 인터랙션이 죽습니다 (애니메이션처럼 선언적으로 재생되는
것만 동작). 그래서 카드는 **요약 배너(SVG)** 로만 쓰고, 펼쳐지는 상세 내용은
GitHub가 네이티브로 지원하는 `<details><summary>` 접기 블록으로 구현합니다.
카드 이미지 + `<details>` 조합이 GitHub README에서 "자세히 보기"를 만드는
사실상 표준 패턴입니다.

## 카드 미리보기

`scripts/generate_project_card.py`의 `PROJECTS` 리스트에 항목을 추가하면
`projects/cards/<slug>.svg` 가 생성됩니다. 제목 · 기간 · 역할 · 한줄소개 ·
스택 로고까지만 담고, 나머지는 아래 markdown 템플릿에서 작성하세요.

![example card](cards/example.svg)

```python
# scripts/generate_project_card.py 의 PROJECTS 에 추가
(
    "my-project",                          # slug → projects/cards/my-project.svg
    "실시간 주문 알림 서비스",                # 제목
    "2026.03 – 2026.05",                   # 기간
    "백엔드 · 주문/결제 API, 알림 큐 설계",   # 역할
    "폴링 방식이던 주문 상태 확인을 SSE로 전환해 응답 지연을 90% 줄임",  # 한줄소개
    ["openjdk", "springboot", "mysql", "docker"],  # 스택 아이콘 (scripts/icons 의 slug)
),
```

생성: `python3 scripts/generate_project_card.py`

## README에 조합하는 방법

카드 아래에 링크, 그 아래에 접히는 상세 블록을 붙입니다. 이 전체 블록을
프로젝트 하나당 그대로 복사해서 채우세요.

```markdown
![my-project](projects/cards/my-project.svg)

🔗 [배포 링크](https://example.com) · [GitHub 레포](https://github.com/me/my-project)

<details>
<summary>📂 자세히 보기 — 아키텍처 · ERD · 트러블슈팅</summary>

### 아키텍처

<img src="projects/cards/my-project-architecture.png" width="700" alt="architecture">

- 클라이언트 → API Gateway → Spring Boot → MySQL / Redis
- (다이어그램은 draw.io, Excalidraw 등으로 그려서 PNG로 내보낸 뒤 이 경로에 추가)

### ERD

<img src="projects/cards/my-project-erd.png" width="700" alt="erd">

### 트러블슈팅

**1. N+1 쿼리로 목록 조회가 느렸던 문제**
- 증상: 주문 목록 API가 항목 수에 비례해 쿼리가 늘어남
- 원인: 연관 엔티티를 각 루프마다 지연 로딩
- 해결: `fetch join`으로 전환, 응답 시간 420ms → 60ms

**2. (문제 제목)**
- 증상:
- 원인:
- 해결:

### 담당 역할

- 주문/결제 API 설계 및 구현
- 알림 큐(RabbitMQ) 도입

</details>
```

### 구현 포인트

- **카드에는 요약만**: 제목·기간·역할 한 줄·스택 로고까지만 SVG에 넣고,
  분량이 긴 내용(ERD, 아키텍처, 트러블슈팅)은 `<details>` 안 markdown으로 —
  SVG 텍스트로는 줄바꿈·긴 문단 관리가 사실상 불가능하기 때문
- **이미지 경로**: ERD·아키텍처 다이어그램은 draw.io / Excalidraw / dbdiagram.io 등에서
  그려서 PNG로 내보낸 뒤 `projects/cards/<slug>-erd.png` 형태로 레포에 함께 커밋
- **트러블슈팅 포맷**: 증상 → 원인 → 해결 3단 구조를 고정해서, 면접관이
  훑어도 문제 해결 과정이 바로 읽히도록 함
- **스택 로고**: `scripts/icons`(뱃지와 같은 simple-icons 소스)를 재사용해
  카드마다 새로 로고를 구할 필요 없음
- **카드 안에 "자세히 보기" 문구를 넣지 않음**: 눌러도 반응 없는 텍스트를 이미지에
  박아두면 오히려 어색해 보여서 뺐다 — 실제 펼치기 동작은 카드 바로 아래
  `<details><summary>`가 담당하므로 그쪽에만 문구가 있으면 충분함
- **설명 줄바꿈**: 글자 수가 아니라 `scripts/textwidth.py`(뱃지와 공용)로 추정한
  실제 렌더링 폭 기준으로 줄바꿈해서, 카드 가로 폭을 최대한 채우고 남는 만큼만
  다음 줄로 넘어감
