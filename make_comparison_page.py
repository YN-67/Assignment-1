# -*- coding: utf-8 -*-
"""Generate output/results.html — a unified comparison page merging all
collocate tables (window ±5, window ±10, sentence) into one interactive view.

Features:
- Side-by-side comparison: each collocate's obs/ratio/p across the three settings
- Filter: core (all three) / shared (any two) / unique to one setting
- Search + sortable table
- Self-contained, works offline and on GitHub Pages
"""
import csv
import html
from datetime import date

SOURCES = {
    "±5": "collocates_老残.csv",
    "±10": "collocates_老残_h10.csv",
    "句": "collocates_老残_sentence.csv",
}
OUT = "output/results.html"
TARGET = "老残"


def load(path: str) -> dict[str, dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return {r["collocate"]: r for r in csv.DictReader(f)}


def main() -> None:
    data = {k: load(v) for k, v in SOURCES.items()}
    all_words = sorted({w for d in data.values() for w in d},
                       key=lambda w: -max((int(d[w]["obs_local"]) for d in data.values() if w in d), default=0))

    rows = []
    for w in all_words:
        present = [k for k in SOURCES if w in data[k]]
        rows.append({
            "word": w,
            "n": len(present),
            "cells": {k: data[k].get(w) for k in SOURCES},
        })

    # summary counts
    n_all3 = sum(1 for r in rows if r["n"] == 3)
    n_any2 = sum(1 for r in rows if r["n"] == 2)
    n_only1 = sum(1 for r in rows if r["n"] == 1)

    trs = []
    for r in rows:
        tds = []
        for k in SOURCES:
            d = r["cells"][k]
            if d:
                tds.append(f'<td class="num in-{k}">{d["obs_local"]} <span class="ratio">({float(d["ratio_local"]):.1f}×)</span></td>')
            else:
                tds.append('<td class="num miss">—</td>')
        cls = f' data-n="{r["n"]}"'
        trs.append(
            f'<tr{cls}><td>{html.escape(r["word"])}</td>' + "".join(tds) + "</tr>"
        )

    page = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>搭配词整合比较 — 《老残游记》中的 {TARGET}</title>
<style>
  :root {{ --bg:#faf9f6; --card:#fff; --ink:#2b2b2b; --muted:#6b6b6b;
    --accent:#8b2f2f; --soft:#f3e3e3; --line:#e5e1d8; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:2rem 1rem 4rem; background:var(--bg); color:var(--ink);
    font-family:"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif; line-height:1.5; }}
  main {{ max-width:960px; margin:0 auto; }}
  header {{ text-align:center; margin-bottom:2rem; }}
  h1 {{ font-size:1.7rem; margin:0 0 .3rem; }}
  h1 .t {{ color:var(--accent); }}
  .sub {{ color:var(--muted); font-size:.92rem; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1rem; margin-bottom:2rem; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1rem; text-align:center; }}
  .card .num {{ font-size:1.5rem; font-weight:700; color:var(--accent); }}
  .card .lbl {{ font-size:.78rem; color:var(--muted); }}
  section {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1.4rem; margin-bottom:2rem; }}
  h2 {{ font-size:1.1rem; margin:0 0 1rem; border-bottom:2px solid var(--soft); padding-bottom:.35rem; }}
  .controls {{ display:flex; gap:.6rem; flex-wrap:wrap; margin-bottom:1rem; }}
  input[type="search"] {{ flex:1; min-width:200px; padding:.5rem .8rem; border:1px solid var(--line); border-radius:8px; font-size:.95rem; }}
  .btn {{ padding:.45rem .9rem; border:1px solid var(--line); border-radius:8px; background:#fff; cursor:pointer; font-size:.85rem; }}
  .btn.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
  th, td {{ padding:.45rem .6rem; border-bottom:1px solid var(--line); text-align:left; }}
  th {{ background:var(--soft); cursor:pointer; user-select:none; position:sticky; top:0; }}
  td.num {{ font-variant-numeric:tabular-nums; }}
  .ratio {{ color:var(--muted); font-size:.78rem; }}
  .miss {{ color:#ccc; }}
  .in-±5 {{ background:#fdf6f6; }}
  .in-±10 {{ background:#f6f9fd; }}
  .in-句 {{ background:#f6fdf6; }}
  tr:hover td {{ background:#fbf3f3 !important; }}
  .note {{ color:var(--muted); font-size:.8rem; margin-top:.8rem; }}
  footer {{ text-align:center; color:var(--muted); font-size:.8rem; margin-top:2rem; }}
  footer a {{ color:var(--accent); }}
</style>
</head>
<body>
<main>
  <header>
    <h1>搭配词整合比较：<span class="t">{TARGET}</span> ·《老残游记》</h1>
    <div class="sub">三种设定并排比较 · Fisher 精确检验 p &lt; 0.05 · 括号内为 obs/exp 本地比值</div>
  </header>

  <div class="cards">
    <div class="card"><div class="num">{len(rows)}</div><div class="lbl">去重后搭配词总数</div></div>
    <div class="card"><div class="num">{n_all3}</div><div class="lbl">三设定共有（核心）</div></div>
    <div class="card"><div class="num">{n_any2}</div><div class="lbl">两设定共有</div></div>
    <div class="card"><div class="num">{n_only1}</div><div class="lbl">仅单一设定</div></div>
  </div>

  <section>
    <h2>整合搭配词表</h2>
    <div class="controls">
      <input type="search" id="q" placeholder="搜索搭配词…" oninput="apply()">
      <button class="btn active" data-f="0" onclick="setF(0,this)">全部</button>
      <button class="btn" data-f="3" onclick="setF(3,this)">三设定共有</button>
      <button class="btn" data-f="2" onclick="setF(2,this)">两设定共有</button>
      <button class="btn" data-f="1" onclick="setF(1,this)">仅单一设定</button>
    </div>
    <table id="tb">
      <thead><tr>
        <th data-k="w">搭配词</th>
        <th data-k="0">Window ±5（obs · 比值）</th>
        <th data-k="1">Window ±10（obs · 比值）</th>
        <th data-k="2">Sentence（obs · 比值）</th>
      </tr></thead>
      <tbody>
{chr(10).join(trs)}
      </tbody>
    </table>
    <div class="note">— 表示该设定下不显著（p ≥ 0.05 或词被过滤）。底色区分设定列。点击表头排序。</div>
  </section>

  <footer>
    相关页面：<a href="../index.html">总览</a> ·
    <a href="../collocates_老残.html">±5 报告</a> ·
    <a href="../collocates_老残_h10.html">±10 报告</a> ·
    <a href="../collocates_老残_sentence.html">Sentence 报告</a><br>
    生成于 {date.today().isoformat()} · jieba + qhchina · 《老残游记》（刘鹗）
  </footer>
</main>
<script>
let filterN = 0;
function setF(n, btn) {{
  filterN = n;
  document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  apply();
}}
function apply() {{
  const q = document.getElementById('q').value.trim();
  document.querySelectorAll('#tb tbody tr').forEach(tr => {{
    const okQ = !q || tr.children[0].textContent.includes(q);
    const okF = filterN === 0 || +tr.dataset.n === filterN;
    tr.style.display = okQ && okF ? '' : 'none';
  }});
}}
document.querySelectorAll('#tb th').forEach((th, i) => {{
  th.addEventListener('click', () => {{
    const tb = document.querySelector('#tb tbody');
    const rows = [...tb.querySelectorAll('tr')];
    const numeric = i > 0;
    rows.sort((a, b) => {{
      const va = a.children[i].textContent, vb = b.children[i].textContent;
      if (numeric) {{
        const na = va.trim() === '—' ? -1 : parseFloat(va);
        const nb = vb.trim() === '—' ? -1 : parseFloat(vb);
        return nb - na;
      }}
      return va.localeCompare(vb, 'zh');
    }});
    rows.forEach(r => tb.appendChild(r));
  }});
}});
</script>
</body>
</html>'''

    import os
    os.makedirs("output", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {OUT}: {len(rows)} unique collocates "
          f"(core={n_all3}, two={n_any2}, single={n_only1})")


if __name__ == "__main__":
    main()
