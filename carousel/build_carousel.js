// Builds LinkedIn carousel slides (1080x1350 PNG) from out/powerbi/skill_scores.csv
// Run: node carousel/build_carousel.js   (needs Microsoft Edge for the PNG rendering)
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const ROOT = path.join(__dirname, ".."), OUT = path.join(__dirname, "slides");
fs.mkdirSync(OUT, { recursive: true });

const rows = fs.readFileSync(path.join(ROOT, "out", "powerbi", "skill_scores.csv"), "utf8").replace(/^\uFEFF/, "").trim().split(/\r?\n/).slice(1).map((l) => l.split(","))
  .map(([role, skill, category, type, , , demand, lift, , rank]) => ({ role, skill, category, type, demand: +demand, lift: +lift, rank: +rank }));
const get = (role, skill) => rows.find((r) => r.role === role && r.skill === skill);
const top = (role, type, n) => rows.filter((r) => r.role === role && r.type === type).sort((a, b) => a.rank - b.rank).slice(0, n);
const pct = (v) => `${Math.round(v * 100)}%`;
const ROLES = { "Product Manager": "#8B7BFF", "Project Manager": "#19D3B5", "Data Analyst": "#FF9A3C" };
const TOTAL = 8473, N = 8;

const css = `
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;font-family:'Segoe UI',Arial,sans-serif;color:#F2F5FF;background:#0B1020;position:relative;overflow:hidden}
.glow{position:absolute;border-radius:50%;filter:blur(120px);opacity:.55}
.wrap{position:absolute;inset:0;padding:90px 80px 80px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;font-size:26px;font-weight:700;letter-spacing:3px;color:#9AA6C8}
.kick{font-size:30px;font-weight:800;letter-spacing:4px;color:#FFD166;margin-top:70px}
h1{font-size:112px;line-height:1.02;font-weight:800;margin-top:26px;letter-spacing:-2px}
h2{font-size:80px;line-height:1.05;font-weight:800;margin-top:30px;letter-spacing:-1px}
p.sub{font-size:38px;line-height:1.35;color:#B8C2E0;margin-top:34px}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:700;color:#9AA6C8}
.pill{background:#FFD166;color:#0B1020;padding:20px 38px;border-radius:60px;font-weight:800;font-size:30px}
.card{border-radius:36px;padding:44px 48px;color:#0B1020}
.bar{display:flex;align-items:center;margin-top:30px}
.bar .n{width:420px;font-size:34px;font-weight:600}
.bar .t{flex:1;height:54px;background:#1C2444;border-radius:27px;overflow:hidden}
.bar .f{height:100%;border-radius:27px}
.bar .v{width:120px;text-align:right;font-size:38px;font-weight:800}
.hl{color:#FFD166}
table{border-collapse:separate;border-spacing:8px;margin-top:20px;width:100%}
th{font-size:26px;color:#9AA6C8;font-weight:700;padding:8px}
td.s{font-size:30px;font-weight:600;padding:8px 0}
td.c{height:64px;text-align:center;font-size:32px;font-weight:800;border-radius:16px;width:190px}
`;
const heat = (d) => (d >= 0.65 ? "#FF5C8A" : d >= 0.5 ? "#E04FD0" : d >= 0.3 ? "#7B5CFF" : d >= 0.15 ? "#3D4FB5" : d >= 0.05 ? "#2B3770" : "#1C2444");
const blobs = (a, b) => `<div class="glow" style="width:700px;height:700px;background:${a};top:-250px;right:-250px"></div><div class="glow" style="width:620px;height:620px;background:${b};bottom:-260px;left:-240px"></div>`;
const page = (i, inner, a = "#8B7BFF", b = "#FF9A3C", cta = "Swipe \u2192") => `<!doctype html><meta charset="utf-8"><style>${css}</style><body>${blobs(a, b)}
<div class="wrap"><div class="top"><span>JOB MARKET DATA</span><span>${i} / ${N}</span></div>${inner}<div class="foot"><span>${cta === "" ? "" : "Based on " + TOTAL.toLocaleString() + " real job postings"}</span>${cta ? `<span>${cta}</span>` : ""}</div></div></body>`;

