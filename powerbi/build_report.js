// Generates all report pages (PBIR) for the LinkedIn Skills Compass dashboard.
// Run: node powerbi/build_report.js   (close Power BI Desktop first, then reopen the .pbip)
const fs = require("fs"), path = require("path");
const DEF = path.join(__dirname, "project", "LinkedInSkills.Report", "definition");
const PAGES = path.join(DEF, "pages");
fs.rmSync(PAGES, { recursive: true, force: true });

const SCH = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition";
// ---- palette (dark, colourful) ----
const BG = "#0B1020", PANEL = "#151B33", PANEL2 = "#1C2444", TEXT = "#F2F5FF", MUTED = "#9AA6C8", GRID = "#2A3358";
const VIOLET = "#8B7BFF", TEAL = "#19D3B5", ORANGE = "#FF9A3C";
const PINK = "#FF5C8A", CYAN = "#22D3EE", GOLD = "#FFD166";
const ROLES = { "Product Manager": "#8B7BFF", "Project Manager": "#19D3B5", "Data Analyst": "#FF9A3C" };
const CATS = { Technical: "#22D3EE", Product: "#8B7BFF", Delivery: "#19D3B5", "Tools & Methods": "#FFD166", "Soft / Management": "#FF5C8A" };

// ---- query / format helpers ----
const col = (e, p) => ({ Column: { Expression: { SourceRef: { Entity: e } }, Property: p } });
const meas = (e, p) => ({ Measure: { Expression: { SourceRef: { Entity: e } }, Property: p } });
const proj = (f, ref, displayName) => ({ field: f, queryRef: ref, ...(displayName ? { displayName } : {}) });
const lit = (v) => ({ Literal: { Value: v } });
const txt = (v) => ({ expr: lit(`'${v}'`) });
const num = (v) => ({ expr: lit(`${v}D`) });
const on = (b) => ({ expr: lit(String(b)) });
const clr = (c) => ({ solid: { color: txt(c) } });
const clrM = (e, p) => ({ solid: { color: { expr: meas(e, p) } } });
const S = "skill_scores", F = "fact_postings";
const sm = (p) => proj(meas(S, p), `${S}.${p}`);
const sc = (p, d) => proj(col(S, p), `${S}.${p}`, d);

const cond = (type, e, p, inner) => ({ Condition: inner });
const inWhere = (p, vals, src = "t") => ({ Condition: { In: { Expressions: [{ Column: { Expression: { SourceRef: { Source: src } }, Property: p } }], Values: vals.map((v) => [lit(`'${v}'`)]) } } });
const inFilter = (name, e, p, vals) => ({ name, field: col(e, p), type: "Categorical", filter: { Version: 2, From: [{ Name: "t", Entity: e, Type: 0 }], Where: [inWhere(p, vals)] } });
const cmpFilter = (name, field, entity, kind, value) => ({ name, field, type: "Advanced", filter: { Version: 2, From: [{ Name: "t", Entity: entity, Type: 0 }],
  Where: [{ Condition: { Comparison: { ComparisonKind: kind, Left: field.Column ? { Column: { Expression: { SourceRef: { Source: "t" } }, Property: field.Column.Property } } : { Measure: { Expression: { SourceRef: { Source: "t" } }, Property: field.Measure.Property } }, Right: lit(value) } } }] } });
const rankLE = (n) => cmpFilter(`rank${n}`, col(S, "skill_rank"), S, 4, `${n}L`);
const hard = () => inFilter("hard", S, "skill_type", ["Hard"]);
const soft = () => inFilter("soft", S, "skill_type", ["Soft"]);

// container styling
const box = (title, o = {}) => ({
  background: [{ properties: { show: on(true), color: clr(o.bg || PANEL), transparency: num(0) } }],
  border: [{ properties: { show: on(true), color: clr(o.bg || PANEL), radius: num(o.radius === undefined ? 14 : o.radius) } }],
  dropShadow: [{ properties: { show: on(false) } }],
  title: [{ properties: title ? { show: on(true), text: txt(title), fontSize: num(13), bold: on(true), fontColor: clr(MUTED), alignment: txt("left") } : { show: on(false) } }],
});
const bare = { background: [{ properties: { show: on(false) } }], border: [{ properties: { show: on(false) } }], title: [{ properties: { show: on(false) } }] };

