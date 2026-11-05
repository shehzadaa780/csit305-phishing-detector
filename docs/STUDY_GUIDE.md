# Study guide: understand and defend the prototype

The Week 11 panel can ask **any** member about **any** part of the project, and they will check
how you verified AI-written work (brief, criterion C4). Everyone should read Parts 1–3 and 5.
Part 4 gives each person one module to know in depth.

---

## Part 1. The project in five sentences

1. People need a simple way to check whether an e-mail, SMS or link is a scam, and to be told **why**.
2. We built a local Python service that gives a 0–100 risk score in three bands and lists the
   warning signs it found **in the input itself**.
3. Each format has its own model, because e-mails, SMS and links look different and the
   literature warns against comparing results across datasets.
4. We tested each model once on data it had never seen, plus 40 new AI-written messages and
   18 edge cases, and reported failures honestly.
5. The main research finding is about **how** to evaluate: a fairer test split changed our URL
   conclusion completely, which is why evaluation protocol matters as much as the model.

## Part 2. Key ideas in plain words

| Term | What it means here | Where in the code |
|---|---|---|
| **TF-IDF** | Turns text into numbers. Each word or word pair gets a weight: high if it is frequent in this message but rare across all messages. | `train.py` `_vectoriser()` |
| **Logistic regression** | Adds up (word weight × learned importance) and squashes the total into a probability between 0 and 1. Each word's importance is a number we can read, which makes explanations possible. | `train.py` |
| **Character n-grams** | For links, we look at every 3-, 4- and 5-character piece (`ogin`, `pay-`, `.xyz`), so the model can spot patterns in links it has never seen. | `url_model.py` |
| **Lexical URL features** | 21 readable properties of a link: length, hyphens, IP address instead of a name, `@`, shortener, punycode, brand name in the wrong place. | `url_features.py` |
| **Calibration** | Makes the probability honest: when the model says 0.8, about 80% of such messages really are phishing. Done on the validation set. | `train.py` `_calibrate()` |
| **Risk bands** | risk = round(100 × probability). 0–39 low, 40–69 uncertain ("check before acting"), 70–100 high. If a message has a link, the higher of the text and link risk is used. | `pipeline.py` `band_for()` |
| **Explanation** | For a linear model, each feature's contribution = its value × its weight, exactly. We show the biggest positive contributions that are present in the input. Nothing is invented. | `explain.py` |
| **Train / validation / test** | 70% to learn, 15% to choose settings and calibrate, 15% held back and used **once** for the final score. | `data.py` `split()` |
| **Data leakage** | When the test set accidentally shares information with training data, scores look better than reality. We found and fixed two cases. | Evidence log EL01, EL11 |
| **Grouped split** | For URLs, all links from the same website go into the same set, so the test measures performance on **new** websites. | `data.py` `split()` |
| **Recall** | Of all real phishing, how much did we catch? Our priority, because a miss can cost money. | `evaluate.py` |
| **Precision / false alarms** | Of everything we flagged, how much was really phishing? / How many safe messages did we wrongly flag? | `evaluate.py` |
| **F1** | One number balancing precision and recall. | `evaluate.py` |
| **Brier score** | Average squared gap between predicted probability and what really happened. 0 is perfect. | `evaluate.py` |
| **Bootstrap 95% CI** | Resample the test set 1,000 times to see how much a score could vary by chance. | `evaluate.py` `bootstrap_f1()` |

## Part 3. What happens to one message (follow along in `pipeline.py`)

Example: SMS `Your parcel is held. Pay at delivery-update-example.test`

1. **API** (`api.py`): checks `consent` is true, otherwise HTTP 403.
2. **Intake** (`Detector.analyze`): type must be email / sms / url; empty input → error 422.
3. **Preprocess** (`preprocess.py`): finds the link `delivery-update-example.test` without
   opening it; replaces it with the word `urltoken`; masks e-mails and phone numbers;
   lower-cases; keeps only letters and digits → `your parcel is held pay at urltoken`.
4. **Text model**: TF-IDF → calibrated probability 0.11 (the words alone are only mildly suspicious).
5. **URL model**: character pieces + 21 features → probability 0.99.
6. **Risk**: max(0.11, 0.99) → 99 → **high**.
7. **Explanation** (`explain.py`): top contributions found in this input: "at a link" (call to
   action), "held" (delivery), uncommon domain ending, several hyphens.