const slides = [];
// 1 hook
slides.push(page(1, `<div class="kick">I READ ${TOTAL.toLocaleString()} JOB POSTINGS</div>
<h1>What do employers <span class="hl">REALLY</span> ask for?</h1>
<p class="sub">Product Manager vs Project Manager vs Data Analyst. The #1 skill for each might surprise you.</p>`));
// 2 the three #1s
slides.push(page(2, `<div class="kick">THE #1 SKILL PER ROLE</div>
${Object.entries(ROLES).map(([r, c]) => { const t = top(r, "Hard", 1)[0]; return `<div class="card" style="background:${c};margin-top:34px"><div style="font-size:28px;font-weight:800;letter-spacing:3px">${r.toUpperCase()}</div><div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:8px"><div style="font-size:64px;font-weight:800;line-height:1.05">${t.skill}</div><div style="text-align:right"><div style="font-size:96px;font-weight:800;line-height:1">${pct(t.demand)}</div><div style="font-size:24px;font-weight:700">of postings</div></div></div></div>`; }).join("")}`, "#19D3B5", "#8B7BFF"));
// 3-5 per role
Object.entries(ROLES).forEach(([r, c], k) => {
  const hard = top(r, "Hard", 5), first = hard[0];
  slides.push(page(3 + k, `<div class="kick" style="color:${c}">${r.toUpperCase()}</div>
<h2>Top 5 hard skills</h2>
${hard.map((s) => `<div class="bar"><div class="n">${s.skill}</div><div class="t"><div class="f" style="width:${Math.round(s.demand * 100)}%;background:${c}"></div></div><div class="v">${pct(s.demand)}</div></div>`).join("")}
<p class="sub" style="margin-top:50px"><b style="color:${c}">${first.skill}</b> is asked in ${pct(first.demand)} of ${r} postings, and ${Math.round(first.lift)}x more often than in the other two roles.</p>`, c, "#FF5C8A"));
});
// 6 communication
const comm = Object.keys(ROLES).map((r) => [r, get(r, "Communication").demand]);
slides.push(page(6, `<div class="kick">THE ONE SKILL EVERYONE WANTS</div>
<h2>Communication</h2>
${comm.map(([r, v]) => `<div class="bar"><div class="n">${r}</div><div class="t"><div class="f" style="width:${Math.round(v * 100)}%;background:${ROLES[r]}"></div></div><div class="v">${pct(v)}</div></div>`).join("")}
<p class="sub" style="margin-top:50px">It is in <b class="hl">${pct(Math.min(...comm.map((x) => x[1])))}-${pct(Math.max(...comm.map((x) => x[1])))}</b> of postings in every role. Expected everywhere, so it will not set you apart. Hard skills do.</p>`, "#FF5C8A", "#8B7BFF"));
// 7 heatmap
const HS = [["SQL", "Data Analyst"], ["Python", "Data Analyst"], ["Product Roadmap", "Product Manager"], ["Product Strategy / GTM", "Product Manager"], ["Budget Management", "Project Manager"], ["PM Certification", "Project Manager"], ["Reporting", null], ["Communication", null]];
slides.push(page(7, `<div class="kick">WHO NEEDS WHAT</div>
<h2>Same market, different skill sets</h2>
<table><tr><th></th>${Object.keys(ROLES).map((r) => `<th style="color:${ROLES[r]}">${r.replace(" ", "<br>")}</th>`).join("")}</tr>
${HS.map(([s]) => `<tr><td class="s">${s}</td>${Object.keys(ROLES).map((r) => { const d = (get(r, s) || { demand: 0 }).demand; return `<td class="c" style="background:${heat(d)}">${pct(d)}</td>`; }).join("")}</tr>`).join("")}</table>`, "#8B7BFF", "#FF5C8A"));
// 8 cta
slides.push(page(8, `<div class="kick">THE TAKEAWAY</div>
<h2>Learn what is <span class="hl" style="white-space:nowrap">role-defining</span>, not just popular</h2>
<p class="sub">${["Product Manager|Product Roadmap, Backlog, Product Strategy", "Project Manager|Budget Management, Reporting, Risk, PM Certification", "Data Analyst|SQL, Data Visualization, Statistics, Python"].map((x) => { const [r, s] = x.split("|"); return `<span style="color:${ROLES[r]};font-weight:800">${r}:</span> ${s}<br><br>`; }).join("")}</p>
<div class="card" style="background:#FFD166;margin-top:20px;font-size:40px;font-weight:800;line-height:1.2">Follow for more data-backed career advice.<div style="font-size:26px;font-weight:600;margin-top:10px">Sources: LinkedIn 2022-25, Indeed/ZipRecruiter 2024. Aggregated, no personal data.</div></div>`, "#FFD166", "#8B7BFF", ""));

const EDGE = ["C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "C:/Program Files/Microsoft/Edge/Application/msedge.exe"].find(fs.existsSync);
slides.forEach((html, i) => {
  const f = path.join(OUT, `slide_${i + 1}.html`), png = path.join(OUT, `slide_${i + 1}.png`);
  fs.writeFileSync(f, html);
  execFileSync(EDGE, ["--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", `--screenshot=${png}`, "--window-size=1080,1350", "file:///" + f.replace(/\\/g, "/")], { stdio: "ignore" });
});
console.log("wrote", slides.length, "slides to", OUT);
