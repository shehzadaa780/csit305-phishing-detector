// Builds evidence/CSIT305_Evidence_Pack.docx (insert-ready text for the group report).
// Run: node scripts/build_report_pack.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, BorderStyle, LevelFormat, ImageRun, PageBreak, Footer, PageNumber,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const W = 9026; // A4 content width in DXA with 1" margins
const BLUE = "1F4E79", HEAD_BG = "D9E2F3", NOTE_BG = "FFF4E0", BORDER = "BFBFBF";
const FONT = "Calibri";

const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 21, ...o });
const P = (parts, o = {}) => new Paragraph({
  spacing: { after: 100, line: 276 }, ...o,
  children: (Array.isArray(parts) ? parts : [parts]).map(x => typeof x === "string" ? run(x) : x),
});
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 120 },
  children: [run(t, { bold: true, size: 30, color: BLUE })] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 80 },
  children: [run(t, { bold: true, size: 24, color: BLUE })] });
const bullet = (parts, level = 0) => new Paragraph({ numbering: { reference: "b", level }, spacing: { after: 60 },
  children: (Array.isArray(parts) ? parts : [parts]).map(x => typeof x === "string" ? run(x) : x) });
const B = t => run(t, { bold: true });
const I = t => run(t, { italics: true });

const border = { style: BorderStyle.SINGLE, size: 4, color: BORDER };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(content, width, o = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map(c =>
    c instanceof Paragraph ? c : new Paragraph({ spacing: { after: 40 },
      children: (Array.isArray(c) ? c : [c]).map(x => typeof x === "string" ? run(x, { size: 18, bold: o.bold }) : x) }));
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA },
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined, children: paras });
}
function table(widths, header, rows) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], { bold: true, fill: HEAD_BG })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i])) })),
    ],
  });
}
function note(parts) {
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W],
    rows: [new TableRow({ children: [cell([parts], W, { fill: NOTE_BG })] })] });
}
const caption = t => P([run(t, { italics: true, size: 18 })], { alignment: AlignmentType.CENTER, spacing: { after: 160 } });
const gap = () => P("");
const fill = t => run(`[${t}]`, { size: 18, color: "C00000", italics: true });

const metrics = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "metrics.json")));
const F = metrics.formats;
const fx = (v, d = 3) => Number(v).toFixed(d);
const pct = v => (100 * v).toFixed(1) + "%";

// ------------------------------------------------------------------ content
const children = [];
children.push(new Paragraph({ spacing: { after: 60 }, children: [run("CSIT305 | AI Phishing & Scam Detector", { size: 18, color: "7F7F7F" })] }));
children.push(new Paragraph({ spacing: { after: 80 }, children: [run("Evidence Pack: implementation, testing, contributions and AI-use declaration", { bold: true, size: 36, color: BLUE })] }));
children.push(P([I("Prepared 29 October 2026 alongside prototype v0.2.0. Red bracketed text must be completed by the group. Every number below comes from results/metrics.json in the repository.")]));

children.push(H1("How to use this pack"));
children.push(bullet([B("Part 1 "), run("maps the milestone requirements to what now exists and what the group still has to do.")]));
children.push(bullet([B("Part 2 "), run("is insert-ready text for a new Section 6 of the report. It is written to fit about one IEEE page, because the final paper is limited to six pages including references. Detailed evidence stays in the repository, which the brief allows to be submitted separately.")]));
children.push(bullet([B("Parts 3 and 4 "), run("are the individual contribution table and the GenAI declaration. Only the group can complete them truthfully.")]));
children.push(bullet([B("Part 5 "), run("lists the corrections to the current draft (citations, duplicates, leftover text, sections that the prototype has made out of date).")]));
children.push(gap());
children.push(note([B("Before submitting: "), run("the brief (Section 7 and criterion C4) says each member may be asked to explain the code, distinguish human from AI work, and show how AI output was verified. Much of the prototype was written with AI assistance in one session. Each member should run it, read the modules listed against their name in Part 3, and be able to explain them. Please do not present AI-written parts as your own work.")]));

