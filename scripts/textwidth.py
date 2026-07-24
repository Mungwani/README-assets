"""프로포셔널 산세리프 폰트의 글자 폭을 근사 추정하는 공용 유틸.

단순히 "글자 수 × 평균폭"으로 계산하면 i/l 같은 좁은 글자가 많은 라벨은
오른쪽 여백이 넓어 보이고, M/W나 한글이 많은 문장은 좁아 보인다.
글자를 폭 등급으로 분류해 실제 렌더링 폭에 더 가깝게 추정하고,
모든 뱃지·카드가 같은 함수를 쓰게 해서 오른쪽 여백이 일관되게 만든다.
"""

NARROW = set("iIjlJ.,:;'!|ftr")   # 좁은 글자: i, l, 구두점, f/t/r
WIDE = set("mwMW@%")              # 넓은 글자

NARROW_EM = 0.30
WIDE_EM = 0.85
UPPER_EM = 0.68
DEFAULT_EM = 0.55
SPACE_EM = 0.30
HANGUL_EM = 1.05


def _is_hangul(ch):
    o = ord(ch)
    return 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3131 <= o <= 0x318E


def char_em(ch):
    if ch == " ":
        return SPACE_EM
    if _is_hangul(ch):
        return HANGUL_EM
    if ch in NARROW:
        return NARROW_EM
    if ch in WIDE:
        return WIDE_EM
    if ch.isupper():
        return UPPER_EM
    return DEFAULT_EM


def text_width(label, font_size, weight_factor=1.0):
    """label을 font_size(px)로 렌더링했을 때의 대략적인 폭(px)."""
    return sum(char_em(ch) for ch in label) * font_size * weight_factor
