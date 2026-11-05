# Demo script (about 5 minutes)

**Start:** double-click `run_windows.bat`, wait for http://127.0.0.1:8000 to open, and tick the
consent box. Scores below were checked on 5 November 2026 on Windows with Python 3.14. If the
live demo fails, use the pictures in `evidence/screenshots/`.

## Opening (30 seconds)
The prototype is not the research aim. It collects evidence on how detection and explanations
behave across e-mail, SMS and links, tested under one protocol.

## The four examples

| # | Tab | Paste this | Expected | Point to make |
|---|---|---|---|---|
| 1 | SMS | `Your parcel is held. Pay at delivery-update-example.test` | 99, high | The words alone are only mildly suspicious (0.11); the link drives the score. This is why text and link are both checked. |
| 2 | SMS | `Hi, its Abdul. Running 10 mins late to the lab, start without me.` | 2, low | Everyday messages stay low, and the page shows no warning list. Testing found it used to list ordinary words here, so this is a small example of fix and retest (EL21-EL22). |
| 3 | Link | `http://shop-deals-online.com/offer` | 47, uncertain | The middle band tells people to check before acting, rather than forcing a yes or no. The link is never opened. |
| 4 | E-mail | The gift-card message, item C06 in `evidence/challenge_set.csv` | 1, low | A known failure: no link and no scam words. We report this rather than hide it. |

## How it supports the research gap (1 minute)
- **Supported:** conventional ML compared across three formats under one protocol. A fairer URL
  split changed our conclusion (random forest F1 0.803 against 0.947 for the final model).
- **Supported, with a limit:** explanation cues come from the input, but that is true by design,
  so the check mainly confirms the implementation.
- **Not yet shown:** an LLM comparison, and whether non-specialists understand the warnings.

## Results and limits (1 minute)
- F1 is 0.993 for e-mail, 0.966 for SMS and 0.947 for URLs, but these figures cannot be compared
  across formats because the datasets differ.
- E-mail is probably optimistic (legitimate mail is all Enron, 2000-2002). SMS measures spam,
  not smishing.
- The safety-net recall target was missed for SMS (0.946) and URLs (0.963).
- Real sign-in pages can be falsely flagged: accounts.google.com/signin scored 80.