// ---------------- Part 1
children.push(H1("Part 1. Milestone checklist"));
children.push(table([2300, 3600, 3126], ["Requirement (milestone 6 / 7)", "Now in place", "Still to do by the group"], [
  ["Demonstration that the artefact works", "Working API and web page; recorded live session (evidence/api_demo_transcript.txt); 23/23 automated tests pass", [[fill("Take screenshots of the web page at http://127.0.0.1:8000 with 2-3 examples, add them to evidence/screenshots/")]]],
  ["Version histories", "Two documented versions; v0.1.0 results archived in results/history/v0.1.0", [[fill("Create the GitHub repository and push in several real commits (see README). Each member commits their own changes from now on")]]],
  ["Prototype iterations and design decisions", "Section 6.5 below; 17-entry evidence log (evidence/evidence_log.csv)", [[fill("Add entries for your own future changes, tutor feedback and responses")]]],
  ["Testing / validation incl. results and limitations", "Held-out results for all three formats, 18 edge cases, 40-message challenge set, time-split test, criteria table", [[fill("Brief asks to compare AI-generated and manually written tests where appropriate: each member writes 2-3 tests of their own in tests/test_manual.py and the group compares them")]]],
  ["README.md", "README.md: purpose, architecture, datasets, reproduction steps, results, limitations", "Review and add the repository URL"],
  ["GitHub repository link", "Repository folder ready to push", [[fill("Repository URL")]]],
  ["AI-use declaration", "Draft in Part 4", [[fill("Each member completes their own rows")]]],
  ["Individual contributions", "Table in Part 3 with the attributions visible in the draft", [[fill("Fill missing rows, especially Djamel and sections 1-3.5, 5.1-5.7")]]],
  ["Prompt records", "This chat session is a prompt record", [[fill("Save/share the chat link and the earlier Claude chat shown in reference [15]")]]],
]));

