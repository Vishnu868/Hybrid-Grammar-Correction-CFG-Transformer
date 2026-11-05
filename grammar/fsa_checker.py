"""FSA layer: word-level morphology checks (plurals, tense, subject-verb agreement) using spaCy."""
import spacy

_nlp = None

IRREGULAR_PLURALS = {
    "childs": "children", "mans": "men", "womans": "women", "foots": "feet", "tooths": "teeth",
    "mouses": "mice", "gooses": "geese", "persons": "people", "sheeps": "sheep", "fishs": "fish",
}
IRREGULAR_PAST = {
    "go": "went", "eat": "ate", "see": "saw", "come": "came", "take": "took", "run": "ran",
    "write": "wrote", "buy": "bought", "make": "made", "get": "got", "have": "had", "do": "did",
    "give": "gave", "know": "knew", "think": "thought", "drink": "drank", "sing": "sang",
}
PAST_MARKERS = {"yesterday", "ago", "last", "previously"}
THIRD_SINGULAR = {"he", "she", "it"}


def nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _past(verb: str) -> str:
    if verb in IRREGULAR_PAST:
        return IRREGULAR_PAST[verb]
    return verb + ("d" if verb.endswith("e") else "ed")


def _third_person(verb: str) -> str:
    if verb in ("have",):
        return "has"
    if verb.endswith(("s", "sh", "ch", "x", "o")):
        return verb + "es"
    if verb.endswith("y") and verb[-2:-1] not in "aeiou":
        return verb[:-1] + "ies"
    return verb + "s"


def check(sentence: str) -> list[dict]:
    doc = nlp()(sentence)
    tokens = [t.text.lower() for t in doc]
    errors = []

    for t in doc:
        if t.text.lower() in IRREGULAR_PLURALS:
            errors.append({"layer": "FSA", "error": f"Wrong plural form '{t.text}'",
                           "suggestion": IRREGULAR_PLURALS[t.text.lower()]})

    has_past_marker = any(m in tokens for m in PAST_MARKERS)
    for t in doc:
        if t.pos_ not in ("VERB", "AUX") or t.text.lower() in ("will", "shall", "can", "may"):
            continue
        # Tense: base/present form together with a past-time marker
        if has_past_marker and t.tag_ in ("VB", "VBP", "VBZ") and t.dep_ == "ROOT":
            errors.append({"layer": "FSA", "error": f"Tense mismatch: '{t.text}' with past-time marker",
                           "suggestion": _past(t.lemma_.lower())})
        # Agreement: he/she/it + base verb (present tense)
        subj = [c for c in t.children if c.dep_ == "nsubj"]
        if (not has_past_marker and subj and subj[0].text.lower() in THIRD_SINGULAR
                and t.tag_ == "VBP"):
            errors.append({"layer": "FSA",
                           "error": f"Subject-verb agreement: '{subj[0].text} {t.text}'",
                           "suggestion": f"{subj[0].text} {_third_person(t.text.lower())}"})
    return errors
