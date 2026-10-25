"""Generate a Power BI Project (.pbip) with the semantic model: 6 CSV tables, relationships, DAX measures.

Run: python powerbi/make_pbip.py      -> powerbi/project/LinkedInSkills.pbip
Open the .pbip in Power BI Desktop (File > Options > Preview features > "Power BI Project (.pbip) save option" must be on).
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent / "project"
DATA = (Path(__file__).parent.parent / "out" / "powerbi").resolve()
SM = ROOT / "LinkedInSkills.SemanticModel"
RP = ROOT / "LinkedInSkills.Report"
T = "\t"

TEXT, INT, DBL = "string", "int64", "double"
TABLES = {
    "dim_role": [("role", TEXT), ("role_order", INT)],
    "dim_skill": [("skill", TEXT), ("category", TEXT)],
    "fact_postings": [("job_id", TEXT), ("role", TEXT), ("title", TEXT), ("company_name", TEXT), ("location", TEXT),
                      ("work_type", TEXT), ("remote_allowed", DBL), ("listed_date", TEXT), ("source", TEXT)],
    "fact_job_skill": [("job_id", TEXT), ("skill", TEXT)],
    "skill_scores": [("role", TEXT), ("skill", TEXT), ("category", TEXT), ("skill_type", TEXT), ("n_postings", INT),
                     ("n_with", INT), ("demand_pct", DBL), ("specificity_lift", DBL), ("score", DBL), ("skill_rank", INT)],
    "linkedin_skill_stats": [("role", TEXT), ("skill_name", TEXT), ("n_with", INT), ("demand_pct", DBL)],
}
M_TYPE = {TEXT: "type text", INT: "Int64.Type", DBL: "type number"}
FORMAT = {"demand_pct": "0.0%", "specificity_lift": "0.0", "score": "0.000"}

# measure name -> (expression, formatString or None)
MEASURES = {
    "fact_job_skill": {
        "Skill Mentions": ("COUNTROWS ( fact_job_skill )", "#,0"),
        "Is Top 10 Mention": ("IF ( RANKX ( ALL ( fact_job_skill[skill] ), [Skill Mentions], , DESC, Dense ) <= 10, 1 )", None),
    },
    "fact_postings": {
        "Companies": ("DISTINCTCOUNT ( fact_postings[company_name] )", "#,0"),
        "Remote Share (known)": ("DIVIDE ( CALCULATE ( COUNTROWS ( fact_postings ), fact_postings[remote_allowed] = 1 ), CALCULATE ( COUNTROWS ( fact_postings ), NOT ISBLANK ( fact_postings[remote_allowed] ) ) )", "0%"),
        "Is Top 10 Company": ("IF ( RANKX ( ALL ( fact_postings[company_name] ), [Postings], , DESC, Dense ) <= 10, 1 )", None),
        "Is Top 10 Location": ("IF ( RANKX ( ALL ( fact_postings[location] ), [Postings], , DESC, Dense ) <= 10, 1 )", None),
        "Postings": ("DISTINCTCOUNT ( fact_postings[job_id] )", "#,0"),
        "Remote Share": ("DIVIDE ( CALCULATE ( [Postings], fact_postings[remote_allowed] = 1 ), [Postings] )", "0.0%"),
    },
    "skill_scores": {
        "Also Label": ("\"Then: \" & [Hard Skill 2] & \"  ·  \" & [Hard Skill 3]", None),
        "Demand Data Analyst": ("CALCULATE ( [Demand Heat], skill_scores[role] = \"Data Analyst\" )", "0%"),
        "Color Data Analyst": ("VAR d = [Demand Data Analyst] RETURN SWITCH ( TRUE (), d >= 0.65, \"#FF5C8A\", d >= 0.5, \"#E04FD0\", d >= 0.3, \"#7B5CFF\", d >= 0.15, \"#3D4FB5\", d >= 0.05, \"#2B3770\", \"#1C2444\" )", None),
        "Demand Product Manager": ("CALCULATE ( [Demand Heat], skill_scores[role] = \"Product Manager\" )", "0%"),
        "Color Product Manager": ("VAR d = [Demand Product Manager] RETURN SWITCH ( TRUE (), d >= 0.65, \"#FF5C8A\", d >= 0.5, \"#E04FD0\", d >= 0.3, \"#7B5CFF\", d >= 0.15, \"#3D4FB5\", d >= 0.05, \"#2B3770\", \"#1C2444\" )", None),
        "Demand Project Manager": ("CALCULATE ( [Demand Heat], skill_scores[role] = \"Project Manager\" )", "0%"),
        "Color Project Manager": ("VAR d = [Demand Project Manager] RETURN SWITCH ( TRUE (), d >= 0.65, \"#FF5C8A\", d >= 0.5, \"#E04FD0\", d >= 0.3, \"#7B5CFF\", d >= 0.15, \"#3D4FB5\", d >= 0.05, \"#2B3770\", \"#1C2444\" )", None),
        "Is Must-have": ("IF ( [Skill Demand %] >= 0.25 && [Role Specificity] >= 2.5, 1 )", None),
        "Is Table Stakes": ("IF ( [Skill Demand %] >= 0.25 && [Role Specificity] < 2.5, 1 )", None),
        "Is Differentiator": ("IF ( [Skill Demand %] >= 0.08 && [Skill Demand %] < 0.25 && [Role Specificity] >= 5, 1 )", None),
        "Role Color": ("SWITCH ( SELECTEDVALUE ( dim_role[role] ), \"Product Manager\", \"#8B7BFF\", \"Project Manager\", \"#19D3B5\", \"Data Analyst\", \"#FF9A3C\", \"#8B7BFF\" )", None),
        "Demand Heat": ("COALESCE ( [Skill Demand %], 0 )", "0%"),
        "Heat Color": ("VAR d = [Demand Heat] RETURN SWITCH ( TRUE (), d >= 0.65, \"#FF5C8A\", d >= 0.5, \"#E04FD0\", d >= 0.3, \"#7B5CFF\", d >= 0.15, \"#3D4FB5\", d >= 0.05, \"#2B3770\", \"#1C2444\" )", None),
        "Max Demand Any Role": ("CALCULATE ( MAX ( skill_scores[demand_pct] ), ALL ( skill_scores[role] ) )", "0%"),
        "Postings With Skill": ("SUM ( skill_scores[n_with] )", "#,0"),
        "Hard Pct 1": ("CALCULATE ( [Skill Demand %], skill_scores[skill_type] = \"Hard\", skill_scores[skill_rank] = 1 )", "0%"),
        "Hard Pct 2": ("CALCULATE ( [Skill Demand %], skill_scores[skill_type] = \"Hard\", skill_scores[skill_rank] = 2 )", "0%"),
        "Hard Pct 3": ("CALCULATE ( [Skill Demand %], skill_scores[skill_type] = \"Hard\", skill_scores[skill_rank] = 3 )", "0%"),
        "Skill Demand %": ("AVERAGE ( skill_scores[demand_pct] )", "0.0%"),
        "Role Specificity": ("AVERAGE ( skill_scores[specificity_lift] )", "0.0"),
        "Dynamic Title": ('"Top 3 skills to become a " & SELECTEDVALUE ( dim_role[role], "..." )', None),
        "Demand Label": ('"Asked in " & FORMAT ( [Skill Demand %], "0%" ) & " of postings"', None),
        "Specificity Label": ('VAR s = [Role Specificity] RETURN IF ( ISBLANK ( s ), "", FORMAT ( s, "0.0" ) & "x more common than in the other two roles" )', None),
        "Hard Rank Label 1": ('"TOP HARD SKILL #1"', None),
        "Hard Rank Label 2": ('"TOP HARD SKILL #2"', None),
        "Hard Rank Label 3": ('"TOP HARD SKILL #3"', None),
        "Hard Skill 1": ('CALCULATE ( SELECTEDVALUE ( skill_scores[skill] ), skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 1 )', None),
        "Hard Demand Label 1": ('"Asked in " & FORMAT ( CALCULATE ( [Skill Demand %], skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 1 ), "0%" ) & " of postings"', None),
        "Hard Specificity Label 1": ('CALCULATE ( [Specificity Label], skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 1 )', None),
        "Hard Skill 2": ('CALCULATE ( SELECTEDVALUE ( skill_scores[skill] ), skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 2 )', None),
        "Hard Demand Label 2": ('"Asked in " & FORMAT ( CALCULATE ( [Skill Demand %], skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 2 ), "0%" ) & " of postings"', None),
        "Hard Specificity Label 2": ('CALCULATE ( [Specificity Label], skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 2 )', None),
        "Hard Skill 3": ('CALCULATE ( SELECTEDVALUE ( skill_scores[skill] ), skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 3 )', None),
        "Hard Demand Label 3": ('"Asked in " & FORMAT ( CALCULATE ( [Skill Demand %], skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 3 ), "0%" ) & " of postings"', None),
        "Hard Specificity Label 3": ('CALCULATE ( [Specificity Label], skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = 3 )', None),
    },
}

RELATIONSHIPS = [
    ("fact_postings.role", "dim_role.role"),
    ("fact_job_skill.job_id", "fact_postings.job_id"),
    ("fact_job_skill.skill", "dim_skill.skill"),
    ("skill_scores.role", "dim_role.role"),
    ("linkedin_skill_stats.role", "dim_role.role"),
]


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def table_tmdl(name, cols):
    out = [f"table {name}", ""]
    for m, (expr, fmt) in MEASURES.get(name, {}).items():
        out.append(f"{T}measure '{m}' = {expr}")
        if fmt:
            out.append(f"{T}{T}formatString: {fmt}")
        out.append("")
    for c, typ in cols:
        out += [f"{T}column {c}", f"{T}{T}dataType: {typ}"]
        if c in FORMAT:
            out.append(f"{T}{T}formatString: {FORMAT[c]}")
        out += [f"{T}{T}summarizeBy: none", f"{T}{T}sourceColumn: {c}", ""]
    types = ", ".join(f'{{"{c}", {M_TYPE[t]}}}' for c, t in cols)
    out += [f"{T}partition {name} = m", f"{T}{T}mode: import", f"{T}{T}source =",
            f"{T}{T}{T}let",
            f'{T}{T}{T}{T}Source = Csv.Document(File.Contents(DataFolder & "{name}.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
            f"{T}{T}{T}{T}Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
            f'{T}{T}{T}{T}Typed = Table.TransformColumnTypes(Promoted, {{{types}}}, "en-US")',
            f"{T}{T}{T}in", f"{T}{T}{T}{T}Typed", ""]
    return "\n".join(out)


def main():
    write(ROOT / "LinkedInSkills.pbip", json.dumps({
        "version": "1.0", "artifacts": [{"report": {"path": "LinkedInSkills.Report"}}],
        "settings": {"enableAutoRecovery": True}}, indent=2))

    # semantic model
    write(SM / "definition.pbism", json.dumps({"version": "4.0", "settings": {}}, indent=2))
    write(SM / "definition" / "database.tmdl", "database\n\tcompatibilityLevel: 1567\n")
    refs = "\n".join(f"ref table {t}" for t in TABLES)
    write(SM / "definition" / "model.tmdl",
          "model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\n"
          f"{refs}\n\nref expression DataFolder\n")
    write(SM / "definition" / "expressions.tmdl",
          "expression DataFolder = \"" + str(DATA) + "\\\" "  # M strings take backslashes literally
          "meta [IsParameterQuery = true, Type = \"Text\", IsParameterQueryRequired = true]\n")
    for name, cols in TABLES.items():
        write(SM / "definition" / "tables" / f"{name}.tmdl", table_tmdl(name, cols))
    rel = []
    for i, (frm, to) in enumerate(RELATIONSHIPS, 1):
        rel += [f"relationship rel_{i}", f"{T}fromColumn: {frm}", f"{T}toColumn: {to}", ""]
    write(SM / "definition" / "relationships.tmdl", "\n".join(rel))

    # report skeleton (one empty page; visuals are added in Desktop)
    sch = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
    write(RP / "definition.pbir", json.dumps({
        "version": "4.0", "datasetReference": {"byPath": {"path": "../LinkedInSkills.SemanticModel"}}}, indent=2))
    d = RP / "definition"
    write(d / "version.json", json.dumps({"$schema": f"{sch}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"}, indent=2))
    write(d / "report.json", json.dumps({
        "$schema": f"{sch}/report/3.0.0/schema.json",
        "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": {"visual": "1.8.0", "report": "2.0.0", "page": "1.3.0"}, "type": "SharedResources"}}}, indent=2))
    write(d / "pages" / "pages.json", json.dumps({
        "$schema": f"{sch}/pagesMetadata/1.0.0/schema.json", "pageOrder": ["page1"], "activePageName": "page1"}, indent=2))
    write(d / "pages" / "page1" / "page.json", json.dumps({
        "$schema": f"{sch}/page/2.0.0/schema.json", "name": "page1", "displayName": "Top 3 skills",
        "displayOption": "FitToPage", "height": 720, "width": 1280}, indent=2))
    print(f"wrote {ROOT / 'LinkedInSkills.pbip'}; data folder = {DATA}")


if __name__ == "__main__":
    main()