class Page {
  constructor(id, name) { this.id = id; this.name = name; this.v = []; }
  add(name, x, y, w, h, visual, filters, extra = {}) {
    this.v.push({ $schema: `${SCH}/visualContainer/2.0.0/schema.json`, name, position: { x, y, z: this.v.length, width: w, height: h, tabOrder: this.v.length }, visual, ...(filters ? { filterConfig: { filters } } : {}), ...extra });
  }
  text(name, x, y, w, h, runs, cont = bare, align = "left") {
    const paragraphs = runs.map((para) => ({ textRuns: para.map((r) => ({ value: r.t, textStyle: { fontFamily: r.f || "Segoe UI", fontSize: `${r.s || 12}pt`, fontWeight: r.b ? "bold" : "normal", color: r.c || TEXT } })), horizontalTextAlignment: align }));
    this.add(name, x, y, w, h, { visualType: "textbox", objects: { general: [{ properties: { paragraphs } }] }, visualContainerObjects: cont, drillFilterOtherVisuals: true });
  }
  // card: items = [{entity, m, name?}]
  card(name, x, y, w, h, entity, m, o) {
    const lab = { fontSize: num(o.size || 24), bold: on(o.bold !== false), fontFamily: txt("Segoe UI Semibold"), color: o.colorMeasure ? clrM(S, o.colorMeasure) : clr(o.color || TEXT) };
    this.add(name, x, y, w, h, { visualType: "card", query: { queryState: { Values: { projections: [proj(meas(entity, m), `${entity}.${m}`, o.caption)] } } },
      objects: { labels: [{ properties: lab }], categoryLabels: [{ properties: o.caption ? { show: on(true), fontSize: num(o.capSize || 12), color: clr(o.capColor || MUTED) } : { show: on(false) } }] },
      visualContainerObjects: o.cont || bare, drillFilterOtherVisuals: true }, o.filters);
  }
  slicer(name, x, y, w, h, role) {
    const f = inFilter("def", "dim_role", "role", [role]).filter;
    this.add(name, x, y, w, h, { visualType: "slicer", query: { queryState: { Values: { projections: [proj(col("dim_role", "role"), "dim_role.role")] } } },
      objects: { data: [{ properties: { mode: txt("Basic") } }],
        selection: [{ properties: { singleSelect: on(true), selectAllCheckboxEnabled: on(false) } }],
        header: [{ properties: { show: on(false) } }],
        items: [{ properties: { fontSize: num(15), fontColor: clr(TEXT), background: clr(PANEL2), outline: clr(GRID) } }],
        general: [{ properties: { orientation: num(1), filter: { filter: f } } }] },
      visualContainerObjects: { background: [{ properties: { show: on(false) } }], border: [{ properties: { show: on(false) } }], title: [{ properties: { show: on(false) } }] },
      drillFilterOtherVisuals: true });
  }
  // horizontal bar chart. o: {cat:[entity,prop], val:[entity,measure], fillMeasure, fill, byRole, byCat, labelFmt, title, filters}
  bar(name, x, y, w, h, o) {
    const dp = [];
    if (o.fillMeasure) dp.push({ properties: { fill: clrM(S, o.fillMeasure) } });
    else dp.push({ properties: { fill: clr(o.fill || CYAN) } });
    if (o.byRole) for (const [r, c] of Object.entries(ROLES)) dp.push({ properties: { fill: clr(c) }, selector: { data: [{ scopeId: { Comparison: { ComparisonKind: 0, Left: col(o.cat[0], o.cat[1]), Right: lit(`'${r}'`) } } }] } });
    this.add(name, x, y, w, h, { visualType: "barChart",
      query: { queryState: { Category: { projections: [proj(col(o.cat[0], o.cat[1]), `${o.cat[0]}.${o.cat[1]}`)] }, Y: { projections: [proj(meas(o.val[0], o.val[1]), `${o.val[0]}.${o.val[1]}`)] } },
        sortDefinition: { sort: [{ field: meas(o.val[0], o.val[1]), direction: "Descending" }] } },
      objects: { dataPoint: dp,
        labels: [{ properties: { show: on(true), fontSize: num(12), color: clr(TEXT), labelPrecision: num(0), labelDisplayUnits: num(1) } }],
        valueAxis: [{ properties: { show: on(false), showAxisTitle: on(false) } }],
        categoryAxis: [{ properties: { fontSize: num(12), labelColor: clr(TEXT), showAxisTitle: on(false), maxMarginFactor: num(50) } }],
        legend: [{ properties: { show: on(false) } }] },
      visualContainerObjects: box(o.title), drillFilterOtherVisuals: true }, o.filters);
  }
  write() {
    this.interactions = this.interactions || [];
    [VIOLET, TEAL, ORANGE, PINK].forEach((c, i) => this.v.unshift({ $schema: `${SCH}/visualContainer/2.0.0/schema.json`, name: `strip${i}`, position: { x: i * 320, y: 0, z: -10 + i, width: 320, height: 16, tabOrder: 100 + i }, visual: { visualType: "textbox", objects: { general: [{ properties: { paragraphs: [{ textRuns: [{ value: " " }] }] } }] }, visualContainerObjects: { background: [{ properties: { show: on(true), color: clr(c), transparency: num(0) } }], border: [{ properties: { show: on(false) } }], title: [{ properties: { show: on(false) } }] }, drillFilterOtherVisuals: true } }));
    const d = path.join(PAGES, this.id);
    for (const v of this.v) { const vd = path.join(d, "visuals", v.name); fs.mkdirSync(vd, { recursive: true }); fs.writeFileSync(path.join(vd, "visual.json"), JSON.stringify(v, null, 2)); }
    fs.mkdirSync(d, { recursive: true });
    fs.writeFileSync(path.join(d, "page.json"), JSON.stringify({ $schema: `${SCH}/page/2.0.0/schema.json`, name: this.id, displayName: this.name, displayOption: "FitToPage", height: 720, width: 1280, ...(this.interactions.length ? { visualInteractions: this.interactions } : {}),
      objects: { background: [{ properties: { color: clr(BG), transparency: num(0) } }] } }, null, 2));
  }
}
const H = (t, sub) => [[{ t, s: 26, b: true, f: "Segoe UI Semibold" }], ...(sub ? [[{ t: sub, s: 12, c: MUTED }]] : [])];
const DARK = "#0B1020";
const kicker = (pg, t, c = GOLD) => pg.text("kicker", 40, 14, 1200, 24, [[{ t, s: 11, b: true, c }]]);

