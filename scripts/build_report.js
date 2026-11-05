// Builds report/CSIT305_Group_Project_corrected.docx: the group draft with all corrections
// from the review applied, Sections 4-5 updated to the implemented prototype, and a new
// Section 6 with results. Red text = the group must check or complete.
// Run: node scripts/build_report.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, BorderStyle, LevelFormat, ImageRun, PageBreak, Footer, Header, PageNumber,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const W = 9026;
const BLUE = "2F5597", HEAD_BG = "E2EFD9", BORDER = "000000", FONT = "Calibri";
const m = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "metrics.json")));
const F = m.formats, e = F.email.main, s = F.sms.main, u = F.url.main;
const fx = (v, d = 3) => Number(v).toFixed(d);
const pct = v => (100 * v).toFixed(1) + "%";

const R = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 22, ...o });
const red = t => R(t, { color: "C00000", italics: true });
const norm = x => (typeof x === "string" ? R(x) : x);
const P = (parts, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, alignment: AlignmentType.JUSTIFIED, ...o,
  children: (Array.isArray(parts) ? parts : [parts]).map(norm) });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 120 }, children: [R(t, { bold: true, size: 30, color: BLUE })] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 220, after: 100 }, children: [R(t, { bold: true, size: 26, color: BLUE })] });
const H3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 160, after: 80 }, children: [R(t, { bold: true, size: 23 })] });
const LI = (parts, ref = "b") => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 70 },
  children: (Array.isArray(parts) ? parts : [parts]).map(norm) });
const B = t => R(t, { bold: true });
const cap = t => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 }, children: [R(t, { italics: true, size: 19 })] });
const tcap = t => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 80 }, children: [R(t, { size: 19, bold: true })] });

const bd = { style: BorderStyle.SINGLE, size: 4, color: BORDER };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
function cell(c, w, o = {}) {
  const kids = (Array.isArray(c) ? c : [c]).map(x => typeof x === "string" ? R(x, { size: 19, bold: o.bold }) : x);
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, margins: { top: 50, bottom: 50, left: 90, right: 90 },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    children: [new Paragraph({ children: kids })] });
}
function table(widths, header, rows) {
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], { bold: true, fill: HEAD_BG })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i])) }))] });
}
const img = (file, wpx, hpx) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(ROOT, "results", "figures", file)), transformation: { width: wpx, height: hpx } })] });
const brk = () => new Paragraph({ children: [new PageBreak()] });

const C = [];
// ---------------------------------------------------------------- title page
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1800, after: 200 }, children: [R("UNIVERSITY OF WOLLONGONG IN DUBAI", { bold: true, size: 32 })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [R("CSIT305 | Research Paper", { size: 28 })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [R("AI Phishing & Scam Detector", { bold: true, size: 44, color: BLUE })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [R("Group Members", { bold: true, size: 26 })] }));
C.push(new Table({ width: { size: 6000, type: WidthType.DXA }, alignment: AlignmentType.CENTER, columnWidths: [900, 3300, 1800],
  rows: [new TableRow({ children: ["Member", "Full Name", "Student ID"].map((h, i) => cell(h, [900, 3300, 1800][i], { bold: true, fill: HEAD_BG })) }),
    ...[["1", "Djamel Salmi", "9079166"], ["2", "Shehzad Siddiqui", "8983859"], ["3", "Imad Rahman", "8811131"], ["4", "Abdul Mohimin", "8974585"], ["5", "Abdallah Al Faqih", "8240012"]]
      .map(r => new TableRow({ children: r.map((c, i) => cell(c, [900, 3300, 1800][i])) }))] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 }, children: [R("Instructor: Ms. Pradnya Bhagwat", { size: 24 })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [R("Prototype and evidence repository: "), red("[GitHub URL]")] }));
C.push(brk());

// ---------------------------------------------------------------- 1
C.push(H1("1. Topic Selection and Project Proposal"));
C.push(P("Phishing and online scams have become major cybersecurity threats as more people rely on digital communication for everyday activities. Cybercriminals use fake emails, text messages, and websites to trick users into sharing sensitive information, such as passwords, banking details, and personal data. Traditional phishing detection systems often rely on predefined rules and known suspicious patterns, which may struggle to identify new and sophisticated scams."));
C.push(P("Artificial Intelligence (AI) offers a promising approach to improving phishing detection. Machine Learning (ML) and Natural Language Processing (NLP) can analyze message content, identify suspicious language patterns, and recognize potential threats. Large Language Models (LLMs) can also help explain why a message might be dangerous."));
C.push(P("This paper investigates how effectively AI-based approaches can identify phishing and scam attempts in digital messages and URLs, and examines whether understandable explanations could help users interpret potential threats."));

