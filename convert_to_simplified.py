# -*- coding: utf-8 -*-
"""Convert the novel to simplified Chinese using OpenCC (t2s).

Reads 10_老残游记.txt, normalizes any traditional/variant characters
to simplified, and writes the result to novel.txt (UTF-8).
"""
from opencc import OpenCC

SRC = "10_老残游记.txt"
DST = "novel.txt"


def read_text(path: str) -> str:
    # Try common encodings in order.
    for enc in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Could not decode {path} with any known encoding")


def main() -> None:
    text = read_text(SRC)
    cc = OpenCC("t2s")  # Traditional -> Simplified (safe on already-simplified text)
    simplified = cc.convert(text)

    with open(DST, "w", encoding="utf-8") as f:
        f.write(simplified)

    print(f"Characters read:    {len(text):,}")
    print(f"Characters written: {len(simplified):,}")
    print(f"Wrote {DST}")


if __name__ == "__main__":
    main()