// ---------------- Part 2
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(H1("Part 2. Insert-ready section"));
children.push(note([run("Paste from here. Table and figure numbers continue the report's existing numbering (Table II is already used); renumber if needed.")]));
children.push(H2("6. Implementation, Testing and Results"));
children.push(H2("6.1 Implemented prototype"));
children.push(P([run("A working research prototype (v0.2.0) implements workflow steps 1-8 of Section 4.1 as a locally hosted Python service: a FastAPI REST API (POST /analyze, GET /health) that also serves a simple web page, a pipeline of preprocessing, feature extraction, calibrated classification, risk mapping and explanation, a versioned model registry, and a SQLite audit log that stores no message text. Links are parsed but never opened. No external LLM is called. The code, tests and evidence log are in the project repository " ), fill("GitHub URL"), run(".")]));
children.push(P([run(`Each format has its own model. E-mail and SMS use TF-IDF word and two-word features with logistic regression (linear SVM as comparator). URLs use one logistic regression over character fragments (3-5 characters) and 21 lexical features (length, hyphens, IP host, '@', shortener, punycode, brand misuse); the random forest from Table II is kept as the comparator. Probabilities are calibrated on the validation split and mapped to the 0-39 / 40-69 / 70-100 bands. Explanations list the exact feature contributions (value × coefficient) found in the input, so every warning is traceable to the message itself.`)]));
children.push(H2("6.2 Data"));
children.push(P([run(`E-mail: Nazario phishing [12] versus Enron legitimate e-mails [13] (Enron spam removed), 16,858 after cleaning. SMS: UCI SMS Spam Collection [3], 5,108; this measures spam, not smishing. URL: the phishing and legitimate URL lists of Sahingoz et al. [2], 50,226. Duplicates and near-duplicates were removed (23,349 URLs, 496 e-mails, 464 SMS) and all text was normalised identically for both classes. Splits are 70/15/15 (seed 42), stratified for text and grouped by website for URLs so that no website appears in both training and test data.`)]));
children.push(H2("6.3 Results"));
children.push(P([run("Each model was scored once on a held-out test set not used for training, model selection or calibration (Table III). Recall is given for the high band; false alarms are legitimate items placed in the high band.")]));
const e = F.email.main, s = F.sms.main, u = F.url.main;
children.push(table([3026, 2000, 2000, 2000], ["Criterion (target)", "E-mail", "SMS (spam)", "URL"], [
  ["Test items (phishing / legitimate)", `${e.support.phishing} / ${e.support.legitimate}`, `${s.support.phishing} / ${s.support.legitimate}`, `${u.support.phishing} / ${u.support.legitimate}`],
  ["Recall, high band (≥ 0.90)", fx(e.recall_high), fx(s.recall_high), fx(u.recall_high)],
  ["Recall, high + uncertain (≥ 0.97)", fx(e.recall_high_or_uncertain), fx(s.recall_high_or_uncertain) + " (not met)", fx(u.recall_high_or_uncertain) + " (not met)"],
  ["False alarms in high band (≤ 2%)", pct(e.false_positive_rate_high), pct(s.false_positive_rate_high), pct(u.false_positive_rate_high)],
  ["F1 (≥ 0.85) [95% CI]", `${fx(e.f1)} [${fx(F.email.bootstrap.f1_main_95ci[0])}-${fx(F.email.bootstrap.f1_main_95ci[1])}]`, `${fx(s.f1)} [${fx(F.sms.bootstrap.f1_main_95ci[0])}-${fx(F.sms.bootstrap.f1_main_95ci[1])}]`, `${fx(u.f1)} [${fx(F.url.bootstrap.f1_main_95ci[0])}-${fx(F.url.bootstrap.f1_main_95ci[1])}]`],
  ["Brier score (≤ 0.10)", fx(e.brier), fx(s.brier), fx(u.brier)],
  ["F1 gain over comparator [95% CI]", `+${fx(F.email.bootstrap.f1_main_minus_comparator)} vs SVM`, `${fx(F.sms.bootstrap.f1_main_minus_comparator)} vs SVM`, `+${fx(F.url.bootstrap.f1_main_minus_comparator)} [${fx(F.url.bootstrap.f1_diff_95ci[0])}-${fx(F.url.bootstrap.f1_diff_95ci[1])}] vs RF`],
  ["Precision at 90% recall, 5% phishing (≥ 0.75)", fx(F.email.low_prevalence.precision_at_90_recall_mean, 2), "-", fx(F.url.low_prevalence.precision_at_90_recall_mean, 2)],
  ["Median time, full result (≤ 3 s)", metrics.latency.email.total_ms_median + " ms", metrics.latency.sms.total_ms_median + " ms", metrics.latency.url.total_ms_median + " ms"],
]));
children.push(caption("Table III. Held-out results of prototype v0.2.0 against the evaluation criteria in Section 5.9."));
const img = fs.readFileSync(path.join(ROOT, "results", "figures", "confusion_matrices.png"));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data: img, transformation: { width: 600, height: 194 } })] }));
children.push(caption("Fig. 2. Confusion matrices at the high-risk threshold (risk ≥ 70) on the held-out test sets."));
const ts = metrics.email_time_split, ex = metrics.explanations;
children.push(P([run(`Robustness: an e-mail model trained only on phishing up to 2019 caught ${pct(ts.recall_high_old)} of held-out older phishing and ${pct(ts.recall_high_new)} of 2020-2022 phishing (a ${ts.recall_drop_points}-point drop, within the 5-point target). Explanations: an automated check confirmed that all ${ex.n_cues} cues produced for the challenge set exist in the input, with no unsupported claims, and identical inputs always produced identical cues. User comprehension, rater agreement and the click-through study were not carried out because they require ethics approval.`)]));
children.push(H2("6.4 Challenge set and edge cases"));
const cs = metrics.challenge_set;
children.push(P([run(`To test the "fluent AI-written phishing" edge case (Section 5.8), 40 new messages in a UAE and university context were written with GenAI and labelled by design (20 phishing, 20 legitimate). They were never used to change the models. The detector placed 16 of 20 phishing items in the high band and 18 of 20 in high or uncertain, and flagged 2 of 20 legitimate items. It missed a gift-card request from a "manager" and a "Hi mum, new number" SMS, which contain no link and no typical scam words, and it falsely flagged the real paypal.com website and a genuine bank-statement e-mail. All ${metrics.edge_cases.total} edge cases passed (empty input, broken and IP-address links, '@' links, punycode, shorteners, Arabic and emoji-only text, very long e-mails, missing consent).`)]));
children.push(H2("6.5 Iteration and design decisions"));
children.push(table([1100, 3900, 4026], ["Version", "Finding", "Change and effect"], [
  ["0.1.0", "URL lists differed in scheme and 'www.' between classes; e-mail corpora differed in formatting", "Removed before feature extraction; text normalised identically, so the model judges content rather than dataset artefacts"],
  ["0.1.0", `Random forest URL model: F1 0.854, 5.2% false alarms, precision 0.30 at 5% phishing`, "Three core URL criteria failed; result archived and investigated"],
  ["0.2.0", "66% of URL test items shared a website with training data, contrary to Stage 3", "Split grouped by website; random forest fell to F1 0.803 on unseen websites"],
  ["0.2.0", "Character fragments generalise better to unseen websites", `Hybrid logistic regression adopted: F1 ${fx(u.f1)}, ${pct(u.false_positive_rate_high)} false alarms; random forest kept as comparator`],
  ["0.2.0", "Edge-case failures and unhelpful cues (e.g. 'your')", "Non-URL text rejected, non-English note added, stop-words hidden from cues; 18/18 edge cases pass"],
]));
children.push(caption("Table IV. Main development iterations (full log: evidence/evidence_log.csv)."));
children.push(H2("6.6 Discussion and limitations"));
children.push(P([run("The results support the design choices in Section 5.6: format-specific models behave very differently, and a grouped split changed the URL conclusion completely, which shows why results from different datasets should not be compared directly. The near-perfect e-mail scores are probably optimistic because legitimate e-mails come from one company in 2000-2002; the time-split and challenge results are better guides. The SMS model detects spam rather than smishing. Brand names in real websites cause false alarms, and scams that rely only on social engineering, without links or scam vocabulary, are missed. The text models handle English only. No LLM comparator was run, so the LLM part of the research question is answered from the literature [7], [11] rather than from our own measurements.")]));