// ---------------------------------------------------------------- 2
C.push(H1("2. Problem Framing, Research Question, Objectives and Contribution"));
C.push(H2("2.1 Problem statement"));
C.push(P("Phishing and online scams remain difficult to identify as attackers adapt their messages and links to evade established safeguards. Rule-based filters and blacklists depend heavily on known indicators, while research into machine learning and natural language processing has examined other ways to recognize suspicious patterns. However, the effectiveness of these approaches cannot be assumed to transfer equally across emails, SMS messages, and URLs. In addition, a detection result alone may not explain to a user why content appears risky. This paper therefore examines a specific research gap: the comparative effectiveness of AI-based phishing detection across different communication formats, alongside the clarity of explanations given for flagged content. The literature review assesses how far previous studies have addressed this combination of detection performance and user-understandable explanations. The paper investigates this gap rather than treating development of a tool as the primary research aim."));
C.push(H2("2.2 Stakeholder need"));
C.push(P("The people that are most affected by scams are everyday internet users, university students and staff, as well as small businesses that lack the expensive security tools large businesses have. Small businesses are especially vulnerable because they often lack a dedicated security team to help employees differentiate legitimate emails from suspicious ones. Across all organizations, 60% of breaches involve a human element, such as clicking a phishing link [15]. Generative AI is making things worse, as large language models can now create convincing phishing emails automatically and at a lower cost, making these attacks more attractive to attackers [7]. In one study, emails written by GPT-4 received click rates of 30-44%, compared to 19-28% for generic phishing emails [7]. Therefore, users need a simple, accessible tool which checks emails, messages, and links for scams and clearly explains why they look suspicious."));
C.push(H2("2.3 Research question and objectives"));
C.push(P("Based on the identified research gap, this paper addresses the following research question:"));
C.push(P([R("How effectively can machine learning, natural language processing and large language models identify phishing and scam attempts across emails, SMS messages and URLs, and provide understandable explanations of the risks?", { italics: true })], { indent: { left: 400, right: 400 } }));
C.push(P("The research objectives are:"));
C.push(LI("Review existing machine learning and natural language processing methods for detecting phishing in emails, SMS messages and URLs.", "n"));
C.push(LI("Examine how large language models have been used to detect suspicious content and explain phishing indicators.", "n"));
C.push(LI("Compare detection performance using measures such as precision, recall, accuracy and F1-score, without treating results from different datasets as directly equivalent.", "n"));
C.push(LI("Assess limitations in cross-format detection and explanation clarity, including privacy, bias and safe use, and identify opportunities for further evaluation.", "n"));
C.push(H2("2.4 Intended contribution"));
C.push(P("The intended contribution of this paper is a structured analysis of AI-based phishing detection methods, with attention to both their detection performance and their ability to provide understandable explanations. By comparing research on machine learning, natural language processing, and large language models, the paper clarifies the strengths and limitations of different approaches for emails, SMS messages, and URLs."));
C.push(P("Concretely, the paper contributes a transparent, reproducible comparison protocol, a modular detector that applies it to emails, SMS messages and URLs, and an explanation-quality rubric. Rather than making tool development the main outcome, the prototype is used to collect evidence. Claims of superiority are made only where supported by held-out test results."));

// ---------------------------------------------------------------- 3
C.push(H1("3. Literature Review and Research Gap"));
C.push(H2("3.1 Feature-based and URL detection"));
C.push(P("Early phishing detection established the usefulness of combining email and link features. Fette et al. [1] introduced PILFER, showing that structural and content signals can support email phishing classification. However, the older email setting does not establish effectiveness for modern SMS messages. Sahingoz et al. [2] applied machine learning and NLP-derived features to phishing URLs and reported 97.98% accuracy on their own URL dataset. This is evidence for URL classification, not for interpreting full email or SMS messages."));
C.push(H2("3.2 SMS spam and smishing"));
C.push(P(["SMS requires direct consideration because short messages often combine urgent language, impersonation, and shortened links. Almeida et al. [3] provided an SMS spam corpus and baseline findings, but spam labels should not be treated automatically as phishing labels. Mahmood and Hameed [4] specifically combined SMS content analysis with URL inspection for smishing detection. Their results demonstrate that SMS-specific detection has already been researched, so a claim that smishing is “largely unexamined” would be inaccurate. A 2024 survey by Al Saidat et al. [5] reviews ML/NLP approaches to SMS spam and smishing, while a 2026 hybrid TF-IDF/fuzzy-feature study [6] ", red("[verify that [6] exists - it could not be found online]"), " offers additional recent SMS-focused evidence. These studies differ in label definitions and dataset composition; headline accuracy cannot be compared without matched evaluation conditions."]));
C.push(H2("3.3 LLM-assisted analysis"));
C.push(P("Heiding et al. [7] investigated both phishing-email generation and detection with large language models. LLMs may recognize persuasive language and produce readable warnings, but generated explanations can be unsupported, inconsistent, or overconfident. Their usefulness therefore requires separate testing of classification performance and explanation faithfulness."));
C.push(H2("3.4 Explainable AI and user understanding"));
C.push(P("Ribeiro et al. [8] introduced LIME, which approximates a classifier locally to show influential features. Lundberg and Lee [9] introduced SHAP, which attributes feature contributions to predictions. Both offer a basis for tracing model signals, but feature importance is not itself proof that a non-specialist understands a warning. Explanations should therefore be checked for evidence alignment, clarity, and comprehension, rather than evaluated only for fluent wording."));
C.push(H2("3.5 Thematic synthesis"));
C.push(P("The literature suggests four complementary strands: email-feature classifiers, URL-feature classifiers, SMS-specific text/link detectors, and interpretable/LLM-assisted explanations. Existing studies establish progress in each strand, but use different data, tasks, and evaluation protocols. The project therefore compares methods within each input type and separately examines whether warnings communicate real, supported risk indicators."));
C.push(H2("3.6 Comparison and Research Gap — Shehzad"));
C.push(tcap("TABLE I. Comparison of Reviewed Studies"));
C.push(table([1900, 2100, 2400, 2626], ["Study", "Format / approach", "Contribution", "Relevant limitation"], [
  ["Fette et al. [1]", "Email; feature-based ML", "Combines multiple email signals", "Older email-only setting"],
  ["Sahingoz et al. [2]", "URL; ML + NLP features", "URL-focused classification", "Not full message interpretation"],
  ["Almeida et al. [3]", "SMS spam corpus", "SMS baseline and data resource", "Spam is not identical to smishing"],
  ["Mahmood & Hameed [4]", "SMS + URL analysis", "Smishing-specific evidence", "Not a controlled cross-format comparison"],
  ["Al Saidat et al. [5]", "SMS; ML/NLP survey", "Maps SMS detection techniques", "Does not itself validate this proposed system"],
  ["Hybrid smishing [6]", "SMS; TF-IDF + fuzzy features", "Recent SMS-focused classifier", "Different dataset and labeling setup"],
  ["Heiding et al. [7]", "Email; LLMs", "LLM attack/detection study", "Explanation comprehension not established"],
  ["Ribeiro et al. [8]", "XAI; LIME", "Local feature explanations", "Not a smishing user study"],
  ["Lundberg & Lee [9]", "XAI; SHAP", "Feature contribution framework", "Not a measure of user understanding"],
]));
C.push(H3("3.6.1 Defensible research gap"));
C.push(P("The gap is not that SMS phishing or explainable AI have never been studied: [4]-[6] and [8]-[9] show otherwise. Instead, the selected literature provides limited directly comparable evidence about (a) conventional ML versus LLM-assisted classification across distinct email, SMS and URL tasks under a documented evaluation protocol and (b) whether the resulting explanations are faithful to detected evidence and understandable to non-specialist users. This is a bounded gap in the reviewed evidence, not a universal claim that no prior work addresses it."));

