# Power BI build guide

Source: `out/powerbi/*.csv` (Get Data → Text/CSV, or use `load_tables.pq`). Encoding UTF-8.

## Model
```
dim_role (role) 1──* fact_postings (role) 1──* fact_job_skill (job_id) *──1 dim_skill (skill)
dim_role (role) 1──* skill_scores (role)       -- pre-aggregated: role, skill, skill_type, skill_rank, demand_pct, specificity_lift, score
dim_role (role) 1──* linkedin_skill_stats (role)
```
Relationship `fact_postings[job_id] → fact_job_skill[job_id]`: one-to-many, single direction.
Sort `dim_role[role]` by `role_order`. One Role slicer (from `dim_role`) drives every page.

## Pages

**1. "I want to become a..." (the hero page)**
- Slicer: Role (single select, default Product Manager).
- Three big cards, filtered `skill_type = "Hard"` and `skill_rank = 1 / 2 / 3`: skill name, "Asked in X% of postings", specificity.
- Bar: top 10 hard skills by score. Small table: top 3 soft skills (`skill_type = "Soft"`).
- Title: `Dynamic Title` measure.

**2. Market overview** (`fact_postings`): postings by role and source, remote share, top hiring companies.

**3. Skills deep-dive**: scatter of demand % (x) vs specificity (y), bubble = n_with, colour = category — the "common AND role-defining" quadrant is the story. Matrix: skill × role heatmap of demand %.

**4. Recommendations**: 3 text boxes per role (learn first / put on the CV / what to deprioritize), written from the real numbers.

## Fastest route: the generated project (`powerbi/project/LinkedInSkills.pbip`)
Contains the finished data model (6 tables, 5 relationships, all measures) and one empty report page.
1. Power BI Desktop: File > Options > Preview features > tick "Power BI Project (.pbip) save option", restart.
2. File > Open report > Browse > `powerbi/project/LinkedInSkills.pbip`. If asked, Refresh (data comes from `out\powerbi\`).
3. Load `theme.json` (View > Themes > Browse for themes).
4. Build the page (about 5 minutes):
   - Slicer: field `dim_role[role]`, single select, tile style.
   - Card x3: field `skill_scores[skill]` (aggregation "First"), visual-level filters `skill_type = Hard` and `skill_rank = 1` / `2` / `3`; add `[Skill Demand %]` and `[Specificity Label]` to each card's details.
   - Bar chart: axis `skill_scores[skill]`, value `[Skill Demand %]`, filters `skill_type = Hard`, Top N 10 by `[Skill Demand %]`; sort descending.
   - Title text box: bind to the `[Dynamic Title]` measure (Text box > fx).
5. Regenerate the project after any data change: `python powerbi/make_pbip.py`.

## Ready-made files
- `load_tables.pq`: Power Query steps (set the `DataFolder` parameter to `out\powerbi\`).
- `measures.dax`: all measures.
- `theme.json`: View > Themes > Browse for themes.

## Design notes
- One accent colour per role, neutral greys otherwise; no 3-D, no pie charts.
- Page 1 must work as a standalone screenshot for the LinkedIn post.
- The data is aggregated job-posting data with no personal information, so the report is safe to publish.