// =============== COVER ===============
const p0 = new Page("cover", "Cover");
p0.text("k", 40, 22, 1200, 26, [[{ t: "I READ 8,473 JOB POSTINGS SO YOU DON'T HAVE TO", s: 12, b: true, c: GOLD }]]);
p0.text("h", 40, 50, 1200, 100, [[{ t: "What do employers REALLY ask for?", s: 44, b: true, f: "Segoe UI Semibold" }]]);
p0.text("s", 40, 146, 1200, 40, [[{ t: "The #1 skill each role is hiring for, from real LinkedIn and Indeed postings.", s: 16, c: MUTED }]]);
Object.entries(ROLES).forEach(([role, c], i) => {
  const x = 40 + i * 407, W = 386, y0 = 200, f = [inFilter("r", S, "role", [role])];
  const tile = box(null, { bg: c, radius: 0 });
  p0.text(`role${i}`, x, y0, W, 74, [[{ t: role.toUpperCase(), s: 17, b: true, c: DARK, f: "Segoe UI Semibold" }], [{ t: "#1 SKILL TO LEARN", s: 10, b: true, c: DARK }]], tile);
  p0.card(`sk${i}`, x, y0 + 74, W, 68, S, "Hard Skill 1", { size: 28, color: DARK, cont: tile, filters: f });
  p0.card(`pc${i}`, x, y0 + 142, W, 140, S, "Hard Pct 1", { size: 60, color: DARK, caption: "of postings ask for it", capColor: DARK, capSize: 13, cont: tile, filters: f });
  p0.card(`sp${i}`, x, y0 + 282, W, 40, S, "Hard Specificity Label 1", { size: 11, color: DARK, bold: false, cont: tile, filters: f });
  p0.card(`al${i}`, x, y0 + 322, W, 50, S, "Also Label", { size: 12, color: DARK, bold: true, cont: tile, filters: f });
});
p0.text("cta", 40, 590, 1200, 74, [[{ t: "Pick your role on the next page and see exactly what to learn first  →", s: 20, b: true, c: DARK, f: "Segoe UI Semibold" }]], box(null, { bg: GOLD }), "center");
p0.text("foot", 40, 676, 1200, 28, [[{ t: "Source: aggregated public job postings (LinkedIn 2022-25, Indeed/ZipRecruiter 2024). No personal data.", s: 10, c: MUTED }]], bare, "center");

