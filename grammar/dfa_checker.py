"""DFA layer: sentence-level format checks implemented as an explicit finite automaton."""
import re

VALID_CHARS = re.compile(r"^[A-Za-z0-9\s.,!?;:'\"()\-]+$")
END_PUNCT = {".", "!", "?"}
PUNCT = set(".,!?;:")


def _run_dfa(sentence: str) -> bool:
    """States: START -> WORD <-> SPACE, WORD -> PUNCT -> (SPACE | END). Rejects repeated punctuation."""
    state = "START"
    for ch in sentence:
        if state == "START":
            state = "WORD" if ch.isalnum() else "REJECT"
        elif state in ("WORD", "SPACE"):
            if ch.isalnum() or ch in "'\"()-":
                state = "WORD"
            elif ch.isspace():
                state = "SPACE"
            elif ch in PUNCT:
                state = "PUNCT" if state == "WORD" else "REJECT"
            else:
                state = "REJECT"
        elif state == "PUNCT":
            state = "SPACE" if ch.isspace() else ("REJECT" if ch in PUNCT else "WORD")
        if state == "REJECT":
            return False
    return state in ("PUNCT", "WORD", "SPACE")


def check(sentence: str) -> list[dict]:
    s = sentence.strip()
    errors = []
    if not s:
        return [{"layer": "DFA", "error": "Empty sentence"}]
    if not s[0].isupper():
        errors.append({"layer": "DFA", "error": "Sentence should start with a capital letter",
                       "suggestion": s[0].upper() + s[1:]})
    if s[-1] not in END_PUNCT:
        errors.append({"layer": "DFA", "error": "Sentence should end with . ! or ?"})
    if re.search(r"([.,!?;:])\1", s):
        errors.append({"layer": "DFA", "error": "Repeated punctuation marks"})
    if re.search(r"\s{2,}", s):
        errors.append({"layer": "DFA", "error": "Multiple consecutive spaces"})
    if not VALID_CHARS.match(s):
        errors.append({"layer": "DFA", "error": "Sentence contains invalid symbols"})
    if not errors and not _run_dfa(s):
        errors.append({"layer": "DFA", "error": "Invalid token/punctuation sequence"})
    return errors
