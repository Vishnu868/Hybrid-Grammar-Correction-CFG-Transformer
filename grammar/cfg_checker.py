"""CFG layer: validate phrase structure with an NLTK context-free grammar.

The grammar's terminals are POS categories; spaCy maps each word to its category, so the CFG
can parse open-vocabulary sentences while the production rules stay small and readable.
"""
import nltk

from .fsa_checker import nlp

GRAMMAR = nltk.CFG.fromstring("""
S    -> NP VP | NP VP PUNCT | S CONJ S
NP   -> DET N | DET ADJ N | DET ADJ ADJ N | PRON | N | PROPN | ADJ N | NUM N | NP PP
VP   -> V | V NP | V NP PP | V PP | V ADV | V ADJ | AUX V | AUX V NP | AUX V PP
VP   -> AUX ADJ | AUX NP | V NP NP | VP ADV | VP PP | ADV VP | V PART | AUX PART V NP
PP   -> P NP
DET  -> 'DET'
N    -> 'NOUN'
PROPN -> 'PROPN'
PRON -> 'PRON'
ADJ  -> 'ADJ'
NUM  -> 'NUM'
V    -> 'VERB'
AUX  -> 'AUX'
ADV  -> 'ADV'
P    -> 'ADP'
PART -> 'PART'
CONJ -> 'CCONJ'
PUNCT -> 'PUNCT'
""")
_parser = nltk.ChartParser(GRAMMAR)


def pos_sequence(sentence: str) -> list[str]:
    return [t.pos_ for t in nlp()(sentence) if not t.is_space]


def parse(sentence: str):
    seq = pos_sequence(sentence)
    try:
        return next(_parser.parse(seq), None)
    except ValueError:  # POS category not covered by the grammar
        return None


def check(sentence: str) -> list[dict]:
    tree = parse(sentence)
    if tree is None:
        return [{"layer": "CFG",
                 "error": "Sentence structure does not match grammar rules (S -> NP VP)",
                 "detail": " ".join(pos_sequence(sentence))}]
    return []
