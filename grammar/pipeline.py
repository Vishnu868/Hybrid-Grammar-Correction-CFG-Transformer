"""Hybrid pipeline: DFA -> FSA -> CFG (explainable detection) -> T5 (contextual correction)."""
from . import cfg_checker, dfa_checker, fsa_checker, transformer


class HybridGrammarCorrector:
    def __init__(self, use_transformer: bool = True):
        self.use_transformer = use_transformer

    def check(self, sentence: str) -> dict:
        sentence = " ".join(sentence.split())
        dfa = dfa_checker.check(sentence)
        fsa = fsa_checker.check(sentence)
        cfg = cfg_checker.check(sentence)
        corrected = transformer.correct(sentence) if self.use_transformer else sentence
        if corrected and corrected[-1] not in ".!?":
            corrected += "."
        return {
            "input": sentence,
            "errors": {"DFA": dfa, "FSA": fsa, "CFG": cfg},
            "error_count": len(dfa) + len(fsa) + len(cfg),
            "corrected": corrected,
            "changed": corrected.strip() != sentence.strip(),
        }


if __name__ == "__main__":
    import json
    hgc = HybridGrammarCorrector()
    for s in ["he go to school yesterday", "The childs is playing in the park.",
              "Dog the runs fast.", "She goes to school."]:
        print(json.dumps(hgc.check(s), indent=2))