// ---------------------------------------------------------------- 4
C.push(H1("4. Methodology and Evaluation Plan"));
C.push(H2("4.1 System Workflow — Imad"));
C.push(table([2200, 3600, 3226], ["Step", "Input / operation", "Output or decision"], [
  ["1. Input", "Accept pasted email, SMS or URL; request user consent", "Input type and raw content"],
  ["2. Privacy preprocessing", "Mask e-mail addresses and phone numbers, clean text and extract URLs without visiting them", "Cleaned text and extracted URLs"],
  ["3. Feature extraction", "Text is converted into TF-IDF features. URLs are analysed for character patterns and features such as length, hostname, special characters and misleading words, following Sahingoz et al. [2]", "Text and URL features"],
  ["4. Classification", "Apply format-specific trained baseline; optional LLM comparator", "Predicted probability for the text and/or the URL"],
  ["5. Risk mapping", "Convert calibrated probability to 0-100; apply thresholds", "Low / uncertain / high risk indicator"],
  ["6. Explanation", "Show evidence-backed phrases or URL indicators taken from the model", "Plain-language explanation with cited input cues"],
  ["7. User output", "The label, risk score, explanation and advice are displayed", "Classification result"],
  ["8. Recording", "The result is saved with the input format, response time and model version only when permitted", "Record for evaluation"],
]));
C.push(P("Illustrative example: for the SMS “Your parcel is held. Pay at delivery-update-example.test”, the text classifier detects delivery wording and a call to action, and the URL classifier detects an unofficial-looking domain. The system explains these warning signs in simple terms, without claiming that the website is definitely malicious, and recommends independently opening the official courier website rather than clicking the message link. The implemented prototype gives this message a risk of 99 (Section 6)."));
C.push(P("Risk score design: Each classifier outputs a probability that the input is phishing. These probabilities are calibrated on validation data, so that a score of 0.8 means about 80% of similar inputs are phishing. The risk score is calculated as round(100 × probability of phishing). For messages containing both text and a link, the higher of the two scores is used. Categories: 0-39 low, 40-69 uncertain, 70-100 high. These thresholds were fixed before testing and were not adjusted after seeing test results."));
C.push(H2("4.2 Tools, Datasets and Development Stages — Abdul"));
C.push(table([1900, 3400, 3726], ["Component", "Selection", "Rationale / caveat"], [
  ["Language", "Python 3; pandas; NumPy", "Reproducible data preparation"],
  ["Text models", "scikit-learn TF-IDF + logistic regression; linear SVM comparator", "Transparent baselines"],
  ["URL model", "Logistic regression on character fragments + lexical features; random forest comparator", "Chosen after testing (Section 6.5)"],
  ["Explanation", "Exact linear contributions (feature value × coefficient)", "Cues come only from the input; no LLM wording"],
  ["SMS dataset", "UCI SMS Spam Collection [3]", "Spam benchmark only; not a phishing ground truth"],
  ["Smishing dataset", "Not available for this build", "Smishing evaluation left to future work"],
  ["Email dataset", "Nazario phishing corpus [12] + Enron legitimate e-mails [13]", "Enron spam removed; corpora differ in era (Section 6.6)"],
  ["URL dataset", "Phishing / legitimate URL lists of Sahingoz et al. [2]", "Duplicates removed; split grouped by website"],
  ["Environment", "Git; fixed random seed (42); requirements file; pytest", "Repeatability"],
]));
C.push(H3("4.2.1 Development stages"));
C.push(P("Stage 1: define labels separately for phishing, spam, and benign. Stage 2: verify corpus provenance, license, sample counts and class balance. Stage 3: remove duplicates and near-duplicates, redact personal information and prevent source overlap between training and test data. Stage 4: create 70/15/15 training/validation/test splits. Stage 5: fit format-specific baselines on training data and tune on validation data. Stage 6: calibrate risk scores on validation data. Stage 7: compare an optional LLM classifier using a fixed prompt, model version and identical held-out inputs, subject to privacy approval. Stage 8: evaluate detection and explanation quality; publish methods and limitations. Section 5.8 groups these stages into four development phases."));
C.push(H2("4.3 Testing, Evaluation and Responsible Research — Abdallah"));
C.push(H3("4.3.1 Detection metrics"));
C.push(P("For each format, report the confusion matrix (TP, FP, TN, FN), precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2PR/(P+R), accuracy = (TP+TN)/N, specificity = TN/(TN+FP) and false-positive rate = FP/(FP+TN). Report class support, macro-F1 when relevant, and confidence intervals if feasible. For probabilistic models, assess calibration with Brier score and reliability plots. Never pool unlike tasks into a single misleading headline score."));
C.push(H3("4.3.2 Explanation-quality framework"));
C.push(table([1900, 4000, 3126], ["Metric", "How to measure", "Proposed criterion"], [
  ["Evidence fidelity", "Check whether each warning is supported by actual message/URL features", "Proportion of claims supported"],
  ["Comprehension", "Participants answer what the warning means and what action to take", "% correct across 2-3 questions"],
  ["Clarity", "5-point participant rating of understandable wording", "Median and distribution"],
  ["Actionability", "Rubric: identifies risk cue and safe next action", "0-2 score by two raters"],
  ["Consistency", "Repeat identical inputs with fixed settings; compare labels and cues", "Agreement percentage"],
  ["Unsupported claims", "Count explanations asserting unverified facts", "Rate per 100 warnings"],
]));
C.push(P("Suggested user evaluation: recruit consenting adult volunteers if institutional approval permits; randomize plain prediction versus prediction plus explanation; ask the same comprehension questions; report group-level scores and avoid collecting names or real private messages. If user testing is not approved, perform a clearly labeled expert rubric evaluation instead, and do not claim demonstrated user comprehension."));
C.push(H3("4.3.3 Responsible research"));
C.push(P("Use licensed or permissioned datasets and minimize personal data. Do not send raw emails, SMS content, or credentials to external LLM APIs without approval and a lawful basis. Never automatically open suspicious links. Consider dialects, multilingual texts, short URLs and dataset shift. A false negative may expose users to fraud; a false positive may wrongly block legitimate communication. Provide uncertainty messaging and make clear the system is decision support, not a guarantee of safety."));
C.push(H3("4.3.4 Success criteria and limitations"));
C.push(P("Compare baselines using held-out data and evaluation choices fixed in advance. The goals are to achieve high recall without unacceptable false-positive rates and to demonstrate evidence-aligned explanations. Limits include sample bias, outdated attacks, changing URLs, domain drift, potential LLM hallucinations, and the distinction between SMS spam and phishing."));

