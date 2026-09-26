# -*- coding: utf-8 -*-
"""Find statistically significant collocates of 老残 in the novel.

Pipeline:
1. Read novel.txt and split it into sentences (on Chinese end-of-sentence
   punctuation: 。！？；… and their full-width variants).
2. Tokenize each sentence with jieba.
3. Use qhchina.analytics.collocations.find_collocates with:
     - method  = "window"
     - horizon = 5   (5 words to the left and right of the target)
     - filter  = max_p 0.05 (only significant collocates kept)
4. Write the results to collocates_老残.csv.
"""
import csv
import string

import jieba
from qhchina.analytics.collocations import find_collocates
from qhchina.helpers.texts import load_stopwords

SRC = "novel.txt"
DST = "collocates_老残.csv"
TARGET = "老残"

# Sentence-ending punctuation used to split the text.
SENTENCE_DELIMITERS = "。！？；…\n\r"

# All punctuation characters to strip from the token lists (Chinese + ASCII).
PUNCTUATION = set(string.punctuation + "：；，。！？、（）《》〈〉「」『』【】〔〕"
                  "“”‘’…—～·［］｛＂＃＄％＆＇＊＋－／＜＝＞＠〔〕＼＾＿｀｛｜｝～")


def split_sentences(text: str) -> list[str]:
    """Split text into sentences on Chinese end-of-sentence punctuation."""
    sentences, current = [], []
    for ch in text:
        if ch in SENTENCE_DELIMITERS:
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []
        else:
            current.append(ch)
    # Keep any trailing text without a final delimiter.
    tail = "".join(current).strip()
    if tail:
        sentences.append(tail)
    return sentences


def is_punct(token: str) -> bool:
    """True if the token consists only of punctuation/whitespace characters."""
    return all(ch in PUNCTUATION or ch.isspace() for ch in token)


def main() -> None:
    with open(SRC, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Split into sentences.
    sentences = split_sentences(text)
    print(f"Sentences: {len(sentences)}")

    # 2. Tokenize each sentence with jieba and remove punctuation tokens.
    tokenized = [[t for t in jieba.cut(s) if not is_punct(t)]
                 for s in sentences]
    print(f"Tokens:    {sum(len(t) for t in tokenized):,}")

    # Drop empty token lists (find_collocates expects non-empty sentences).
    tokenized = [t for t in tokenized if t]

    # Load simplified Chinese stopwords.
    stopwords = load_stopwords("zh_sim")
    print(f"Stopwords: {len(stopwords)}")

    # 3. Find collocates of 老残: window method, horizon 5 left and right,
    #    p-value below 0.05, stopwords and one-character words filtered out.
    results = find_collocates(
        sentences=tokenized,
        target_words=TARGET,
        method="window",
        horizon=5,
        filters={
            "max_p": 0.05,
            "stopwords": stopwords,
            "min_word_length": 2,
        },
        return_type="dataframe",
    )

    print(f"Significant collocates (p < 0.05): {len(results)}")

    # 4. Save as CSV.
    results.to_csv(DST, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote {DST}")

    # Show a preview.
    if not results.empty:
        preview = results[["collocate", "obs_local", "exp_local", "ratio_local", "p_value"]]
        print("\nTop collocates:")
        print(preview.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
