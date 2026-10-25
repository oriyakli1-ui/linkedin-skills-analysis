"""Read out/skills.db, embed the numbers into template.html -> index.html (the shareable dashboard)."""
import json
import sqlite3
from pathlib import Path

here = Path(__file__).parent
con = sqlite3.connect(here.parent / "out" / "skills.db")
con.row_factory = sqlite3.Row

data = {
    "postings": {r[0]: r[1] for r in con.execute("SELECT role, COUNT(*) FROM postings GROUP BY role")},
    "sources": [list(r) for r in con.execute(
        "SELECT CASE WHEN source LIKE 'Indeed%' THEN 'Indeed / ZipRecruiter' ELSE 'LinkedIn' END, COUNT(*) "
        "FROM postings GROUP BY 1")],
    "skills": {},
}
for role in data["postings"]:
    rows = [dict(r) for r in con.execute(
        "SELECT skill, skill_type, ROUND(100 * demand_pct, 1) AS demand, ROUND(specificity_lift, 1) AS lift "
        "FROM skill_scores WHERE role = ? ORDER BY skill_type, skill_rank", (role,))]
    data["skills"][role] = {"hard": [r for r in rows if r["skill_type"] == "Hard"][:10],
                            "soft": [r for r in rows if r["skill_type"] == "Soft"][:3]}

html = (here / "template.html").read_text(encoding="utf-8").replace("/*DATA*/", json.dumps(data, ensure_ascii=False))
(here / "index.html").write_text(html, encoding="utf-8")
print(f"wrote {here / 'index.html'} ({len(html) // 1024} KB)")
