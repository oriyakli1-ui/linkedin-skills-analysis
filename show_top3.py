"""Print the Top 3 skills per role from the built database.
Usage: python show_top3.py [db]
"""
import sqlite3
import sys
from pathlib import Path

db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "out" / "skills.db"
con = sqlite3.connect(db)
for role, rank, skill, demand, lift, score in con.execute(
        "SELECT role, skill_rank, skill, demand_pct, specificity_lift, score FROM v_top3"):
    lift_txt = f"{lift:.1f}x" if lift is not None else "n/a"
    print(f"  {role:16} #{rank} {skill:32} asked in {demand:5.1f}% of postings  vs other roles {lift_txt:>6}  score {score}")