// ---------------- Part 3
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(H1("Part 3. Individual contribution statement"));
children.push(P([run("Attributions in the first column are taken from the section headings in the current draft. Everything in red must be confirmed or completed by the group. Do not leave a member without a contribution; the brief allows marks to be moderated individually.")]));
children.push(table([1700, 2400, 2700, 2226], ["Member", "Report sections", "Prototype / evidence work (from now on)", "Evidence (commits, logs)"], [
  ["Djamel Salmi (9079166)", [[fill("Not attributed in the draft - confirm")]], [[fill("e.g. owns preprocess.py and edge-case tests")]], [[fill("commit links")]]],
  ["Shehzad Siddiqui (8983859)", "3.6 Comparison and research gap", [[fill("e.g. owns literature table and Section 6.6 discussion")]], [[fill("commit links")]]],
  ["Imad Rahman (8811131)", "4.1 System workflow; 5.8 Methodology and development stages", [[fill("e.g. owns pipeline.py / api.py and the demo")]], [[fill("commit links")]]],
  ["Abdul Mohimin (8974585)", "4.2 Tools, datasets and stages; 5.9 Evaluation plan", [[fill("e.g. owns evaluate.py and criteria table")]], [[fill("commit links")]]],
  ["Abdallah Al Faqih (8240012)", "4.3 Testing, evaluation and responsible research; 5.8 Failure/edge cases and evidence log", [[fill("e.g. owns edge_cases.csv, evidence log")]], [[fill("commit links")]]],
  ["Unattributed", "1, 2, 3.1-3.5, 5.1-5.7", [[fill("Who wrote these?")]], ""],
]));

