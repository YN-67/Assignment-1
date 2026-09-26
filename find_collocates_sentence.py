# -*- coding: utf-8 -*-
"""Find collocates of 老残 using the SENTENCE method.

Pipeline:
1. Split novel.txt into sentences (on Chinese end-of-sentence punctuation).
2. Tokenize each sentence with jieba, removing punctuation tokens.
3. qhchina find_collocates with method="sentence": a sentence counts as one
   co-occurrence unit (no horizon needed). p < 0.05, stopwords and 1-char
   words filtered.
4. Write results to collocates_老残_sentence.csv.
5. Compare with the window-method results (horizon 5 and 10) and print
   which collocates differ between the settings.
"""
import csv

import jieba
from qhchina.analytics.collocations import find_collocates
from qhchina.helpers.texts import load_stopwords

from find_collocates_laocan import SRC, TARGET, is_punct, split_sentences

DST = "collocates_老残_sentence.csv"
H5_CSV = "collocates_老残.csv"        # window ±5 results
H10_CSV = "collocates_老残_h10.csv"   # window ±10 results


def main() -> None:
    with open(SRC, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Split into sentences.
    sentences = split_sentences(text)
    print(f"Sentences: {len(sentences)}")

    # 2. Tokenize with jieba, no punctuation tokens.
    tokenized = [[t for t in jieba.cut(s) if not is_punct(t)] for s in sentences]
    print(f"Tokens:    {sum(len(t) for t in tokenized):,}")
    tokenized = [t for t in tokenized if t]

    stopwords = load_stopwords("zh_sim")
    print(f"Stopwords: {len(stopwords)}")

    # 3. Collocates of 老残, SENTENCE method (whole sentence as context unit).
    results = find_collocates(
        sentences=tokenized,
        target_words=TARGET,
        method="sentence",          # no horizon parameter in this mode
        filters={
            "max_p": 0.05,
            "stopwords": stopwords,
            "min_word_length": 2,
        },
        return_type="dataframe",
    )

    print(f"Significant collocates (p < 0.05, sentence method): {len(results)}")

    # 4. Save as CSV.
    results.to_csv(DST, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote {DST}")

    if not results.empty:
        preview = results[["collocate", "obs_local", "exp_local", "ratio_local", "p_value"]]
        print("\nTop collocates (sentence method):")
        print(preview.head(20).to_string(index=False))

    # 5. Compare settings: which collocates are unique to each method?
    def load_collocates(path: str) -> set[str]:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                return {r["collocate"] for r in csv.DictReader(f)}
        except FileNotFoundError:
            return set()

    sent = set(results["collocate"]) if not results.empty else set()
    h5 = load_collocates(H5_CSV)
    h10 = load_collocates(H10_CSV)

    print("\n=== Comparison of settings ===")
    print(f"window ±5: {len(h5)} | window ±10: {len(h10)} | sentence: {len(sent)}")
    print(f"\nOnly in sentence method ({len(sent - h5 - h10)}):")
    print("  " + "、".join(sorted(sent - h5 - h10)))
    print(f"\nOnly in window ±5 ({len(h5 - sent - h10)}):")
    print("  " + "、".join(sorted(h5 - sent - h10)))
    print(f"\nIn all three settings ({len(sent & h5 & h10)}):")
    print("  " + "、".join(sorted(sent & h5 & h10)))


if __name__ == "__main__":
    main()