8. **Response**: label, risk, band, cues, a sentence built from the cues, advice, model version.
   The audit log stores a row (no text) only if `allow_logging` is true.

## Part 4. One module per person (suggested)

| Member | Know in depth | Be ready to explain |
|---|---|---|
| Imad | `pipeline.py`, `api.py`, `static/index.html` | The 8 steps; why max(text, link); why 403/422; how to run the demo |
| Abdul | `evaluate.py`, `results/criteria_table.csv` | Every metric in Table III; bootstrap CI; 5%-prevalence precision; time-split test |
| Abdallah | `evidence/`, edge cases, `audit.py` | Each edge case and why it matters; the evidence log entries; why no text is logged |
| Shehzad | `train.py`, Table II, literature link | Why logistic regression; why the random forest was replaced; how results relate to [2], [3], [7] |
| Djamel | `preprocess.py`, `url_features.py`, `data.py` | Privacy masking; links never visited; de-duplication; the two leakage fixes |

**How to study your module:** run it, change one thing, and watch what happens. For example:

```bash
cd src
python -c "from phishdetect.preprocess import preprocess; print(preprocess('Call +971 50 123 4567 or visit bit.ly/abc'))"
python -c "from phishdetect.url_features import extract; print(extract('http://paypal.com.secure-login.xyz/verify'))"
python -c "from phishdetect.pipeline import Detector; import json; print(json.dumps(Detector().analyze('sms','You won a free iPhone, claim at prize-claim.top'), indent=2))"
```

## Part 5. Likely panel questions, with answers

**Why not just use ChatGPT/an LLM to detect phishing?**
Sending real messages to an external API is a privacy risk, it costs money per check, and LLMs
can give confident but unsupported reasons [7]. Our explanations come straight from the model's
numbers, so they cannot invent facts. An LLM comparator is planned but needs privacy approval.

**Your e-mail F1 is 0.993. Isn't that too good?**
Yes, and we say so. Legitimate e-mails come from one company (Enron, 2000–2002) and phishing
from 2015–2022, so part of what the model learns may be "not Enron". That is why we added the
time-split test (recall 0.95 → 0.90) and the challenge set (7/8 caught, 1 false alarm).

**Why did you change from a random forest to logistic regression for URLs?**
Evidence log EL10–EL12. The random forest failed three criteria. We then found 66% of test URLs
came from websites also in training. On a fair split by website, the random forest got F1 0.80;
logistic regression with character pieces got 0.95. We kept the random forest as the comparator.

**What is your SMS model actually detecting?**
Spam, not smishing. The UCI dataset labels spam. We say this in the limitations, and a
phishing-labelled SMS dataset is future work.

**Where does it fail?**
Scams with no link and no scam words (gift-card request, "Hi mum, new number"); real brand
websites like paypal.com (the brand name appears so often in phishing links); non-English text.

**How do you know the explanations are correct?**
Each cue is an exact contribution from the model for a feature that is present in the input.
An automated check confirmed all 264 cues exist in their input, and the same input always gives
the same cues. We did **not** test whether people understand them; that needs ethics approval.

**What did AI do, and how did you check it?** (answer for your own part honestly)
The code, tests and challenge messages were written with Claude in one session, then:
23 automated tests, a single held-out test per model, 18 edge cases, and a 40-message challenge
set. Testing made us **reject** two AI design choices (random forest URL model, random URL split).
Then add what **you** checked, changed or wrote yourself, e.g. your manual tests.

**Why the 40/70 thresholds?**
Set in the proposal before testing and not changed afterwards, so the results are not tuned to
the test set. The uncertain band is a safety net that tells users to check before acting.

**What would you do next?**
Smishing data; modern legitimate e-mails; an official-brand allow-list to fix paypal.com-type
false alarms; the approved LLM comparison; a small user study of the explanations.

## Part 6. Before the symposium

- [ ] Everyone has run the web page and tried their own examples.
- [ ] Everyone can explain Parts 1–3 without notes.
- [ ] Each person has committed their own manual tests and at least one other change.
- [ ] Demo plan: one obvious phishing SMS, one safe message, one link in the uncertain band,
      one known failure (e.g. the gift-card e-mail), so you show honesty about limitations.
