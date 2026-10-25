"""LinkedIn Skills Project - build the SQLite warehouse and export Power BI tables.

Usage:
    python pipeline.py --data-dir data/raw --extra-dir data/raw_extra

--data-dir  : Kaggle `arshkon/linkedin-job-postings` (postings.csv, jobs/job_skills.csv, mappings/skills.csv)
--extra-dir : optional extra sources (cedricaubin, joykimaiyo18, christopherkverne US tech jobs)
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent

# ---------------------------------------------------------------- roles
ROLE_PATTERNS = {
    "Data Analyst": re.compile(
        r"\bdata\s+analyst\b|\banalytics\s+analyst\b|\bbi\s+analyst\b|business\s+intelligence\s+analyst|\bdata\s+analytics\b",
        re.I),
    "Product Manager": re.compile(r"\bproduct\s+(?:manager|owner|management)\b", re.I),
    "Project Manager": re.compile(r"\bproject\s+(?:manager|management)\b", re.I),
}
# Construction / facilities project managers are a different career path; keep the scope office/tech.
EXCLUDE_TITLE = re.compile(
    r"construction|civil|mechanical|electrical|hvac|plumb|facilit|real estate|property|architect|estimat|utilit|\bmep\b",
    re.I)
HYBRID_TITLE = re.compile(r"product\s*[/&-]\s*project|project\s*[/&-]\s*product", re.I)


def classify_role(title):
    if not isinstance(title, str) or EXCLUDE_TITLE.search(title) or HYBRID_TITLE.search(title):
        return None
    hits = [r for r, p in ROLE_PATTERNS.items() if p.search(title)]
    return hits[0] if len(hits) == 1 else None  # ambiguous titles are dropped


# ---------------------------------------------------------------- skills dictionary
# (skill, category, regex). Matched against description + skills_desc, case-insensitive.
SKILLS = [
    ("SQL", "Technical", r"\bsql\b|\bmysql\b|postgres|t-sql|\bplsql\b"),
    ("Excel", "Technical", r"\bexcel\b|spreadsheets?\b|vlookup|pivot tables?"),
    ("Power BI", "Technical", r"power\s?-?bi"),
    ("Tableau", "Technical", r"\btableau\b"),
    ("Looker", "Technical", r"\blooker\b"),
    ("Python", "Technical", r"\bpython\b"),
    ("Cloud Data Warehouse", "Technical", r"snowflake|bigquery|redshift|databricks"),
    ("Cloud (AWS/Azure/GCP)", "Technical", r"\baws\b|\bazure\b|\bgcp\b|google cloud"),
    ("Google Analytics", "Technical", r"google analytics|\bga4\b"),
    ("Product Analytics Tools", "Technical", r"amplitude|mixpanel|heap analytics|pendo"),
    ("ETL / Data Pipelines", "Technical", r"\betl\b|\belt\b|data pipelines?|data warehous"),
    ("Data Modeling", "Technical", r"data model+ing|dimensional model"),
    ("Data Visualization", "Technical", r"data visuali[sz]ation|dashboards?|visuali[sz]ations?"),
    ("Statistics", "Technical", r"statistic|regression|hypothesis test"),
    ("A/B Testing", "Technical", r"a/b test|\bab test|split test|experimentation"),
    ("Machine Learning / AI", "Technical", r"machine learning|\bml\b|\bai\b|artificial intelligence"),
    ("Salesforce / CRM", "Technical", r"salesforce|\bcrm\b|hubspot"),
    ("SAP / ERP", "Technical", r"\bsap\b|\berp\b|oracle"),
    ("APIs / Technical Fluency", "Technical", r"\bapis?\b|technical background|software development|\bsdlc\b"),
    ("Jira / Confluence", "Tools & Methods", r"\bjira\b|confluence"),
    ("Asana / Monday / Smartsheet", "Tools & Methods", r"\basana\b|monday\.com|smartsheet"),
    ("MS Project", "Tools & Methods", r"ms project|microsoft project"),
    ("Figma / Wireframing", "Tools & Methods", r"figma|wireframe|prototyp"),
    ("Agile / Scrum", "Tools & Methods", r"\bagile\b|\bscrum\b|\bkanban\b|sprints?"),
    ("Waterfall", "Tools & Methods", r"waterfall"),
    ("PM Certification", "Tools & Methods", r"\bpmp\b|prince2|\bcapm\b|six sigma|\bcspo\b|\bcsm\b"),
    ("Product Roadmap", "Product", r"roadmap"),
    ("Product Strategy / GTM", "Product", r"product strategy|product vision|go-to-market|\bgtm\b"),
    ("User Research", "Product", r"user research|customer discovery|user interviews?|ux research|voice of (?:the )?customer"),
    ("Backlog / Prioritization", "Product", r"backlog|prioriti[sz]"),
    ("OKRs / KPIs", "Product", r"\bokrs?\b|\bkpis?\b|key performance|success metrics"),
    ("Requirements Gathering", "Product", r"requirements? (?:gathering|definition|analysis)|user stories|\bprd\b|business requirements"),
    ("SaaS / B2B", "Product", r"\bsaas\b|\bb2b\b"),
    ("Business Analysis", "Product", r"business analy"),
    ("Stakeholder Management", "Soft / Management", r"stakeholder"),
    ("Cross-functional Collaboration", "Soft / Management", r"cross[- ]functional"),
    ("Communication", "Soft / Management", r"communicat"),
    ("Leadership", "Soft / Management", r"leadership|lead(?:ing)? teams?|mentor"),
    ("Problem Solving", "Soft / Management", r"problem[- ]solving"),
    ("Presentation / Storytelling", "Soft / Management", r"presentation|storytelling|data story"),
    ("Strategic Thinking", "Soft / Management", r"strategic"),
    ("Attention to Detail", "Soft / Management", r"attention to detail|detail[- ]oriented"),
    ("Negotiation", "Soft / Management", r"negotiat"),
    ("Risk Management", "Delivery", r"risk (?:management|assessment|mitigation)|\brisks?\b"),
    ("Budget Management", "Delivery", r"budget"),
    ("Vendor Management", "Delivery", r"vendor"),
    ("Change Management", "Delivery", r"change management"),
    ("Process Improvement", "Delivery", r"process improvement|continuous improvement|\blean\b"),
    ("Data Governance & Quality", "Delivery", r"data (?:governance|quality|integrity)"),
    ("Reporting", "Delivery", r"\breporting\b|\breports\b"),
]
SKILL_RES = [(n, re.compile(p, re.I)) for n, _, p in SKILLS]

POST_COLS = ["job_id", "role", "title", "company_name", "location", "work_type", "remote_allowed",
             "listed_date", "source"]
IN_COLS = ["job_id", "title", "description", "skills_desc", "company_name", "location", "work_type",
           "remote_allowed", "listed_date"]


def mine(df, source):
    """df has the IN_COLS columns (missing ones are filled). Returns (postings frame, [(job_id, skill)])."""
    df = df.reindex(columns=IN_COLS)
    df["role"] = df["title"].map(classify_role)
    df = df[df["role"].notna()].copy()
    if df.empty:
        return None, []
    text = df["description"].fillna("") + " " + df["skills_desc"].fillna("")
    rows = [(j, n) for j, t in zip(df["job_id"], text) for n, rx in SKILL_RES if rx.search(t)]
    df["source"] = source
    return df[POST_COLS], rows


# ---------------------------------------------------------------- sources
def load_arshkon(raw: Path):
    path = raw / "postings.csv"
    header = pd.read_csv(path, nrows=0).columns
    want = ["job_id", "company_name", "title", "description", "skills_desc", "location",
            "formatted_work_type", "remote_allowed", "original_listed_time"]
    posts, rows = [], []
    for chunk in pd.read_csv(path, usecols=[c for c in want if c in header], chunksize=20_000):
        chunk = chunk[chunk["title"].map(classify_role).notna()]
        if chunk.empty:
            continue
        df = chunk.assign(
            job_id="a_" + chunk["job_id"].astype(str),
            work_type=chunk.get("formatted_work_type"),
            listed_date=pd.to_datetime(chunk.get("original_listed_time"), unit="ms", errors="coerce")
                          .dt.strftime("%Y-%m-%d"))
        p, r = mine(df, "LinkedIn 2023-24 (arshkon)")
        if p is not None:
            posts.append(p)
            rows += r
    return pd.concat(posts), rows


def load_cedricaubin(extra: Path):
    """LinkedIn Data Analyst listings 2022. USA + Canada only (the Africa file is Arabic-language)."""
    posts, rows = [], []
    for country in ("usa", "canada"):
        f = extra / "linkedin-data-analyst-jobs-listings" / f"linkedin-jobs-{country}.csv"
        if not f.exists():
            print(f"WARN: {f} not found", file=sys.stderr)
            continue
        d = pd.read_csv(f)
        df = pd.DataFrame({
            "job_id": f"c{country}_" + d.index.astype(str), "title": d["title"], "description": d["description"],
            "company_name": d["company"], "location": d["location"],
            "work_type": d.get("onsite_remote"), "listed_date": d.get("posted_date")})
        p, r = mine(df, f"LinkedIn 2022 {country.upper()} (cedricaubin)")
        if p is not None:
            posts.append(p)
            rows += r
    return (pd.concat(posts) if posts else None), rows


def load_joykimaiyo(extra: Path):
    f = extra / "linkedin-data-jobs-dataset" / "clean_jobs.csv"
    if not f.exists():
        return None, []
    d = pd.read_csv(f)
    df = pd.DataFrame({
        "job_id": "j_" + d["id"].astype(str), "title": d["title"], "description": d["description"],
        "company_name": d["company"], "location": d["location"],
        "work_type": d.get("work_type"), "listed_date": d.get("date_posted").astype("string")})
    return mine(df, "LinkedIn 2025 (joykimaiyo18)")


def load_ustech(extra: Path):
    """christopherkverne/100k-us-tech-jobs-winter-2024 (Indeed/ZipRecruiter, Aug-Dec 2024).
    Uses pm_jobs.xlsx (Product + Project Managers) and ds_jobs.xlsx (Data Analysts)."""
    posts, rows = [], []
    for name in ("pm_jobs", "ds_jobs"):
        f = extra / "us-tech-jobs" / f"{name}.xlsx"
        if not f.exists():
            print(f"WARN: {f} not found", file=sys.stderr)
            continue
        d = pd.read_excel(f)
        d = d[d["title"].map(classify_role).notna()]
        d = d[d["date_posted"].astype(str) >= "2024-01-01"]  # a few rows carry bogus 1980s dates
        df = pd.DataFrame({
            "job_id": f"u{name}_" + d["id"].astype(str), "title": d["title"], "description": d["description"],
            "company_name": d["company"], "location": d["location"], "work_type": d.get("job_type"),
            "remote_allowed": d.get("is_remote"), "listed_date": d["date_posted"].astype(str).str[:10]})
        p, r = mine(df, "Indeed/ZipRecruiter 2024 (us-tech-jobs)")
        if p is not None:
            posts.append(p)
            rows += r
    return (pd.concat(posts).drop_duplicates("job_id") if posts else None), rows


def _key(df):
    return list(zip(df["title"].str.lower().str.strip(), df["company_name"].astype(str).str.lower().str.strip()))


def load_postings(raw: Path, extra: Path | None):
    """arshkon is the primary source. Extra sources are added after removing postings whose
    title+company already exist (cross-source / repost duplicates)."""
    p, skill_rows = load_arshkon(raw)
    parts = [p]
    if extra is not None and extra.exists():
        seen = set(_key(p))
        for loader in (load_cedricaubin, load_joykimaiyo, load_ustech):
            ep, er = loader(extra)
            if ep is None:
                continue
            keep, new_seen = [], set()
            for k in _key(ep):
                keep.append(k not in seen and k not in new_seen)
                new_seen.add(k)
            ep = ep[keep]
            seen |= new_seen
            print(f"  {loader.__name__}: +{len(ep):,} postings after dedupe")
            parts.append(ep)
            skill_rows += er
    posts = pd.concat(parts).drop_duplicates("job_id")
    skills = pd.DataFrame(skill_rows, columns=["job_id", "skill"]).drop_duplicates()
    return posts, skills[skills["job_id"].isin(posts["job_id"])]


def load_linkedin_skills(raw: Path, job_ids):
    """LinkedIn's own structured Skills categories (arshkon only)."""
    js, sk = raw / "jobs" / "job_skills.csv", raw / "mappings" / "skills.csv"
    if not (js.exists() and sk.exists()):
        print("WARN: LinkedIn job_skills/skills mapping not found - skipping category skills", file=sys.stderr)
        return pd.DataFrame(columns=["job_id", "skill_abr", "skill_name"])
    df = pd.read_csv(js).merge(pd.read_csv(sk), on="skill_abr", how="left")
    df["job_id"] = "a_" + df["job_id"].astype(str)
    return df[df["job_id"].isin(job_ids)].drop_duplicates()


