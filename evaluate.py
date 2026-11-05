"""Evaluate the corrector on a CSV of (wrong, correct) sentence pairs."""
import argparse

import pandas as pd

from grammar.pipeline import HybridGrammarCorrector


def normalise(s: str) -> str:
    return " ".join(str(s).lower().strip().rstrip(".!?").split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--wrong-col", default="wrong")
    ap.add_argument("--correct-col", default="correct")
    ap.add_argument("--limit", type=int, default=500)
    args = ap.parse_args()

    df = pd.read_csv(args.data).dropna().head(args.limit)
    hgc = HybridGrammarCorrector()
    preds, detected = [], []
    for s in df[args.wrong_col]:
        r = hgc.check(s)
        preds.append(r["corrected"])
        detected.append(r["error_count"] > 0)

    df["predicted"] = preds
    exact = (df["predicted"].map(normalise) == df[args.correct_col].map(normalise)).mean()
    print(f"Sentences evaluated : {len(df)}")
    print(f"Exact-match accuracy: {exact:.2%}")
    print(f"Rule-layer detection: {sum(detected) / len(df):.2%} of inputs flagged")
    df.to_csv("evaluation_results.csv", index=False)


if __name__ == "__main__":
    main()