// ---------------------------------------------------------------- 5
C.push(H1("5. Solution Architecture and Data Flow"));
C.push(H2("5.1 Architecture overview"));
C.push(P("The system is a modular, locally hosted Python service that classifies a pasted email, SMS or URL as phishing or benign, converts the calibrated probability into a 0-100 risk score, and explains the warning using cues that actually appear in the input. It is organised into four parts: (1) a presentation layer (a web page served by the API); (2) an application/API layer (FastAPI) that runs the eight-step pipeline from the System Workflow section; (3) storage (a versioned model registry and a de-identified audit log); and (4) an offline training and evaluation pipeline that produces the models the API loads. An external LLM API remains an optional, privacy-gated component; it was not used in the implemented version."));
C.push(img("architecture.png", 600, 318));
C.push(cap("Figure 1. Solution architecture as implemented (v0.2.0). Numbered steps correspond to the System Workflow (Section 4.1)."));
C.push(H2("5.2 Key components"));
C.push(table([1800, 2200, 2900, 2126], ["Component", "Technology", "Responsibility", "Interface"], [
  ["Web page", "HTML + JavaScript served by FastAPI", "Collects input type, text and consent; displays label, risk band, cited cues and safe next step", "Calls POST /analyze (JSON)"],
  ["REST API", "FastAPI, Uvicorn", "Single entry point; validates request, runs pipeline, returns result", "POST /analyze, GET /health"],
  ["1 Intake & router", "Python", "Rejects requests without consent; routes to email, SMS or URL path", "Internal function call"],
  ["2 Privacy preprocessor", "Python regex, html, urllib.parse", "Masks e-mail addresses and phone numbers, normalises text, parses URLs without visiting them", "Internal"],
  ["3 Feature extraction", "scikit-learn TfidfVectorizer; custom URL features", "Builds TF-IDF vectors, URL character n-grams and 21 lexical URL features", "Loads fitted vectorisers from registry"],
  ["4 Classifiers", "scikit-learn LogisticRegression (comparators: LinearSVC, RandomForest)", "One model per format (email, SMS, URL)", "Loads models from registry"],
  ["5 Calibration & risk mapper", "scikit-learn CalibratedClassifierCV", "Calibrated P(phishing) → Risk = round(100 × P) → low / uncertain / high", "Loads calibrators and thresholds"],
  ["6 Explanation engine", "Model coefficients", "Identifies the input cues driving the score and fills a plain-language template", "Internal"],
  ["7 Response builder", "Python / Pydantic", "Assembles label, score, uncertainty note, cues and advice", "JSON response"],
  ["Model registry", "joblib files + registry.json", "Stores versioned vectorisers, models, calibrators, thresholds", "Read at API start-up"],
  ["Audit log", "SQLite", "Stores model version, label, score and flags; no raw message text", "Written after each request if permitted"],
  ["Offline pipeline", "pandas, NumPy, scikit-learn, Git", "Data preparation, training, calibration, evaluation; exports models", "Writes to model registry"],
]));
C.push(H2("5.3 Runtime data flow (one request)"));
C.push(table([700, 2500, 3300, 2526], ["Step", "From → To", "Data passed", "Format / interface"], [
  ["0", "User → Web page → REST API", "Input type, raw text, consent flag", "HTTP POST /analyze, JSON"],
  ["1", "Intake → Privacy preprocessor", "Raw text + confirmed type", "Python object"],
  ["2", "Preprocessor → Feature extraction", "Sanitised text; extracted URLs", "Python object"],
  ["3", "Feature extraction → Classifier", "Sparse TF-IDF vector and/or URL feature vector", "SciPy sparse matrix"],
  ["4", "Classifier → Calibration & risk", "Raw class score", "Float"],
  ["5", "Risk mapper → Explanation engine", "Calibrated probability, 0-100 score, risk band", "Float, int, string"],
  ["6", "Explanation engine → Response builder", "Top cues found in the input + plain-language text", "List of objects, string"],
  ["7", "Response builder → API → Web page", "Label, risk, band, cues, advice, model_version", "JSON response"],
  ["8", "API → Audit log", "Model version, label, score, flags (no raw text)", "SQLite insert"],
]));
C.push(H2("5.4 Example API contract"));
C.push(P([B("Request: "), R("POST /analyze  { \"type\": \"sms\", \"text\": \"Your parcel is held. Pay at delivery-update-example.test\", \"consent\": true }", { font: "Consolas", size: 19 })]));
C.push(P([B("Response (abridged, actual output of v0.2.0): "), R("{ \"label\": \"phishing\", \"risk\": 99, \"band\": \"high\", \"explanation\": \"This looks risky because: call to action (click / call / reply); parcel or delivery; the website ends in an uncommon domain extension; the website name contains several hyphens.\", \"advice\": \"Do not click links, reply or share details. Contact the organisation through its official website or phone number that you look up yourself.\", \"model_version\": \"sms-v0.2.0+url-v0.2.0\" }", { font: "Consolas", size: 19 })]));
C.push(H2("5.5 Dependencies"));
C.push(LI("Runtime: Python 3, FastAPI + Uvicorn, scikit-learn, NumPy/SciPy, joblib, SQLite."));
C.push(LI("Offline: pandas, NumPy, scikit-learn, matplotlib, pytest, Git, requirements.txt and a fixed random seed."));
C.push(LI("Data: the API depends on the model registry, so no prediction is served until a trained, calibrated, versioned model has been exported."));
C.push(LI("External (optional): LLM API, used only with privacy approval; the core system works fully without it."));
C.push(H2("5.6 Design decisions"));
C.push(LI([B("Separate model per format: "), R("email, SMS and URL are evaluated independently, so results are not pooled into one misleading score.")]));
C.push(LI([B("Links are parsed, never visited: "), R("URL features come from the string alone, avoiding risk to the system and the user.")]));
C.push(LI([B("Explanations come from the model: "), R("cues are the exact contributions of features present in the input, which rules out unsupported claims.")]));
C.push(LI([B("Offline/online split: "), R("training and evaluation are reproducible scripts; the API only loads versioned artefacts, so each decision is traceable to a model version.")]));
C.push(LI([B("Privacy by default: "), R("e-mail addresses and phone numbers are masked before features or logging; the audit log stores no raw message text.")]));
C.push(H2("5.7 Technology Choices and Justification"));
C.push(P("The detector's major technology is AI-based text classification, combining machine learning (ML) and natural language processing (NLP). Supporting technologies are explainable-AI methods and a locally hosted web service (FastAPI). Table II summarises each choice and the alternative considered."));
C.push(tcap("TABLE II. Technology Choices and Alternatives"));
C.push(table([2000, 2500, 1900, 2626], ["Choice", "Why it fits the problem", "Alternative considered", "Decision"], [
  ["TF-IDF with logistic regression (email, SMS)", "Transparent; coefficients show which words drive a verdict, supporting evidence-based explanations", "Fine-tuned transformer (e.g. BERT)", "Deferred: needs more labelled data and compute, and is harder to explain; a possible future comparison"],
  ["Logistic regression on URL character fragments + lexical features", "Generalised best to unseen websites in our tests; still fully explainable", "Random forest on lexical features [2]", `Replaced after testing: F1 0.803 on unseen websites, against ${fx(u.f1)} (Section 6.5); kept as comparator`],
  ["", "", "Blacklist lookup only", "Rejected: depends on known indicators and misses newly created links"],
  ["Model-coefficient explanations", "Trace each prediction back to input features exactly", "LLM-generated explanations alone; LIME / SHAP [8], [9]", "LLM rejected as sole method (may assert unsupported claims). LIME/SHAP unnecessary for linear models, whose contributions are exact"],
  ["LLM as optional comparator", "Allows comparison with LLM-based detection as studied in [7]", "LLM as the main detector", "Rejected for the core system: raw messages would be sent to external APIs, with added cost and latency. Not run in this version"],
  ["Locally hosted FastAPI service with a simple web page, model registry and SQLite audit log", "Keeps messages on the local machine, one service to run and test, and each decision traceable to a model version", "Streamlit front end; cloud-hosted service", "Streamlit deferred (an extra service to run); cloud rejected for privacy and reproducibility"],
]));
C.push(P("These choices favor transparency and reproducibility over peak accuracy. A limitation is that classical models trained on older data may perform worse on fluent, LLM-written phishing, which the evaluation tests directly (Section 6.4)."));
C.push(H2("5.8 Methodology and Development Stages — Imad"));
C.push(P("This study adopts a comparative evaluation design. The group built a locally hosted research prototype that applies the same detection and explanation steps to emails, SMS messages, and URLs. The prototype is not the aim of the project. It is a way of collecting evidence to answer the research question."));
C.push(P("The study has three comparisons. The first is the type of format. Separate models are trained and tested for emails, SMS messages, and URLs, and each goes through the same steps of preparation and evaluation. This shows whether detection results change with the format, something the reviewed studies did not test under similar conditions. The second comparison is between methods. Each baseline is compared with a comparator model on identical held-out inputs; an LLM comparator, if approved, would be run the same way with a fixed prompt and model version. Heiding et al. [7] reported mixed results for LLM-based detection, so this comparison would check whether an LLM improves over simpler models. The third comparison looks at explanations. Participants, or expert raters if user testing is not approved, are shown either the risk band or the risk band with an explanation to see whether the explanation helps them understand the warning."));
C.push(P("The datasets match those shown in Section 4.2. For emails, phishing messages are taken from the Nazario phishing corpus [12] and legitimate messages from the Enron email corpus [13]. For SMS, the UCI SMS Spam Collection [3] is used as a spam benchmark; a phishing-labelled smishing corpus of the kind used in [4], [6] remains future work. For URLs, the phishing and legitimate URL lists released with Sahingoz et al. [2] are used; PhiUSIIL [14] is a candidate external test set. Before each dataset was used, the labels, size and source were checked and recorded in the evidence log. Training uses class weighting on the natural class ratio, and an additional test with about 5% phishing is used for the precision criterion in the evaluation plan [10]."));
C.push(P("Development happened in four phases, which group the eight stages of Section 4.2.1:"));
C.push(LI([B("Data preparation (Stages 1-4). "), R("Labels are checked, duplicate items and personal details are removed, and each dataset is split into training, validation and test sets in a 70/15/15 ratio. A small set of AI-generated phishing examples was also written to check the edge case of fluent, LLM-written messages.")], "n2"));
C.push(LI([B("Model development (Stages 5-6). "), R("The format-specific baselines are trained, their probabilities are calibrated on the validation data, and each probability is turned into a risk score in the low (0-39), uncertain (40-69) or high (70-100) band.")], "n2"));
C.push(LI([B("Explanation integration. "), R("Each prediction is linked to the input features that influenced it most and turned into a plain-language explanation.")], "n2"));
C.push(LI([B("Evaluation and iteration (Stages 7-8). "), R("Each model is tested once on its held-out set using the criteria in Section 5.9, and this result is reported. Mistakes are recorded in the evidence log, and the model is retested after any changes, which is recorded separately to show improvements (Section 6.5).")], "n2"));
C.push(P("These phases follow the research objectives. The review of existing methods guided the baseline models (Objective 1), and the literature review, together with the optional LLM comparison, addresses how LLMs detect and explain phishing (Objective 2). Testing each format separately allows performance to be compared across emails, SMS messages, and URLs, alongside results reported in previous studies (Objective 3). Finally, the explanation evaluation and reported issues address weaknesses across formats and the clarity of explanations (Objective 4)."));
C.push(H2("5.9 Evaluation Plan and Measurable Criteria — Abdul"));
C.push(P("Emails, SMS messages, and URLs are evaluated separately, and results from different formats are not combined into one overall score. Each model is tested once on a held-out test set that was not used for training or threshold tuning, and baseline models and comparators are run on identical inputs."));
C.push(P("Using the risk bands from the system workflow (0-39 low, 40-69 uncertain, 70-100 high), the detector is not limited to a yes/no answer. Messages that are less likely but still possibly phishing fall into the uncertain band and are shown to the user as “suspicious – check before acting”. This acts as a safety net: the high band must catch most phishing on its own, and the high and uncertain bands together must catch almost all of it."));
C.push(P("Real inboxes contain far more legitimate messages than phishing, so a detector that looks accurate on a balanced dataset can still raise many false alarms in practice [10]. For this reason, the false-alarm target is stricter than it would be on balanced data. The criteria below build on the metrics in Section 4.3.1 and are targets set before testing; results are reported in Section 6."));
C.push(P("To keep the evaluation manageable, the criteria are split into two groups. Core criteria are the ones the detector is judged on, and all of them are expected to be measured. Extended criteria are optional: they give direction for deeper evaluation and are only attempted if time, data and ethics approval allow. Not attempting an extended criterion, or not meeting it, does not count as a failure of the project, but it is noted in the limitations."));
C.push(P([B("Core criteria")]));
C.push(table([2300, 3800, 2926], ["Criterion", "How it is measured", "Target"], [
  ["Catching phishing", "Recall of the high-risk band (70-100), per format", "≥ 0.90"],
  ["Suspicious safety net", "Recall when high and uncertain bands (40-100) are counted together", "≥ 0.97"],
  ["Avoiding false alarms", "Share of legitimate messages placed in the high-risk band", "≤ 2%"],
  ["Overall balance", "F1-score on the held-out test set, per format", "≥ 0.85"],
  ["Reliable risk score", "Brier score of calibrated probabilities", "≤ 0.10"],
  ["Baseline vs comparator", "Difference in F1 on identical held-out inputs", "Reported with 95% confidence interval"],
  ["Response time", "Time to classify / time to show full result with explanation", "≤ 0.5 s / ≤ 3 s"],
  ["User understanding", "Participants correctly state the risk and the safe next action", "≥ 70% correct"],
]));
C.push(P([B("Extended criteria (optional)")], { spacing: { before: 160, after: 80 } }));
C.push(table([2300, 3800, 2926], ["Criterion", "How it is measured", "Target"], [
  ["Uncertain-band load", "Share of legitimate messages placed in the uncertain band", "≤ 10%"],
  ["Precision in realistic conditions", "Precision at 90% recall on a test set with about 5% phishing [10]", "≥ 0.75"],
  ["Robustness to new attacks", "Drop in recall when trained on older data and tested on newer data (time-based split) [10]", "≤ 5 percentage points"],
  ["Explanation accuracy", "Share of warning claims supported by real message or URL features", "≥ 85%"],
  ["Rater agreement", "Cohen's kappa between the two raters", "≥ 0.60"],
  ["Protective effect", "Click-through rate on phishing links after a warning, in a simulated inbox task [11]", "≤ 10%"],
]));
C.push(P("Recall is given priority over accuracy, because a missed phishing message can cause more harm than a false alarm. The uncertain band allows the detector to stay cautious without flooding users with high-risk warnings. The extended click-through target is based on a controlled study in which LLM-generated feature-based warnings led to a click-through rate of about 9% [11]. If a format does not meet its targets, the result is reported as a limitation rather than adjusted after testing. All evaluation settings (dataset version, data split, random seed, thresholds and model version) are recorded so the results can be repeated.", { spacing: { before: 160, after: 120 } }));
C.push(H2("5.10 Failure/Edge Cases and Evidence Log — Abdallah"));
C.push(H3("5.10.1 Failure and edge-case testing"));
C.push(P("The detector is subjected to failure and edge-case testing to find its weaknesses when analysing emails, SMS messages and URLs. Building on Fette et al. [1], Sahingoz et al. [2] and Heiding et al. [7], tests target situations where the detector may misclassify suspicious or legitimate material:"));
C.push(LI([B("False positives: "), R("legitimate messages that use urgent words, or unfamiliar but genuine links, may be flagged as phishing.")]));
C.push(LI([B("False negatives: "), R("phishing written in natural, fluent language and formatting may escape detection.")]));
C.push(LI([B("Short messages: "), R("SMS messages give the model little information, which may cause errors.")]));
C.push(LI([B("Modified URLs: "), R("shortened links, look-alike domains (punycode), '@' tricks and unusual characters may be used to evade detection.")]));
C.push(LI([B("AI-generated phishing: "), R("messages written by LLMs may be harder to identify.")]));
C.push(LI([B("Invalid input: "), R("empty messages, broken URLs, non-English and symbol-only text, very long e-mails and missing consent are tested to make sure the system behaves correctly.")]));
C.push(H3("5.10.2 Evidence log"));
C.push(P("An evidence log records how the system performs and what improvements are made. Each entry includes the input type, expected result, actual result, identified issue, corrective action and the result after the change. Evidence also includes screenshots of detection results, test-case records, performance measurements and documented changes to the system. The log is kept in the project repository (evidence/evidence_log.csv)."));
C.push(H3("5.10.3 Evaluation and improvement"));
C.push(P("The collected evidence is used to judge the reliability of the detector and the improvements needed. Comparing the initial and updated test results shows whether changes improved detection and reduced misclassifications. This supports clear, repeatable evaluation and responsible development of AI."));