// =============== PAGE 1: explore a role ===============
const p1 = new Page("hero", "1 Explore your role");
p1.card("title", 40, 16, 1200, 52, S, "Dynamic Title", { size: 28, colorMeasure: "Role Color" });
p1.text("sub", 40, 66, 1200, 28, [[{ t: "Pick a role below. Every number is the share of that role's job postings that mention the skill.", s: 12, c: MUTED }]], bare, "center");
p1.slicer("roleSlicer", 40, 100, 1200, 50, "Product Manager");
[1, 2, 3].forEach((n, i) => {
  const x = 40 + i * 407, W = 386;
  p1.card(`rank${n}`, x, 166, W, 34, S, `Hard Rank Label ${n}`, { size: 12, colorMeasure: "Role Color", cont: box() });
  p1.card(`skill${n}`, x, 200, W, 54, S, `Hard Skill ${n}`, { size: 22, cont: box() });
  p1.card(`pct${n}`, x, 254, W, 84, S, `Hard Pct ${n}`, { size: 44, colorMeasure: "Role Color", caption: "of postings ask for it", cont: box() });
  p1.card(`spec${n}`, x, 338, W, 34, S, `Hard Specificity Label ${n}`, { size: 11, color: MUTED, bold: false, cont: box() });
});
p1.bar("top10", 40, 390, 760, 310, { cat: [S, "skill"], val: [S, "Skill Demand %"], fillMeasure: "Role Color", title: "TOP 10 HARD SKILLS  -  % of postings asking for them", filters: [hard(), rankLE(10)] });
p1.bar("soft5", 820, 390, 420, 200, { cat: [S, "skill"], val: [S, "Skill Demand %"], fill: PINK, title: "TOP SOFT SKILLS", filters: [soft(), rankLE(5)] });
p1.card("postings", 820, 600, 420, 100, F, "Postings", { size: 30, colorMeasure: "Role Color", caption: "job postings analysed for this role", cont: box() });

// =============== PAGE 2: compare roles ===============
const p2 = new Page("compare", "2 Compare roles");
p2.text("t", 40, 12, 1200, 84, H("Same market, three completely different skill sets", "The top skills of every role side by side."));
p2.text("ban", 40, 100, 1200, 46, [[{ t: "The one skill all three share: Communication (85%, 82% and 69% of postings). Everything else is what sets the roles apart.", s: 13, b: true, c: DARK }]], box(null, { bg: GOLD }), "center");
Object.entries(ROLES).forEach(([role, c], i) => {
  const x = 40 + i * 407, W = 386;
  p2.card(`n${i}`, x, 158, W, 92, F, "Postings", { size: 32, color: c, caption: `${role} postings analysed`, cont: box(), filters: [inFilter("r", F, "role", [role])] });
  p2.bar(`h${i}`, x, 262, W, 250, { cat: [S, "skill"], val: [S, "Skill Demand %"], fill: c, title: `${role.toUpperCase()}  -  TOP HARD SKILLS`, filters: [inFilter("r", S, "role", [role]), hard(), rankLE(6)] });
  p2.bar(`s${i}`, x, 524, W, 176, { cat: [S, "skill"], val: [S, "Skill Demand %"], fill: MUTED, title: "TOP SOFT SKILLS", filters: [inFilter("r", S, "role", [role]), soft(), rankLE(3)] });
});

