// Builds FiberLens_Executive_Summary.pptx from out/report.json, out/tableau/lift_weekly.csv and docs/incident_notes.json.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const SKILL = process.env.PPTX_SKILL_DIR;
const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));
const ROOT = path.join(__dirname, "..");
const R = JSON.parse(fs.readFileSync(path.join(ROOT, "out", "report.json"), "utf8"));
const NOTES = JSON.parse(fs.readFileSync(path.join(ROOT, "docs", "incident_notes.json"), "utf8"));
const lw = fs.readFileSync(path.join(ROOT, "out", "tableau", "lift_weekly.csv"), "utf8").trim().split("\n").slice(1).map((l) => l.split(","));
const L = R.lift, ch = R.channels.filter((c) => c.channel !== "organic").sort((a, b) => a.cost_per_signup - b.cost_per_signup);
const rc = R.root_cause[0], an = R.anomalies[0], comp = R.competitive, sv = R.survey;
const pct = (x, d = 1) => `${x >= 0 ? "+" : ""}${(x * 100).toFixed(d)}%`;
const money = (x) => "$" + Math.round(x).toLocaleString("en-US");

const THEME = {
  name: "FiberLens", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "16202E", lt1: "FFFFFF", dk2: "14213D", lt2: "EEF3F8", accent1: "14213D", accent2: "D9822B", accent3: "0F766E", accent4: "7F8CA3", accent5: "F0B561", accent6: "C24B3F", hlink: "0F766E", folHlink: "14213D" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "FiberLens Executive Summary";
pres.author = "Christian Kouadio Kouassi";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: "DARK", background: { color: C.text2 }, objects: [], slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4 } });
pres.defineSlideMaster({
  title: "CONTENT", background: { color: C.background1 },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 8.8, h: 0.8, fontSize: 24, bold: true, color: C.text2, fontFace: "Cambria", margin: 0, valign: "top", align: "left" }, text: "" } }],
  slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4 },
});
const card = (s, x, y, w, h, name, fill) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { color: fill || C.background2, width: 0 }, objectName: name });
const txt = (s, t, o) => s.addText(t, { margin: 0, isTextBox: true, ...o });
const chartBase = { showLegend: false, showValue: true, dataLabelFontFace: "+mn-lt", dataLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 11, valAxisHidden: true, valAxisMinVal: 0, valGridLine: { style: "none" }, catGridLine: { style: "none" } };
const note = (s, t) => txt(s, t, { x: 0.6, y: 5.17, w: 8.4, h: 0.25, fontSize: 10, color: C.accent4, objectName: "FootNote" });

// 1 Title
let s = pres.addSlide({ masterName: "DARK" });
txt(s, "FiberLens", { x: 0.7, y: 1.3, w: 8.6, h: 1.0, fontFace: "Cambria", fontSize: 54, bold: true, color: C.background1, objectName: "Title" });
txt(s, "Which broadband marketing works, where to grow, and which numbers to trust", { x: 0.7, y: 2.4, w: 8.2, h: 1.0, fontSize: 22, color: C.background2, objectName: "Subtitle" });
txt(s, "SQL  |  Python  |  Excel  |  Tableau-ready  |  Christian Kouadio Kouassi", { x: 0.7, y: 4.55, w: 8.6, h: 0.4, fontSize: 14, color: C.accent5, objectName: "Byline" });
s.addNotes("FiberLens is a portfolio project. County broadband data is real; Northwind Broadband, its campaigns, orders, competitors and survey are synthetic and labeled as such.");

// 2 Headline numbers
s = pres.addSlide({ masterName: "CONTENT" });
s.addText("Four findings the business can act on", { placeholder: "title" });
const stats = [
  [pct(L.lift), `lift from the direct-mail flight (95% interval ${pct(L.ci_low)} to ${pct(L.ci_high)}); a naive comparison said ${pct(L.naive)}`],
  [money(ch[0].cost_per_signup), `per sign-up through ${ch[0].channel}, the cheapest channel; ${ch[ch.length - 1].channel} costs ${money(ch[ch.length - 1].cost_per_signup)}`],
  [`${Math.round(rc.top_state_share_of_change * 100)}%`, `of the week ${an.week} drop traced to ${rc.top_state}: an outage, not a demand problem`],
  [`${R.opportunity.tiers.find((t) => t.tier === "A").n}`, "counties score Tier A for expansion, ranked on real availability, usage, size and unemployment"],
];
stats.forEach(([big, label], i) => {
  const x = 0.6 + (i % 2) * 4.5, y = 1.4 + Math.floor(i / 2) * 1.75;
  card(s, x, y, 4.2, 1.5, `StatCard${i + 1}`);
  txt(s, big, { x: x + 0.25, y: y + 0.1, w: 3.7, h: 0.7, fontFace: "Cambria", fontSize: 36, bold: true, color: C.accent2, objectName: `StatValue${i + 1}` });
  txt(s, label, { x: x + 0.25, y: y + 0.82, w: 3.7, h: 0.62, fontSize: 12, color: C.text1, objectName: `StatLabel${i + 1}` });
});
note(s, "Campaign data is synthetic. County data is real (Microsoft AI for Good, JHU/Census, BLS).");

