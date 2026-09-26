# -*- coding: utf-8 -*-
"""Find statistically significant collocates of 老残 (horizon = 10).

Pipeline:
1. Split novel.txt into sentences (on Chinese end-of-sentence punctuation).
2. Tokenize each sentence with jieba, removing punctuation tokens.
3. qhchina find_collocates: method="window", horizon=10 (10 words left and
   right of the target), p < 0.05, stopwords and 1-char words filtered.
4. Write results to collocates_老残_h10.csv.
"""
import csv

import jieba
from qhchina.analytics.collocations import find_collocates
from qhchina.helpers.texts import load_stopwords

from find_collocates_laocan import SRC, TARGET, is_punct, split_sentences

DST = "collocates_老残_h10.csv"
HORIZON = 10


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

    # 3. Collocates of 老残, window ±10, p < 0.05.
    results = find_collocates(
        sentences=tokenized,
        target_words=TARGET,
        method="window",
        horizon=HORIZON,
        filters={
            "max_p": 0.05,
            "stopwords": stopwords,
            "min_word_length": 2,
        },
        return_type="dataframe",
    )

    print(f"Significant collocates (p < 0.05, horizon {HORIZON}): {len(results)}")

    # 4. Save as CSV.
    results.to_csv(DST, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote {DST}")

    if not results.empty:
        preview = results[["collocate", "obs_local", "exp_local", "ratio_local", "p_value"]]
        print("\nTop collocates:")
        print(preview.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
