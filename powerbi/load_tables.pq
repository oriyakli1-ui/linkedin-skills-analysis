// Power BI: Home > Transform data > New Source > Blank Query > Advanced Editor.
// Create ONE parameter first: Home > Manage parameters > New  ->  DataFolder (Text) = C:\Users\oriya\.claude\linkedin-skills-project\out\powerbi\
// Then paste this as a function-style helper query named LoadCsv, and create one query per table below.

// ---- Query "LoadCsv" (set as function) ----
(fileName as text) =>
let
    Source = Csv.Document(File.Contents(DataFolder & fileName), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Promoted

// ---- Query "dim_role" ----   = LoadCsv("dim_role.csv")  then: change types role=text, role_order=Int64
// ---- Query "dim_skill" ----  = LoadCsv("dim_skill.csv")
// ---- Query "fact_postings" - = LoadCsv("fact_postings.csv")
//        types: listed_date=Date
// ---- Query "fact_job_skill" = LoadCsv("fact_job_skill.csv")
// ---- Query "skill_scores" -- = LoadCsv("skill_scores.csv")
//        types: demand_pct, specificity_lift, score = Decimal;
//               skill_rank, n_with, n_postings = Int64
// ---- Query "linkedin_skill_stats" = LoadCsv("linkedin_skill_stats.csv")
// ---- Query "top3" ---------- = LoadCsv("v_top3.csv")   (optional shortcut table for the hero cards)

// Example of one complete table query (fact_postings):
let
    Source = LoadCsv("fact_postings.csv"),
    Typed = Table.TransformColumnTypes(Source, {
        {"listed_date", type date}, {"role", type text}})
in
    Typed