// 3 Channel economics
s = pres.addSlide({ masterName: "CONTENT" });
s.addText("Email and search are cheapest per credited sign-up; TV and social cost the most", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Cost per sign-up", labels: ch.slice().reverse().map((c) => c.channel), values: ch.slice().reverse().map((c) => Math.round(c.cost_per_signup)) }],
  { x: 0.6, y: 1.3, w: 5.6, h: 3.8, barDir: "bar", chartColors: ["0F766E"], dataLabelPosition: "outEnd", dataLabelFormatCode: "$#,##0", ...chartBase, objectName: "ChannelChart" });
card(s, 6.5, 1.4, 3.0, 3.6, "ChannelCard");
s.addText([
  { text: "Read it as attributed cost", options: { bold: true, breakLine: true, color: C.text2, fontSize: 15 } },
  { text: "Each order is credited to its last marketing touch in the prior 28 days. Late-journey channels look better under that rule.", options: { breakLine: true } },
  { text: "Before acting", options: { bold: true, breakLine: true, color: C.text2, fontSize: 15 } },
  { text: "Run holdout tests on TV and social before cutting them; only mail has an incrementality read so far.", options: {} },
], { x: 6.65, y: 1.55, w: 2.7, h: 3.4, fontSize: 11.5, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "ChannelNotes" });
note(s, "Sum of spend over sum of credited sign-ups per channel. Synthetic spend and orders.");