// =============== PAGE 3: skill tiers ===============
const p3 = new Page("tiers", "3 What to learn");
p3.text("t", 40, 12, 1200, 84, H("What to learn: three kinds of skills", "Pick a role. Skills are sorted by how many employers ask for them and how unique they are to that role."));
p3.slicer("roleSlicer", 40, 92, 1200, 44, "Product Manager");
const TIERS = [
  ["MUST-HAVES", PINK, "Asked by 25%+ of postings and 2.5x+ more common in this role than elsewhere. Learn these first.", "Is Must-have"],
  ["TABLE STAKES", CYAN, "Asked by 25%+ of postings, but wanted in every role. Expected, will not set you apart.", "Is Table Stakes"],
  ["DIFFERENTIATORS", GOLD, "Rarer (8-25% of postings) but 5x+ more common here. Add one to stand out.", "Is Differentiator"],
];
TIERS.forEach(([name, c, desc, flag], i) => {
  const x = 40 + i * 407, W = 386;
  p3.text("h" + i, x, 150, W, 116, [[{ t: name, s: 18, b: true, c, f: "Segoe UI Semibold" }], [{ t: " ", s: 4 }], [{ t: desc, s: 11, c: MUTED }]], box());
  p3.bar("b" + i, x, 278, W, 422, { cat: [S, "skill"], val: [S, "Skill Demand %"], fill: c, title: "% of postings asking for it", filters: [cmpFilter("tier", meas(S, flag), S, 2, "1L")] });
});

// =============== PAGE 4: heat map ===============
const p4 = new Page("heat", "4 Skill heat map");
p4.text("t", 40, 12, 1200, 84, H("Which skills belong to which role?", "The brighter the cell, the more of that role's postings ask for the skill. Read across a row to see where a skill matters."));
p4.add("matrix", 40, 100, 760, 600, { visualType: "pivotTable",
  query: { queryState: { Rows: { projections: [sc("skill", "Skill")] }, Columns: { projections: [proj(col("dim_role", "role"), "dim_role.role", "Role")] }, Values: { projections: [sm("Demand Heat")] } },
    sortDefinition: { sort: [{ field: meas(S, "Max Demand Any Role"), direction: "Descending" }] } },
  objects: {
    values: [{ properties: { fontSize: num(12), fontColor: clr(TEXT), backColor: clrM(S, "Heat Color") }, selector: { data: [{ dataViewWildcard: { matchingOption: 1 } }], metadata: `${S}.Demand Heat` } }],
    columnHeaders: [{ properties: { fontSize: num(12), bold: on(true), fontColor: clr(MUTED), backColor: clr(PANEL) } }],
    rowHeaders: [{ properties: { fontSize: num(12), fontColor: clr(TEXT), backColor: clr(PANEL) } }],
    grid: [{ properties: { gridVertical: on(false), gridHorizontal: on(false), outlineColor: clr(PANEL), rowPadding: num(2) } }],
    total: [{ properties: { totals: on(false) } }], subTotals: [{ properties: { rowSubtotals: on(false), columnSubtotals: on(false) } }] },
  visualContainerObjects: box("HEAT MAP  -  % of postings asking for each skill"), drillFilterOtherVisuals: true }, [hard(), cmpFilter("maxd", meas(S, "Max Demand Any Role"), S, 2, "0.25D")]);