// ---------------------------------------------------------------- 6
C.push(H1("6. Implementation, Testing and Results"));
C.push(H2("6.1 Implemented prototype"));
C.push(P(["A working research prototype (v0.2.0) implements workflow steps 1-8 as a locally hosted Python service (Figure 1). Each format has its own model. Email and SMS use TF-IDF word and two-word features with logistic regression (linear SVM as comparator). URLs use one logistic regression over character fragments (3-5 characters) and 21 lexical features (length, hyphens, IP host, '@', shortener, punycode, brand misuse); the random forest of the original design is kept as the comparator. Probabilities are calibrated on the validation split and mapped to the three bands. The code, tests, evidence log and reproduction instructions are in the project repository ", red("[GitHub URL]"), "."]));
C.push(H2("6.2 Data"));
C.push(P("Email: Nazario phishing [12] against Enron legitimate e-mails [13] (Enron spam removed), 16,858 after cleaning. SMS: UCI SMS Spam Collection [3], 5,108; this measures spam, not smishing. URL: the phishing and legitimate URL lists of Sahingoz et al. [2], 50,226. Duplicates and near-duplicates were removed (23,349 URLs, 496 e-mails, 464 SMS) and all text was normalised identically for both classes. Splits are 70/15/15 (seed 42), stratified for text and grouped by website for URLs so that no website appears in both training and test data."));
C.push(H2("6.3 Results"));
C.push(P("Each model was scored once on a held-out test set not used for training, model selection or calibration (Table III). Recall is given for the high band; false alarms are legitimate items placed in the high band."));
C.push(tcap("TABLE III. Held-out Results of Prototype v0.2.0"));
C.push(table([3026, 2000, 2000, 2000], ["Criterion (target)", "Email", "SMS (spam)", "URL"], [
  ["Test items (phishing / legitimate)", `${e.support.phishing} / ${e.support.legitimate}`, `${s.support.phishing} / ${s.support.legitimate}`, `${u.support.phishing} / ${u.support.legitimate}`],
  ["Recall, high band (≥ 0.90)", fx(e.recall_high), fx(s.recall_high), fx(u.recall_high)],
  ["Recall, high + uncertain (≥ 0.97)", fx(e.recall_high_or_uncertain), fx(s.recall_high_or_uncertain) + " (not met)", fx(u.recall_high_or_uncertain) + " (not met)"],
  ["False alarms in high band (≤ 2%)", pct(e.false_positive_rate_high), pct(s.false_positive_rate_high), pct(u.false_positive_rate_high)],
  ["F1 (≥ 0.85) [95% CI]", `${fx(e.f1)} [${fx(F.email.bootstrap.f1_main_95ci[0])}-${fx(F.email.bootstrap.f1_main_95ci[1])}]`, `${fx(s.f1)} [${fx(F.sms.bootstrap.f1_main_95ci[0])}-${fx(F.sms.bootstrap.f1_main_95ci[1])}]`, `${fx(u.f1)} [${fx(F.url.bootstrap.f1_main_95ci[0])}-${fx(F.url.bootstrap.f1_main_95ci[1])}]`],
  ["Brier score (≤ 0.10)", fx(e.brier), fx(s.brier), fx(u.brier)],
  ["F1 gain over comparator [95% CI]", `+${fx(F.email.bootstrap.f1_main_minus_comparator)} vs SVM`, `${fx(F.sms.bootstrap.f1_main_minus_comparator)} vs SVM`, `+${fx(F.url.bootstrap.f1_main_minus_comparator)} [${fx(F.url.bootstrap.f1_diff_95ci[0])}-${fx(F.url.bootstrap.f1_diff_95ci[1])}] vs RF`],
  ["Precision at 90% recall, 5% phishing (≥ 0.75)", fx(F.email.low_prevalence.precision_at_90_recall_mean, 2), "-", fx(F.url.low_prevalence.precision_at_90_recall_mean, 2)],
  ["Median time, full result (≤ 3 s)", m.latency.email.total_ms_median + " ms", m.latency.sms.total_ms_median + " ms", m.latency.url.total_ms_median + " ms"],
]));
C.push(img("confusion_matrices.png", 600, 194));
C.push(cap("Figure 2. Confusion matrices at the high-risk threshold (risk ≥ 70) on the held-out test sets."));
const ts = m.email_time_split, ex = m.explanations;
C.push(P(`Robustness: an email model trained only on phishing up to 2019 caught ${pct(ts.recall_high_old)} of held-out older phishing and ${pct(ts.recall_high_new)} of 2020-2022 phishing, a ${ts.recall_drop_points}-point drop within the 5-point target. Explanations: an automated check confirmed that all ${ex.n_cues} cues produced for the challenge set exist in the input, with no unsupported claims, and identical inputs always produced identical cues. User comprehension, rater agreement and the click-through study were not carried out because they require ethics approval.`));
C.push(H2("6.4 Challenge set and edge cases"));
C.push(P(`To test the fluent, AI-written phishing edge case (Section 5.10), 40 new messages in a UAE and university context were written with GenAI and labelled by design (20 phishing, 20 legitimate). They were never used to change the models. The detector placed 16 of 20 phishing items in the high band and 18 of 20 in high or uncertain, and flagged 2 of 20 legitimate items. It missed a gift-card request from a "manager" and a "Hi mum, new number" SMS, which contain no link and no typical scam words, and it falsely flagged the real paypal.com website and a genuine bank-statement email. All ${m.edge_cases.total} edge cases passed (empty input, broken and IP-address links, '@' links, punycode, shorteners, Arabic and emoji-only text, very long emails, missing consent).`));
C.push(H2("6.5 Iteration and design decisions"));
C.push(tcap("TABLE IV. Main Development Iterations"));
C.push(table([1100, 3900, 4026], ["Version", "Finding", "Change and effect"], [
  ["0.1.0", "URL lists differed in scheme and 'www.' between classes; email corpora differed in formatting", "Removed before feature extraction; text normalised identically, so the model judges content rather than dataset artefacts"],
  ["0.1.0", "Random forest URL model: F1 0.854, 5.2% false alarms, precision 0.30 at 5% phishing", "Three core URL criteria failed; result archived and investigated"],
  ["0.2.0", "66% of URL test items shared a website with training data, contrary to Stage 3", "Split grouped by website; random forest fell to F1 0.803 on unseen websites"],
  ["0.2.0", "Character fragments generalise better to unseen websites", `Hybrid logistic regression adopted: F1 ${fx(u.f1)}, ${pct(u.false_positive_rate_high)} false alarms; random forest kept as comparator`],
  ["0.2.0", "Edge-case failures and unhelpful cues (e.g. 'your')", "Non-URL text rejected, non-English note added, common words hidden from cues; all edge cases pass"],
]));
C.push(H2("6.6 Discussion and limitations"));
C.push(P("The results support the design choices in Section 5.6: format-specific models behave differently, and a grouped split changed the URL conclusion completely, which shows why results from different datasets should not be compared directly (Section 3.2). The near-perfect email scores are probably optimistic because legitimate emails come from one company in 2000-2002; the time-split and challenge results are better guides. The SMS model detects spam rather than smishing. Brand names in real websites cause false alarms, and scams that rely only on social engineering, without links or scam vocabulary, are missed. The text models handle English only. No LLM comparator was run, so the LLM part of the research question is answered from the literature [7], [11] rather than from our own measurements. Future work: a phishing-labelled SMS corpus, modern legitimate email data, an approved LLM comparison, and the user-comprehension study."));