// 4 Lift
s = pres.addSlide({ masterName: "CONTENT" });
s.addText(`Mail lifted sign-ups ${pct(L.lift)}; comparing groups head to head hid it`, { placeholder: "title" });
const wk = Array.from({ length: 52 }, (_, i) => i + 1);
const series = (g) => wk.map((w) => Number(lw.find((r) => r[0] === g && Number(r[1]) === w)[4]).toFixed(3) * 1);
s.addChart(pres.charts.LINE, [{ name: "Treated markets", labels: wk, values: series("treated") }, { name: "Holdout markets", labels: wk, values: series("holdout") }],
  { x: 0.6, y: 1.3, w: 5.8, h: 3.8, chartColors: ["0F766E", "7F8CA3"], lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "b", legendFontFace: "+mn-lt", legendFontSize: 11,
    catAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 10, catAxisLabelFrequency: 6, valAxisLabelFontFace: "+mn-lt", valAxisLabelFontSize: 10, valAxisMinVal: 0.3,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" }, showValAxisTitle: true, valAxisTitle: "Orders per 10k people per week", valAxisTitleFontSize: 10, objectName: "LiftChart" });
card(s, 6.7, 1.4, 2.8, 3.6, "LiftCard");
s.addText([
  { text: "Flight: weeks 20 to 31", options: { bold: true, breakLine: true, color: C.text2, fontSize: 14 } },
  { text: `Naive read: ${pct(L.naive)}. The treated markets were better served and behaved differently before any mail went out.`, options: { breakLine: true } },
  { text: "Corrected read", options: { bold: true, breakLine: true, color: C.text2, fontSize: 14 } },
  { text: `${pct(L.lift)} (${pct(L.ci_low)} to ${pct(L.ci_high)}), about ${Math.round(L.incremental_orders).toLocaleString("en-US")} extra orders at ${money(L.cost_per_incremental_order)} each. The simulated truth is ${pct(L.true)}.`, options: {} },
], { x: 6.85, y: 1.55, w: 2.5, h: 3.4, fontSize: 11, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "LiftNotes" });
note(s, "Difference-in-differences on log rates, bootstrap over markets. Synthetic campaign data.");

// 5 Outage
s = pres.addSlide({ masterName: "CONTENT" });
s.addText(`Week ${an.week}: a ${rc.top_state} outage, not a demand problem`, { placeholder: "title" });
s.addChart(pres.charts.LINE, [{ name: "Sign-ups", labels: R.scorecard.map((r) => r.week), values: R.scorecard.map((r) => r.orders) }],
  { x: 0.6, y: 1.3, w: 5.8, h: 3.8, chartColors: ["14213D"], lineSize: 2, lineDataSymbol: "none", showLegend: false, catAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 10, catAxisLabelFrequency: 6,
    valAxisLabelFontFace: "+mn-lt", valAxisLabelFontSize: 10, valAxisMinVal: 2000, valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" }, objectName: "WeeklyChart" });
card(s, 6.7, 1.4, 2.8, 3.6, "OutageCard");
const top3 = rc.by_state.slice(0, 3).map((x) => `${x.st} ${Math.round(x.delta)}`).join(", ");
s.addText([
  { text: `${an.value.toLocaleString("en-US")} sign-ups`, options: { bold: true, breakLine: true, color: C.text2, fontSize: 15 } },
  { text: `The lowest week of the year, flagged by a robust z-score of ${an.z} against its neighbors.`, options: { breakLine: true } },
  { text: "Root cause", options: { bold: true, breakLine: true, color: C.text2, fontSize: 15 } },
  { text: `Largest changes versus the prior four weeks: ${top3}. ${rc.top_state} is ${Math.round(rc.top_state_share_of_change * 100)}% of the total change.`, options: {} },
], { x: 6.85, y: 1.55, w: 2.5, h: 3.4, fontSize: 11, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "OutageNotes" });
note(s, "The outage is planted in the synthetic data; the method finds it without being told.");

// 6 Competition and survey
s = pres.addSlide({ masterName: "CONTENT" });
s.addText("Competitors and customers: two more reads leadership asked for", { placeholder: "title" });
card(s, 0.6, 1.4, 4.3, 3.6, "CompCard");
txt(s, `${Math.round((1 - Math.exp(comp.comp_a)) * 100)}%`, { x: 0.85, y: 1.5, w: 3.8, h: 0.8, fontFace: "Cambria", fontSize: 44, bold: true, color: C.accent2, objectName: "CompValue" });
s.addText([
  { text: "fewer sign-ups where competitor A covers the whole market", options: { bold: true, breakLine: true, color: C.text2, fontSize: 14 } },
  { text: `Estimated across ${comp.n} markets holding availability, usage and marketing exposure constant (log coefficient ${comp.comp_a.toFixed(2)}, 95% interval ${comp.comp_a_ci[0].toFixed(2)} to ${comp.comp_a_ci[1].toFixed(2)}). Competitor B: ${Math.round((1 - Math.exp(comp.comp_b)) * 100)}%.`, options: {} },
], { x: 0.85, y: 2.4, w: 3.8, h: 2.5, fontSize: 12, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "CompNotes" });
card(s, 5.1, 1.4, 4.3, 3.6, "SurveyCard");
txt(s, `${sv.intent_weighted.toFixed(2)} / 5`, { x: 5.35, y: 1.5, w: 3.8, h: 0.8, fontFace: "Cambria", fontSize: 44, bold: true, color: C.accent3, objectName: "SurveyValue" });
s.addText([
  { text: `purchase intent after weighting, not ${sv.intent_unweighted.toFixed(2)}`, options: { bold: true, breakLine: true, color: C.text2, fontSize: 14 } },
  { text: `The 3,000-person panel over-represents under-35s, who are keener. Weighting to the population age mix moves intent by ${(sv.intent_unweighted - sv.intent_weighted).toFixed(2)} and net promoter score from ${sv.nps_unweighted} to ${sv.nps_weighted}.`, options: {} },
], { x: 5.35, y: 2.4, w: 3.8, h: 2.5, fontSize: 12, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "SurveyNotes" });
note(s, "Competitor footprint and survey responses are synthetic; weighting recovers the simulated population value.");

// 7 White space table
s = pres.addSlide({ masterName: "CONTENT" });
s.addText("Where to look next: the largest Tier A counties outside the footprint", { placeholder: "title" });
const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
const rows = [[hdr("County"), hdr("Population"), hdr("Can get service"), hdr("Use it"), hdr("Gap (people)"), hdr("Score")]];
R.opportunity.white_space_top10.slice(0, 8).forEach((w) => rows.push([`${w.county_name}, ${w.st}`, w.pop.toLocaleString("en-US"), `${(w.avail * 100).toFixed(1)}%`, `${(w.usage * 100).toFixed(1)}%`, Math.round(w.gap_pop).toLocaleString("en-US"), w.score.toFixed(3)]));
s.addTable(rows, { x: 0.6, y: 1.3, w: 8.8, colW: [2.9, 1.3, 1.4, 1.0, 1.4, 0.8], fontSize: 11, fontFace: "Calibri", color: "16202E", border: { type: "solid", color: "D5DEDD", pt: 0.75 }, rowH: 0.4, valign: "middle", objectName: "WhiteSpaceTable" });
note(s, "Real data. Gap is population times the share that can get broadband but does not use it. Availability is from Oct 2020.");

// 8 Incidents
s = pres.addSlide({ masterName: "CONTENT" });
s.addText("Six reporting errors caught by tests, each reproduced and then fixed", { placeholder: "title" });
const short = ["Order credit counted twice", "ZIP join multiplied population 43x", "Leading-zero FIPS dropped 317 counties", "Unweighted state averages", "Naive comparison hid the mail lift", "Average of ratios for cost per sign-up"];
const impact = ["+26% orders", "328M became 14.2B", "10% lost unemployment", "TX 83% vs 96%", "-0.6% vs +12.6%", "Email $184 vs $625"];
short.forEach((t, i) => {
  const x = 0.6 + (i % 2) * 4.5, y = 1.3 + Math.floor(i / 2) * 1.25;
  card(s, x, y, 4.3, 1.1, `Inc${i + 1}`);
  txt(s, `INC-${i + 1}  ${impact[i]}`, { x: x + 0.2, y: y + 0.1, w: 3.9, h: 0.35, fontFace: "Cambria", fontSize: 14, bold: true, color: C.accent2, objectName: `IncImpact${i + 1}` });
  txt(s, t, { x: x + 0.2, y: y + 0.5, w: 3.9, h: 0.5, fontSize: 12, color: C.text1, objectName: `IncText${i + 1}` });
});
note(s, "A script re-runs every reproduce and fix commit in a clean checkout: the first fails, the second passes.");

// 9 Real vs synthetic
s = pres.addSlide({ masterName: "CONTENT" });
s.addText("What is real, what is simulated, and what that limits", { placeholder: "title" });
card(s, 0.6, 1.4, 4.3, 3.6, "RealCard");
s.addText([
  { text: "Real", options: { bold: true, breakLine: true, color: C.text2, fontSize: 16 } },
  { text: `${R.data.counties.toLocaleString("en-US")} counties and ${R.data.population.toLocaleString("en-US")} people`, options: { bullet: true, breakLine: true } },
  { text: "Broadband availability and usage (Microsoft AI for Good, Oct 2020)", options: { bullet: true, breakLine: true } },
  { text: "Population (JHU/Census) and 2016 unemployment (BLS)", options: { bullet: true, breakLine: true } },
  { text: "Nine counties lack availability and eleven lack usage; they are excluded, not guessed", options: { bullet: true } },
], { x: 0.8, y: 1.55, w: 3.9, h: 3.3, fontSize: 12, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "RealNotes" });
card(s, 5.1, 1.4, 4.3, 3.6, "SynthCard");
s.addText([
  { text: "Simulated (Northwind Broadband, fictional)", options: { bold: true, breakLine: true, color: C.text2, fontSize: 16 } },
  { text: `${R.data.markets} markets, ${R.data.orders.toLocaleString("en-US")} orders, ${money(R.data.spend)} spend`, options: { bullet: true, breakLine: true } },
  { text: "Campaigns, touches, competitor footprint and the survey", options: { bullet: true, breakLine: true } },
  { text: "True effects are known, so the methods are graded; that shows the method works, not that real campaigns behave this way", options: { bullet: true, breakLine: true } },
  { text: "Last-touch credit is a convention, and no Tableau workbook is included", options: { bullet: true } },
], { x: 5.3, y: 1.55, w: 3.9, h: 3.3, fontSize: 12, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true, objectName: "SynthNotes" });

// 10 Next steps
s = pres.addSlide({ masterName: "DARK" });
txt(s, "Recommended next steps", { x: 0.7, y: 0.6, w: 8.6, h: 0.8, fontFace: "Cambria", fontSize: 34, bold: true, color: C.background1, objectName: "NextTitle" });
const next = [
  ["Repeat the mail test in lower-availability markets", "to see whether the lift holds where service is weaker."],
  ["Run holdouts on TV and social", "before moving budget; last-touch cost alone cannot justify a cut."],
  ["Alert on weekly sign-ups", "using the same robust check that found week 38, with the state breakdown attached."],
  ["Pilot two or three Tier A counties", "outside the footprint, starting with the largest unrealized-demand gaps."],
];
next.forEach(([t, d], i) => {
  const y = 1.65 + i * 0.85;
  txt(s, String(i + 1), { x: 0.7, y, w: 0.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: C.accent5, objectName: `NextNum${i + 1}` });
  s.addText([{ text: t + " ", options: { bold: true, color: C.background1 } }, { text: d, options: { color: C.background2 } }], { x: 1.3, y, w: 8.0, h: 0.7, fontSize: 16, valign: "middle", margin: 0, isTextBox: true, objectName: `NextText${i + 1}` });
});

(async () => {
  const out = path.join(ROOT, "FiberLens_Executive_Summary.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