p4.text("tips", 820, 100, 420, 600, [
  [{ t: "HOW TO READ IT", s: 13, b: true, c: GOLD }], [{ t: " ", s: 6 }],
  [{ t: "Look for a row with one bright cell: that skill belongs to one role.", s: 12 }], [{ t: " ", s: 8 }],
  [{ t: "SQL", s: 14, b: true, c: ROLES["Data Analyst"] }], [{ t: "67% of Data Analyst postings, but only 8% of Product Manager and 2% of Project Manager.", s: 12, c: MUTED }], [{ t: " ", s: 8 }],
  [{ t: "Product Roadmap", s: 14, b: true, c: ROLES["Product Manager"] }], [{ t: "70% of Product Manager postings vs 5% and 4% in the other two.", s: 12, c: MUTED }], [{ t: " ", s: 8 }],
  [{ t: "Budget Management", s: 14, b: true, c: ROLES["Project Manager"] }], [{ t: "56% of Project Manager postings vs 11% and 7% elsewhere.", s: 12, c: MUTED }], [{ t: " ", s: 8 }],
  [{ t: "Communication", s: 14, b: true, c: PINK }], [{ t: "Bright in every column: wanted everywhere, so it is expected, not a differentiator.", s: 12, c: MUTED }],
], box());

// =============== PAGE 5: playbook ===============
const p5 = new Page("recs", "5 Your playbook");
p5.text("t", 40, 12, 1200, 84, H("Your playbook: what to learn, show and skip", "Written from the real numbers: every percentage is the share of that role's postings."));
const REC = {
  "Product Manager": [
    "Product Roadmap (70% of postings, 16x more than other roles), Backlog / Prioritization (65%) and Product Strategy / GTM (55%, 38x more specific). These are what hiring managers screen for.",
    "Lead with Communication (85%), Stakeholder Management (68%) and Cross-functional Collaboration (64%). Add Agile / Scrum (47%) to show you work well with engineers.",
    "SQL (8%), Python (3%) and BI tools such as Tableau or Power BI (2-6%) barely show up, yet dominate analyst roles. Nice to have, not a priority.",
  ],
  "Project Manager": [
    "Budget Management (56%, 5x more than other roles), Reporting (49%) and Risk Management (48%). Delivery skills dominate this role.",
    "PM Certification is in 28% of postings and 8x more common here than elsewhere: a cheap credential that sets you apart. Pair it with Vendor Management (26%) and Communication (82%).",
    "Product Strategy (0%), Product Roadmap (4%), SQL (2%) and Python (0%). Analytics and product skills are almost never requested in project-management postings.",
  ],
  "Data Analyst": [
    "SQL (67%), Reporting (67%) and Data Visualization (59%). SQL alone is 10x more common here than in the other two roles.",
    "Prove Statistics (46%, 12x), Python (43%, 19x) and Power BI (34%, 15x) with real projects. Python is the strongest differentiator in the whole dataset.",
    "Budget Management (7%), Product Roadmap (5%) and Product Strategy (2%). Management-flavoured skills matter little for analyst hiring.",
  ],
};
Object.entries(ROLES).forEach(([role, c], i) => {
  const x = 40 + i * 407, W = 386, rec = REC[role];
  p5.text(`head${i}`, x, 100, W, 46, [[{ t: role.toUpperCase(), s: 17, b: true, c: DARK, f: "Segoe UI Semibold" }]], box(null, { bg: c }));
  [["▲  LEARN FIRST", CYAN], ["■  PUT ON THE CV", GOLD], ["●  DEPRIORITISE", PINK]].forEach(([h, hc], j) => {
    p5.text(`r${i}${j}`, x, 154 + j * 166, W, 160, [[{ t: h, s: 12, b: true, c: hc }], [{ t: " ", s: 4 }], [{ t: rec[j], s: 12, c: TEXT }]], box());
  });
});
p5.text("cta", 40, 656, 1200, 50, [[{ t: "Found this useful? Follow for more data-backed career advice.", s: 16, b: true, c: DARK, f: "Segoe UI Semibold" }]], box(null, { bg: GOLD }), "center");

const pages = [p0, p1, p2, p3, p4, p5];
pages.forEach((p) => p.write());
fs.writeFileSync(path.join(PAGES, "pages.json"), JSON.stringify({ $schema: `${SCH}/pagesMetadata/1.0.0/schema.json`, pageOrder: pages.map((p) => p.id), activePageName: "cover" }, null, 2));
console.log("wrote", pages.length, "pages,", pages.reduce((a, p) => a + p.v.length, 0), "visuals");
