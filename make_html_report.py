# -*- coding: utf-8 -*-
"""Generate a self-contained HTML report of the 老残 collocation results.

Reads collocates_老残.csv and writes collocates_老残.html with:
- summary statistics cards
- a horizontal bar chart of the top collocates (pure CSS, no dependencies)
- a sortable, searchable table of all results
"""
import csv
import html
import math
from datetime import date

CSV_PATH = "collocates_老残.csv"
HTML_PATH = "collocates_老残.html"
TARGET = "老残"
TOP_N = 25


def load_rows(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fmt_p(p: float) -> str:
    if p == 0:
        return "0"
    if p < 1e-4:
        return f"{p:.2e}"
    return f"{p:.4f}"


def main() -> None:
    rows = load_rows(CSV_PATH)
    for r in rows:
        r["exp_local"] = float(r["exp_local"])
        r["obs_local"] = int(r["obs_local"])
        r["ratio_local"] = float(r["ratio_local"])
        r["obs_global"] = int(r["obs_global"])
        r["p_value"] = float(r["p_value"])

    rows.sort(key=lambda r: r["obs_local"], reverse=True)
    top = rows[:TOP_N]
    max_obs = top[0]["obs_local"] if top else 1

    # ---- bar chart rows (CSS width proportional to obs_local) ----
    bars = "\n".join(
        f'''<div class="bar-row">
  <div class="bar-label"><a href="#" onclick="filterTable('{html.escape(r["collocate"])}');return false;">{html.escape(r["collocate"])}</a></div>
  <div class="bar-track"><div class="bar-fill" style="width:{r["obs_local"] / max_obs * 100:.1f}%"></div></div>
  <div class="bar-value">{r["obs_local"]}</div>
</div>'''
        for r in top
    )

    # ---- table rows ----
    table_rows = "\n".join(
        f'''<tr data-collocate="{html.escape(r["collocate"])}">
  <td>{html.escape(r["collocate"])}</td>
  <td class="num">{r["obs_local"]}</td>
  <td class="num">{r["exp_local"]:.2f}</td>
  <td class="num">{r["ratio_local"]:.2f}</td>
  <td class="num">{r["obs_global"]}</td>
  <td class="num">{fmt_p(r["p_value"])}</td>
</tr>'''
        for r in rows
    )

    n = len(rows)
    strongest = max(rows, key=lambda r: r["ratio_local"])

    page = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Collocates of {TARGET} — 《老残游记》</title>
<style>
  :root {{
    --bg: #faf9f6; --card: #ffffff; --ink: #2b2b2b; --muted: #6b6b6b;
    --accent: #8b2f2f; --accent-soft: #f3e3e3; --line: #e5e1d8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 2rem 1rem 4rem; background: var(--bg); color: var(--ink);
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    line-height: 1.5;
  }}
  main {{ max-width: 900px; margin: 0 auto; }}
  header {{ text-align: center; margin-bottom: 2.5rem; }}
  h1 {{ font-size: 1.9rem; margin: 0 0 .3rem; }}
  h1 .target {{ color: var(--accent); }}
  .subtitle {{ color: var(--muted); font-size: .95rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem; margin-bottom: 2.5rem; }}
  .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 1rem 1.2rem; text-align: center; }}
  .card .num {{ font-size: 1.6rem; font-weight: 700; color: var(--accent); }}
  .card .lbl {{ font-size: .8rem; color: var(--muted); margin-top: .2rem; }}
  section {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 1.5rem; margin-bottom: 2rem; }}
  h2 {{ font-size: 1.15rem; margin: 0 0 1rem; border-bottom: 2px solid var(--accent-soft);
    padding-bottom: .4rem; }}
  /* bar chart */
  .bar-row {{ display: grid; grid-template-columns: 90px 1fr 48px; align-items: center;
    gap: .6rem; margin-bottom: .45rem; }}
  .bar-label {{ text-align: right; font-size: .95rem; white-space: nowrap; overflow: hidden; }}
  .bar-label a {{ color: var(--ink); text-decoration: none; }}
  .bar-label a:hover {{ color: var(--accent); text-decoration: underline; }}
  .bar-track {{ background: var(--accent-soft); border-radius: 6px; height: 20px; overflow: hidden; }}
  .bar-fill {{ background: linear-gradient(90deg, #b05050, var(--accent)); height: 100%;
    border-radius: 6px; }}
  .bar-value {{ font-size: .85rem; color: var(--muted); }}
  /* table */
  .controls {{ display: flex; gap: .8rem; margin-bottom: 1rem; flex-wrap: wrap; }}
  input[type="search"] {{ flex: 1; min-width: 220px; padding: .5rem .8rem; font-size: .95rem;
    border: 1px solid var(--line); border-radius: 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
  th, td {{ padding: .5rem .7rem; border-bottom: 1px solid var(--line); text-align: left; }}
  th {{ background: var(--accent-soft); cursor: pointer; user-select: none; position: sticky; top: 0; }}
  th:hover {{ background: #ecd6d6; }}
  td.num {{ font-variant-numeric: tabular-nums; }}
  tr:hover td {{ background: #fdf6f6; }}
  .note {{ color: var(--muted); font-size: .82rem; margin-top: .8rem; }}
  footer {{ text-align: center; color: var(--muted); font-size: .8rem; margin-top: 2rem; }}
</style>
</head>
<body>
<main>
  <header>
    <h1>Collocates of <span class="target">{TARGET}</span> in 《老残游记》</h1>
    <div class="subtitle">Statistically significant collocates · window method · horizon ±5 words · Fisher's exact test, p &lt; 0.05</div>
  </header>

  <div class="cards">
    <div class="card"><div class="num">{n}</div><div class="lbl">significant collocates</div></div>
    <div class="card"><div class="num">{rows[0]["obs_local"]}</div><div class="lbl">most frequent co-occurrence ({html.escape(rows[0]["collocate"])})</div></div>
    <div class="card"><div class="num">{strongest["ratio_local"]:.1f}×</div><div class="lbl">strongest attraction ({html.escape(strongest["collocate"])})</div></div>
    <div class="card"><div class="num">{sum(r["obs_local"] for r in rows)}</div><div class="lbl">total co-occurrences</div></div>
  </div>

  <section>
    <h2>Top {len(top)} collocates by co-occurrence count</h2>
    {bars}
    <div class="note">Click a word to jump to it in the table below.</div>
  </section>

  <section>
    <h2>All results ({n})</h2>
    <div class="controls">
      <input type="search" id="search" placeholder="Search collocate…" oninput="filterTable(this.value)">
    </div>
    <table id="results">
      <thead>
        <tr>
          <th data-key="collocate">Collocate ▾</th>
          <th data-key="obs_local">Obs. co-occurrence</th>
          <th data-key="exp_local">Expected</th>
          <th data-key="ratio_local">Obs/Exp</th>
          <th data-key="obs_global">Global freq.</th>
          <th data-key="p_value">p-value</th>
        </tr>
      </thead>
      <tbody>
{table_rows}
      </tbody>
    </table>
    <div class="note">Obs. = observed co-occurrences within ±5 words of {TARGET}; Expected = count under independence; Obs/Exp &gt; 1 indicates attraction. Click column headers to sort.</div>
  </section>

  <footer>Generated {date.today().isoformat()} · jieba segmentation · qhchina find_collocates · 《老残游记》 (刘鹗)</footer>
</main>

<script>
// ---- table search ----
function filterTable(query) {{
  query = query.trim();
  const rows = document.querySelectorAll('#results tbody tr');
  rows.forEach(tr => {{
    const hit = !query || tr.dataset.collocate.includes(query);
    tr.style.display = hit ? '' : 'none';
  }});
  document.getElementById('search').value = query;
  document.getElementById('results').scrollIntoView({{ behavior: 'smooth' }});
}}

// ---- sortable columns ----
const state = {{ key: null, asc: false }};
document.querySelectorAll('#results th').forEach(th => {{
  th.addEventListener('click', () => {{
    const key = th.dataset.key;
    state.asc = (state.key === key) ? !state.asc : (key === 'collocate');
    state.key = key;
    const tbody = document.querySelector('#results tbody');
    const rows = [...tbody.querySelectorAll('tr')];
    const numeric = key !== 'collocate';
    rows.sort((a, b) => {{
      let va = a.children[[...th.parentNode.children].indexOf(th)].textContent;
      let vb = b.children[[...th.parentNode.children].indexOf(th)].textContent;
      if (numeric) {{ va = parseFloat(va); vb = parseFloat(vb);
        return state.asc ? va - vb : vb - va; }}
      return state.asc ? va.localeCompare(vb, 'zh') : vb.localeCompare(va, 'zh');
    }});
    rows.forEach(r => tbody.appendChild(r));
    document.querySelectorAll('#results th').forEach(t =>
      t.textContent = t.textContent.replace(/ [▲▾]$/, ''));
    th.textContent += state.asc ? ' ▲' : ' ▾';
  }});
}});
</script>
</body>
</html>'''

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {HTML_PATH} ({n} collocates, top {len(top)} charted)")


if __name__ == "__main__":
    main()