// ---------------- Part 4
children.push(H1("Part 4. GenAI and AI-assisted development declaration"));
children.push(P([run("Rows 1-5 describe the AI-assisted build session of 29 October 2026 and are accurate as written. Row 6 is based on the screenshot in reference [15]. Each member must add their own uses in the last rows. Reviewers ask how each output was verified, modified or rejected, so the last column matters most.")]));
children.push(table([1900, 1500, 2600, 3026], ["What", "Tool, date, who prompted", "How AI was used", "How the output was verified / changed / rejected"], [
  ["1. Prototype code (src/phishdetect/), training and evaluation scripts", ["Claude Opus 5.5 (claude.ai), 29 Oct 2026, ", fill("member name")], "Wrote the modules from the architecture in Sections 4-5; inspected the datasets; ran training, evaluation and the live server", "23 automated tests; held-out evaluation; 18 edge cases. Two of the AI's own design choices were rejected after testing (random-forest URL model, random URL split; see Table IV). " ],
  ["2. Unit and integration tests (tests/)", ["Claude Opus 5.5, 29 Oct 2026, ", fill("member")], "Wrote 23 tests", ["All pass (evidence/pytest_output.txt). ", fill("Group to write and compare their own manual tests")]],
  ["3. Challenge set (40 messages) and edge-case list", ["Claude Opus 5.5, 29 Oct 2026, ", fill("member")], "Wrote AI-generated phishing and legitimate messages to test the fluent-phishing edge case (Section 5.8, Stage 1)", "Labels set by design; never used for training or tuning; results reported including failures"],
  ["4. README, evidence log entries EL01-EL17, results tables", ["Claude Opus 5.5, 29 Oct 2026, ", fill("member")], "Drafted from actual run outputs during the session", ["Numbers generated by evaluate.py and checked against results/metrics.json. ", fill("Group review")]],
  ["5. Section 6 text, this pack, review of the draft (Part 5)", ["Claude Opus 5.5, 29 Oct 2026, ", fill("member")], "Drafted Section 6; listed citation and consistency errors", ["Citation [16] figure confirmed against Verizon 2025 DBIR coverage. ", fill("Group to check every correction against the sources")]],
  ["6. Evaluation criteria, Section 5.9", ["Claude (claude.ai), ", fill("date"), ", Abdul"], "Drafted targets and the tiered 'suspicious' band from Abdul's requirements (see [15])", ["Targets grounded in [10], [11]. ", fill("Abdul to describe what he changed")]],
  [[[fill("Other uses, e.g. literature search, paraphrasing, figures")]], [[fill("tool, date, member")]], "", ""],
  [[[fill("Other uses")]], [[fill("tool, date, member")]], "", ""],
]));
children.push(gap());
children.push(P([B("Not AI-generated: "), fill("list what the group wrote without AI, e.g. topic choice, research question, literature selection")]));