// ---------------------------------------------------------------- references
C.push(H1("References"));
const refs = [
  "[1] I. Fette, N. Sadeh, and A. Tomasic, “Learning to detect phishing emails,” in Proc. WWW, 2007, pp. 649–656, doi: 10.1145/1242572.1242660.",
  "[2] O. K. Sahingoz, E. Buber, O. Demir, and B. Diri, “Machine learning based phishing detection from URLs,” Expert Systems with Applications, vol. 117, pp. 345–357, 2019, doi: 10.1016/j.eswa.2018.09.029.",
  "[3] T. A. Almeida, J. M. Gómez Hidalgo, and A. Yamakami, “Contributions to the study of SMS spam filtering: New collection and results,” in Proc. DocEng, 2011, pp. 259–262, doi: 10.1145/2034691.2034742.",
  "[4] A. R. Mahmood and S. M. Hameed, “A smishing detection method based on SMS contents analysis and URL inspection using Google engine and VirusTotal,” Iraqi Journal of Science, vol. 64, no. 10, pp. 6276–6291, 2023, doi: 10.24996/ijs.2023.64.10.41.",
  "[5] M. R. Al Saidat, S. Y. Yerima, and K. Shaalan, “Advancements of SMS spam detection: A comprehensive survey of NLP and ML techniques,” Procedia Computer Science, vol. 244, pp. 248–259, 2024, doi: 10.1016/j.procs.2024.10.198.",
];
refs.forEach(r => C.push(P(r, { alignment: AlignmentType.LEFT, spacing: { after: 80 } })));
C.push(P([R("[6] "), red("[Authors], "), R("“Machine learning-based smishing detection using fuzzy logic and TF-IDF feature engineering,” Franklin Open, vol. 14, art. 100506, 2026, doi: 10.1016/j.fraope.2026.100506. "), red("[Could not be found online - verify it exists and add authors, or replace it]")], { alignment: AlignmentType.LEFT, spacing: { after: 80 } }));
[
  "[7] F. Heiding, B. Schneier, A. Vishwanath, J. Bernstein, and P. S. Park, “Devising and detecting phishing emails using large language models,” IEEE Access, vol. 12, pp. 42131–42146, 2024, doi: 10.1109/ACCESS.2024.3375882.",
  "[8] M. T. Ribeiro, S. Singh, and C. Guestrin, “‘Why should I trust you?’: Explaining the predictions of any classifier,” in Proc. KDD, 2016, pp. 1135–1144, doi: 10.1145/2939672.2939778.",
  "[9] S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting model predictions,” in Advances in Neural Information Processing Systems, vol. 30, 2017.",
  "[10] T. Dalton et al., “PhreshPhish: A real-world, high-quality, large-scale phishing website dataset and benchmark,” arXiv:2507.10854, 2025.",
  "[11] F. M. Cau, G. Desolda, F. Greco, L. D. Spano, and L. Viganò, “Can large language models automate phishing warning explanations? A controlled experiment on effectiveness and user perception,” arXiv:2507.07916, 2025.",
  "[12] J. Nazario, “The online phishing corpus.” [Online]. Available: https://monkey.org/~jose/phishing/ (accessed Oct. 22, 2026).",
  "[13] B. Klimt and Y. Yang, “The Enron corpus: A new dataset for email classification research,” in Machine Learning: ECML 2004, LNCS, vol. 3201, 2004, pp. 217–226, doi: 10.1007/978-3-540-30115-8_22.",
  "[14] A. Prasad and S. Chandra, “PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning,” Computers & Security, art. 103545, 2024, doi: 10.1016/j.cose.2023.103545.",
  "[15] Verizon, “2025 Data Breach Investigations Report,” Verizon Business, 2025.",
].forEach(r => C.push(P(r, { alignment: AlignmentType.LEFT, spacing: { after: 80 } })));

const doc = new Document({
  creator: "CSIT305 group", title: "AI Phishing & Scam Detector",
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: { config: ["b", "n", "n2"].map(ref => ({ reference: ref, levels: [{ level: 0,
    format: ref === "b" ? LevelFormat.BULLET : LevelFormat.DECIMAL, text: ref === "b" ? "•" : "%1.", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 400, hanging: 280 } } } }] })) },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [R("CSIT305 | AI Phishing & Scam Detector", { size: 18, color: "7F7F7F" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, font: FONT, color: "7F7F7F" })] })] }) },
    children: C,
  }],
});
fs.mkdirSync(path.join(ROOT, "report"), { recursive: true });
Packer.toBuffer(doc).then(b => {
  const out = path.join(ROOT, "report", "CSIT305_Group_Project_corrected.docx");
  fs.writeFileSync(out, b);
  console.log("wrote", out);
});
