// Adds the measures used by the multi-page report to the TMDL model and to make_pbip.py (idempotent)
const fs = require("fs"), path = require("path");
const TB = path.join(__dirname, "project", "LinkedInSkills.SemanticModel", "definition", "tables");
const HARD = (n) => `skill_scores[skill_type] = "Hard", skill_scores[skill_rank] = ${n}`;
const M = {
  skill_scores: {
    "Role Color": ['SWITCH ( SELECTEDVALUE ( dim_role[role] ), "Product Manager", "#8B7BFF", "Project Manager", "#19D3B5", "Data Analyst", "#FF9A3C", "#8B7BFF" )', null],
    "Demand Heat": ["COALESCE ( [Skill Demand %], 0 )", "0%"],
    "Heat Color": ['VAR d = [Demand Heat] RETURN SWITCH ( TRUE (), d >= 0.65, "#FF5C8A", d >= 0.5, "#E04FD0", d >= 0.3, "#7B5CFF", d >= 0.15, "#3D4FB5", d >= 0.05, "#2B3770", "#1C2444" )', null],
    "Max Demand Any Role": ["CALCULATE ( MAX ( skill_scores[demand_pct] ), ALL ( skill_scores[role] ) )", "0%"],
    "Is Must-have": ["IF ( [Skill Demand %] >= 0.25 && [Role Specificity] >= 2.5, 1 )", null],
    "Is Table Stakes": ["IF ( [Skill Demand %] >= 0.25 && [Role Specificity] < 2.5, 1 )", null],
    "Is Differentiator": ["IF ( [Skill Demand %] >= 0.08 && [Skill Demand %] < 0.25 && [Role Specificity] >= 5, 1 )", null],
    "Also Label": ['"Then: " & [Hard Skill 2] & "  ·  " & [Hard Skill 3]', null],
    ...Object.fromEntries(["Data Analyst", "Product Manager", "Project Manager"].flatMap((r) => [
      ["Demand " + r, ["CALCULATE ( [Demand Heat], skill_scores[role] = \"" + r + "\" )", "0%"]],
      ["Color " + r, ["VAR d = [Demand " + r + "] RETURN SWITCH ( TRUE (), d >= 0.65, \"#FF5C8A\", d >= 0.5, \"#E04FD0\", d >= 0.3, \"#7B5CFF\", d >= 0.15, \"#3D4FB5\", d >= 0.05, \"#2B3770\", \"#1C2444\" )", null]]])),
    "Postings With Skill": ["SUM ( skill_scores[n_with] )", "#,0"],
    ...Object.fromEntries([1, 2, 3].map((n) => [`Hard Pct ${n}`, [`CALCULATE ( [Skill Demand %], ${HARD(n)} )`, "0%"]])),
  },
  fact_job_skill: {
    "Skill Mentions": ["COUNTROWS ( fact_job_skill )", "#,0"],
    "Is Top 10 Mention": ["IF ( RANKX ( ALL ( fact_job_skill[skill] ), [Skill Mentions], , DESC, Dense ) <= 10, 1 )", null],
  },
  fact_postings: {
    "Companies": ["DISTINCTCOUNT ( fact_postings[company_name] )", "#,0"],
    "Remote Share (known)": ["DIVIDE ( CALCULATE ( COUNTROWS ( fact_postings ), fact_postings[remote_allowed] = 1 ), CALCULATE ( COUNTROWS ( fact_postings ), NOT ISBLANK ( fact_postings[remote_allowed] ) ) )", "0%"],
    "Is Top 10 Company": ["IF ( RANKX ( ALL ( fact_postings[company_name] ), [Postings], , DESC, Dense ) <= 10, 1 )", null],
    "Is Top 10 Location": ["IF ( RANKX ( ALL ( fact_postings[location] ), [Postings], , DESC, Dense ) <= 10, 1 )", null],
  },
};
for (const [table, ms] of Object.entries(M)) {
  const p = path.join(TB, `${table}.tmdl`);
  let s = fs.readFileSync(p, "utf8");
  const nl = s.includes("\r\n") ? "\r\n" : "\n";
  let add = "";
  for (const [name, [expr, fmt]] of Object.entries(ms)) {
    if (s.includes(`measure '${name}'`) || s.includes(`measure ${name} =`)) continue;
    add += `\tmeasure '${name}' = ${expr}${nl}` + (fmt ? `\t\tformatString: ${fmt}${nl}` : "") + nl;
  }
  if (add) s = s.replace(/\tcolumn /, () => add + "\tcolumn ");
  fs.writeFileSync(p, s);
}
const g = path.join(__dirname, "make_pbip.py");
let py = fs.readFileSync(g, "utf8");
for (const [table, ms] of Object.entries(M)) {
  let add = "";
  for (const [name, [expr, fmt]] of Object.entries(ms)) {
    if (py.includes(`"${name}":`)) continue;
    add += `        "${name}": (${JSON.stringify(expr)}, ${fmt ? JSON.stringify(fmt) : "None"}),\n`;
  }
  py = py.replace(new RegExp(`(    "${table}": \\{\\r?\\n)`), (x) => x + add);
}
fs.writeFileSync(g, py);
console.log("ok");
