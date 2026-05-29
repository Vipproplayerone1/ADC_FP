import re


_MULTI_WS = re.compile(r"[ \t]+")
_MULTI_NL = re.compile(r"\n{3,}")
_HYPHEN_BREAK = re.compile(r"(\w+)-\n(\w+)")
_PAGE_NUM_LINE = re.compile(r"^\s*\d+\s*$", re.MULTILINE)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = _HYPHEN_BREAK.sub(r"\1\2", text)
    text = _PAGE_NUM_LINE.sub("", text)
    text = _MULTI_WS.sub(" ", text)
    text = _MULTI_NL.sub("\n\n", text)
    return text.strip()
