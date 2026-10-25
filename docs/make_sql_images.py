"""Renders SQL images (schema diagram, query + result, sample rows) from out/skills.db.
Run: py docs/make_sql_images.py   (needs Microsoft Edge for the PNG rendering)"""
import html, os, sqlite3, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "docs", "images")
EDGE = next(p for p in ["C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
                        "C:/Program Files/Microsoft/Edge/Application/msedge.exe"] if os.path.exists(p))
db = sqlite3.connect(os.path.join(ROOT, "out", "skills.db"))
CSS = """*{box-sizing:border-box;margin:0}body{background:#0B1020;color:#F2F5FF;font-family:'Segoe UI',Arial,sans-serif;padding:40px;width:1600px}
h1{font-size:34px}p.s{color:#9AA6C8;margin:6px 0 24px;font-size:20px}
pre{background:#121936;border-radius:14px;padding:24px;font:20px/1.45 Consolas,monospace;color:#CFE3FF;white-space:pre-wrap}
table{border-collapse:collapse;font-size:20px;width:100%}th{background:#1C2444;text-align:left;padding:10px 14px;color:#FFD166}
td{padding:9px 14px;border-bottom:1px solid #1C2444}.k{color:#FFD166}"""

def shot(name, body, height):
    page = f"<html><meta charset=utf-8><style>{CSS}</style><body>{body}</body></html>"
    f = os.path.join(tempfile.gettempdir(), name + ".html")
    open(f, "w", encoding="utf-8").write(page)
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size=1680,{height}",
                    f"--screenshot={os.path.abspath(os.path.join(OUT, name + '.png'))}", "file:///" + f.replace("\\", "/")],
                   check=True, capture_output=True)

def table(cols, rows):
    return "<table><tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>" + "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in r) + "</tr>" for r in rows) + "</table>"

# 1. schema with live row counts
tables = ["postings", "job_skill_mined", "job_skill_linkedin", "skill_dict", "dim_role", "dim_skill", "fact_postings", "fact_job_skill", "skill_scores", "linkedin_skill_stats"]
rows = []
for t in tables:
    cols = ", ".join(r[1] for r in db.execute(f"pragma table_info({t})"))
    rows.append((t, f"{db.execute(f'select count(*) from {t}').fetchone()[0]:,}", cols))
shot("sql_1_schema", "<h1>skills.db: tables and row counts</h1><p class=s>SQLite star schema built by pipeline.py + sql/01_model.sql</p>"
     + table(["table", "rows", "columns"], rows), 760)

# 2. the headline query and its result
q = open(os.path.join(ROOT, "sql", "02_skill_scores.sql"), encoding="utf-8").read()
q = q[q.index("DROP TABLE IF EXISTS skill_scores"):q.index("-- The headline")].strip()
r = db.execute("select role, skill_rank, skill, category, demand_pct, specificity_lift from v_top3").fetchall()
shot("sql_2_scoring_query", "<h1>Scoring query: demand per role and skill</h1><p class=s>CTEs + window functions (ROW_NUMBER, SUM OVER)</p><pre>"
     + html.escape(q) + "</pre>", 1000)
shot("sql_3_top3_result", "<h1>SELECT * FROM v_top3</h1><p class=s>The 3 most requested hard skills per role (demand_pct = share of the role's postings)</p>"
     + table(["role", "rank", "skill", "category", "demand_pct", "specificity_lift"], r), 560)

# 3. sample rows from the fact table
s = db.execute("select job_id, role, title, company_name, work_type, source from fact_postings order by random() limit 8").fetchall()
shot("sql_4_fact_postings_sample", "<h1>fact_postings: sample rows</h1><p class=s>8,473 postings across 5 sources</p>"
     + table(["job_id", "role", "title", "company", "work_type", "source"], s), 560)