// ---------------- Part 5
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(H1("Part 5. Corrections to the current draft"));
children.push(H2("5a. Citations"));
children.push(table([1600, 3700, 3726], ["Where", "Problem", "Change"], [
  ["2.2", "'60% of breaches involve a human element [1]' - [1] is Fette et al.", "Cite a new reference [16]: Verizon, \"2025 Data Breach Investigations Report,\" Verizon Business, 2025. (The 60% figure is from the 2025 edition.)"],
  ["2.2", "GPT-4 click rates 30-44% vs 19-28% cited as [2] (Sahingoz)", "Cite [7] Heiding et al. Check the exact figures against the paper."],
  ["4.1, step 3", "'following Sahingoz et al. [4]'", "Change [4] to [2]"],
  ["5.8.1", "Fette [3], Sahingoz [4], Heiding [2]", "Change to Fette [1], Sahingoz [2], Heiding [7]"],
  ["5.9 heading", "Stray '[12]' (Nazario corpus)", "Remove"],
  ["5.9 text", "'metrics in Section 6' - no Section 6 existed", "Change to 'Section 4.3.1'"],
  ["References [5], [6]", "No authors", "Add the authors from the publisher pages"],
  ["Reference [15]", "A chat screenshot listed as a reference; shows a nickname", "Remove from references; keep the chat as a prompt record in the evidence folder and mention it in the AI declaration"],
  ["New", "Datasets now used", "Add the Sahingoz et al. URL data under [2] (already cited) and keep [12], [13]; [14] PhiUSIIL is now future work"],
]));
children.push(H2("5b. Duplicates, numbering and leftover text"));
children.push(table([1600, 3700, 3726], ["Where", "Problem", "Change"], [
  ["2.3", "Two research questions and two objective lists (4 and 5 objectives)", "Keep one question and one list. Section 5.8 maps to Objectives 1-4, so keep the 4-objective list or update 5.8"],
  ["2.4 and 3.6.2", "'Intended contribution' appears twice; 2.4 still says the gap 'will be refined in the next deliverable'", "Merge into one; delete the stale sentence"],
  ["Before 5.1", "Heading 'Proposed Solution Architecture and Data Flow' appears twice", "Delete the unnumbered copy"],
  ["5.8", "Two sections numbered 5.8", "Renumber 'Failure/Edge Cases and Evidence Log' to 5.10"],
  ["5.1", "'seven-step detection pipeline' but Section 4.1 has 8 steps", "Change to 'eight-step'"],
  ["4.2 table and 4.2.1 note", "'Select documented email corpus' and 'dataset names ... must be filled in' are out of date", "Replace with the datasets in Section 6.2; delete the note"],
  ["4.2.1 vs 5.8", "8 development stages vs 4 stages", "Keep one list and point to it"],
  ["Between [9] and [10]", "'Editorial note: Bibliographic details ... should be checked'", "Delete"],
  ["Figure 1 subtitle", "'proposed design, not an implemented system'", "Redraw or relabel (see 5c)"],
  ["5.9 opening", "Refers to 'a personal project' without explanation", "Delete the comparison or describe it neutrally"],
]));
children.push(H2("5c. Sections the prototype has made out of date"));
children.push(table([1600, 3700, 3726], ["Where", "Draft says", "Change to"], [
  ["5.1, 5.2, Fig. 1, Table II", "Streamlit web UI", "FastAPI serves a simple web page at '/'. Reason: one service to run and test; Streamlit can be added later"],
  ["5.2, Table II", "Random forest for URLs", "Logistic regression on character fragments + lexical features; RF kept as comparator (evidence: Table IV)"],
  ["5.2", "tldextract; LIME/SHAP", "urllib parsing; exact linear contributions (equivalent role for linear models). LIME/SHAP not used"],
  ["5.8", "PhiUSIIL [14] for URLs", "Sahingoz et al. URL data [2]; PhiUSIIL as a future external test set"],
  ["5.8 / 4.2", "Balanced samples for training", "Class-weighted training on the natural class ratio"],
  ["Throughout", "'proposed, not implemented' wording", "Update to describe what was implemented and measured"],
]));
children.push(H2("5d. Typos"));
children.push(bullet("5.8.1: 'Phrases and phrases that are true...' is garbled, and the bullet list runs into the paragraphs."));
children.push(bullet("'it's held-out set' → 'its held-out set' (5.8)."));
children.push(bullet("'explanation of quality' → 'explanation quality' (4.2.1); 'explanation of faithfulness' → 'explanation faithfulness' (3.3)."));
children.push(bullet("Missing full stops at the end of Sections 1 and 2.2."));
children.push(gap());
children.push(note([B("Page limit: "), run("the final paper must fit six IEEE pages including references. The current draft is far longer, so Sections 4-5 will need to be condensed heavily, keeping the detail in the repository and evidence log.")]));

const doc = new Document({
  creator: "CSIT305 group",
  title: "CSIT305 Evidence Pack",
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  numbering: { config: [{ reference: "b", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } },
    { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 260 } } } },
  ] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [run("CSIT305 Evidence Pack · page ", { size: 16, color: "7F7F7F" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "7F7F7F", font: FONT })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(buf => {
  const out = path.join(ROOT, "evidence", "CSIT305_Evidence_Pack.docx");
  fs.writeFileSync(out, buf);
  console.log("wrote", out);
});
