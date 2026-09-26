# -*- coding: utf-8 -*-
"""Visualize collocates of 老残 with qhchina.plot_collocates.

Steps:
1. Re-run the collocation analysis with only the p-value filter
   (no stopwords / min_word_length restrictions) to get MORE collocates.
2. Load the CJK font for matplotlib via qhchina.helpers.load_fonts().
3. Plot the results as a scatter plot (obs/Exp ratio vs p-value) and
   save it to collocates_老残.png.
"""
import matplotlib.pyplot as plt
from qhchina.analytics.collocations import find_collocates, plot_collocates
from qhchina.helpers import load_fonts

import jieba
from find_collocates_laocan import (DST as CSV_PATH, SENTENCE_DELIMITERS, SRC,
                                    TARGET, is_punct, split_sentences)

OUT_PNG = "collocates_老残.png"


def main() -> None:
    # 1. Tokenize (same pipeline as before).
    with open(SRC, "r", encoding="utf-8") as f:
        text = f.read()

    sentences = split_sentences(text)
    tokenized = [[t for t in jieba.cut(s) if not is_punct(t)] for s in sentences]
    tokenized = [t for t in tokenized if t]

    # 2. Run analysis with ONLY the p-value filter -> more collocates
    #    (stopwords and one-character words are kept this time).
    results = find_collocates(
        sentences=tokenized,
        target_words=TARGET,
        method="window",
        horizon=5,
        filters={"max_p": 0.05},
        return_type="dataframe",
    )
    print(f"Collocates plotted: {len(results)}")

    # 3. Load the CJK font BEFORE rendering so Chinese labels display.
    font_name = load_fonts()
    print(f"Font loaded: {font_name}")

    # 4. Plot: x = association strength (obs/exp), y = significance,
    #    colored by global frequency, top 30 words labelled.
    plot_collocates(
        results,
        x_col="ratio_local",
        y_col="p_value",
        color_by="obs_local",
        title=f"Collocates of {TARGET} in 《老残游记》 (window ±5, p < 0.05)",
        show_labels=True,
        label_top_n=30,
        figsize=(12, 9),
        filename=OUT_PNG,
    )
    print(f"Saved {OUT_PNG}")


if __name__ == "__main__":
    main()
