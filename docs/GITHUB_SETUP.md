# Putting the project on GitHub (copy-paste guide)

About 20 minutes. You need Git installed (`git --version` in a terminal; if missing, install it
from git-scm.com) and a GitHub account.

## 1. Create the empty repository on GitHub

1. Go to github.com → **New repository**.
2. Name: `csit305-phishing-detector`. Visibility: **Private** (add the tutor later if asked).
3. Do **not** tick "Add a README" (we already have one). Click **Create repository**.
4. Copy the URL it shows, e.g. `https://github.com/YOUR-NAME/csit305-phishing-detector.git`.
5. **Settings → Collaborators → Add people**: add the other four group members.

## 2. Push the code in a few logical commits

Unzip `phishing-detector.zip`, open a terminal **inside the `phishing-detector` folder**, then run
these blocks one at a time. Each block is one commit, so the history shows how the project is
built up. The messages say the work was AI-assisted, which matches the AI-use declaration.

```bash
git init
git branch -M main
git config user.name  "Your Name"
git config user.email "your-uow-email@uowmail.edu.au"
```

```bash
git add .gitignore requirements.txt data/raw/.gitkeep scripts/get_data.sh src/phishdetect/__init__.py src/phishdetect/data.py src/phishdetect/brands.txt
git commit -m "Data loading, cleaning, de-duplication and 70/15/15 splits (AI-assisted)"
```

```bash
git add src/phishdetect/preprocess.py src/phishdetect/url_features.py src/phishdetect/url_model.py
git commit -m "Privacy preprocessing and URL features; links parsed, never visited (AI-assisted)"
```

```bash
git add src/phishdetect/train.py src/phishdetect/explain.py src/phishdetect/pipeline.py models/registry.json
git commit -m "Format-specific models, calibration, risk bands and explanations (AI-assisted)"
```

```bash
git add src/phishdetect/api.py src/phishdetect/audit.py src/phishdetect/static/
git commit -m "FastAPI service, web page and de-identified audit log (AI-assisted)"
```

```bash
git add tests/ src/phishdetect/evaluate.py evidence/ results/ scripts/draw_architecture.py
git commit -m "Tests, evaluation harness, evidence log and v0.1.0/v0.2.0 results (AI-assisted)"
```

```bash
git add README.md docs/ report/ scripts/build_report.js scripts/build_report_pack.js run_windows.bat run_mac_linux.sh
git commit -m "README, documentation and report drafts (AI-assisted)"
```

```bash
git status          # should say "nothing to commit"
git remote add origin https://github.com/YOUR-NAME/csit305-phishing-detector.git
git push -u origin main
```

If `git push` asks for a password, GitHub needs a **personal access token** instead
(GitHub → Settings → Developer settings → Personal access tokens), or use GitHub Desktop.

Trained model files (`models/*.joblib`) and the datasets are deliberately **not** pushed
(`.gitignore`): anyone can rebuild them with `bash scripts/get_data.sh` and
`python -m phishdetect.train`.

## 3. From now on: everyone commits their own work

Each member clones the repo once:

```bash
git clone https://github.com/YOUR-NAME/csit305-phishing-detector.git
cd csit305-phishing-detector
```

Then, for every change (a test, a fix, a screenshot, a log entry):

```bash
git pull
# ...make your change...
git add <the files you changed>
git commit -m "Short description of what you did"
git push
```

This is your individual contribution evidence, so commit under your own name and keep the
messages specific ("Add 3 manual tests for Arabic SMS", not "update").

## 4. Good first commits for each member

| Member | First commit idea |
|---|---|
| Everyone | 2–3 hand-written tests in `tests/test_manual.py` (the brief asks to compare AI-written and manual tests) |
| Imad | Screenshots of the web page in `evidence/screenshots/` + a demo script for Week 11 |
| Abdul | A new evidence-log row comparing your manual tests with the AI-written ones |
| Abdallah | New edge cases in `evidence/edge_cases.csv`, re-run `python -m phishdetect.evaluate` |
| Shehzad | Fix or replace reference [6], update the literature table |
| Djamel | Fix one limitation, e.g. an allow-list for official brand domains, and log before/after results |

Finally, put the repository link in the report (title page and Section 6.1) and the milestone
submission.