# ---------------------------------------------------------------- build
def run_sql(con, folder: Path):
    for f in sorted(folder.glob("*.sql")):
        print(f"  running {f.name}")
        con.executescript(f.read_text(encoding="utf-8"))


def export(con, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.csv"):
        old.unlink()
    for t in ["dim_role", "dim_skill", "fact_postings", "fact_job_skill", "skill_scores",
              "linkedin_skill_stats", "v_top3"]:
        df = pd.read_sql(f"SELECT * FROM {t}", con)
        df.to_csv(out / f"{t}.csv", index=False, encoding="utf-8-sig")
        print(f"  exported {t}: {len(df):,} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--extra-dir", type=Path, default=None, help="optional extra datasets (data/raw_extra)")
    ap.add_argument("--db", type=Path, default=HERE / "out" / "skills.db")
    ap.add_argument("--export-dir", type=Path, default=HERE / "out" / "powerbi")
    a = ap.parse_args()

    a.db.parent.mkdir(parents=True, exist_ok=True)
    if a.db.exists():
        a.db.unlink()
    print("Loading postings and mining skills ...")
    posts, skills = load_postings(a.data_dir, a.extra_dir)
    li = load_linkedin_skills(a.data_dir, set(posts["job_id"]))
    print(f"  {len(posts):,} postings, {len(skills):,} mined skill links, {len(li):,} LinkedIn skill links")

    con = sqlite3.connect(a.db)
    posts.to_sql("postings", con, index=False)
    skills.to_sql("job_skill_mined", con, index=False)
    li.to_sql("job_skill_linkedin", con, index=False)
    pd.DataFrame([(n, c) for n, c, _ in SKILLS], columns=["skill", "category"]).to_sql("skill_dict", con, index=False)
    print("Running SQL ...")
    run_sql(con, HERE / "sql")
    print("Exporting for Power BI ...")
    export(con, a.export_dir)
    con.close()
    print(f"Done. DB: {a.db}")


if __name__ == "__main__":
    main()
