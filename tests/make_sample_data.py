"""Generate SYNTHETIC data in the Kaggle LinkedIn layout, to test the pipeline offline.
Never publish results from this data - it is made up.
"""
import random
import sys
from pathlib import Path

import pandas as pd

out = Path(sys.argv[1])
(out / "jobs").mkdir(parents=True, exist_ok=True)
(out / "mappings").mkdir(parents=True, exist_ok=True)
random.seed(7)

# role -> {phrase: (probability, salary uplift)}
PROFILE = {
    "Data Analyst": {"SQL": (0.8, 9000), "Tableau": (0.4, 3000), "Power BI": (0.35, 3000), "Python": (0.45, 8000),
                     "Excel": (0.7, 0), "communication": (0.8, 0), "stakeholder": (0.4, 0), "roadmap": (0.02, 0)},
    "Product Manager": {"roadmap": (0.8, 6000), "stakeholder": (0.7, 0), "A/B testing": (0.35, 9000), "SQL": (0.3, 7000),
                        "communication": (0.85, 0), "Jira": (0.4, 0), "user research": (0.5, 4000)},
    "Project Manager": {"PMP": (0.45, 5000), "Jira": (0.4, 0), "agile": (0.55, 2000), "budget": (0.6, 3000),
                        "stakeholder": (0.7, 0), "communication": (0.85, 0), "risk management": (0.5, 2000)},
}
BASE = {"Data Analyst": 80000, "Product Manager": 125000, "Project Manager": 95000}
LEVELS = [("Entry level", -20000), ("Associate", -10000), ("Mid-Senior level", 15000), ("Director", 45000)]

rows, js = [], []
jid = 1000
for role, prof in PROFILE.items():
    for _ in range(1500):
        jid += 1
        lvl, lvl_adj = random.choice(LEVELS)
        picked = [p for p, (pr, _) in prof.items() if random.random() < pr]
        sal = BASE[role] + lvl_adj + sum(prof[p][1] for p in picked) + random.gauss(0, 8000)
        rows.append({
            "job_id": jid, "company_name": f"Co{jid % 90}", "title": f"Senior {role}" if lvl == "Director" else role,
            "description": "We need someone with " + ", ".join(picked) + ". Join our team.",
            "skills_desc": "", "location": "Remote", "formatted_experience_level": lvl,
            "formatted_work_type": "Full-time", "remote_allowed": random.choice([1.0, None]),
            "views": random.randint(5, 400), "applies": random.randint(0, 80),
            "original_listed_time": 1.7e12, "normalized_salary": round(sal) if random.random() < 0.6 else None,
            "currency": "USD"})
        js.append((jid, random.choice(["IT", "MGMT", "ANLS", "PRDM"])))
# noise rows that must be filtered out
rows.append({"job_id": 9001, "company_name": "X", "title": "Construction Project Manager", "description": "budget",
             "formatted_experience_level": "Mid-Senior level", "currency": "USD"})
rows.append({"job_id": 9002, "company_name": "X", "title": "Product/Project Manager", "description": "roadmap",
             "formatted_experience_level": "Mid-Senior level", "currency": "USD"})
rows.append({"job_id": 9003, "company_name": "X", "title": "Barista", "description": "coffee",
             "formatted_experience_level": "Entry level", "currency": "USD"})

pd.DataFrame(rows).to_csv(out / "postings.csv", index=False)
pd.DataFrame(js, columns=["job_id", "skill_abr"]).to_csv(out / "jobs" / "job_skills.csv", index=False)
pd.DataFrame([("IT", "Information Technology"), ("MGMT", "Management"), ("ANLS", "Analyst"),
              ("PRDM", "Product Management")], columns=["skill_abr", "skill_name"]).to_csv(
    out / "mappings" / "skills.csv", index=False)
print(f"sample written to {out} ({len(rows)} postings)")
