# Rating the explanations (expert rubric, report Section 4.3.2)

Two group members rate separately. Do not discuss scores until both files are finished.

1. Rater A opens `rater_A.csv` and rater B opens `rater_B.csv`. Both contain the same 20
   items: every warning the detector gave on the challenge set, in shuffled order.
2. For each item, read `explanation` and `advice`, then enter a score in `score_0_1_2`:

   | Score | Meaning |
   |---|---|
   | 0 | Names neither a clear risk cue nor a safe next action |
   | 1 | Names one of them clearly, but not both |
   | 2 | Names a clear risk cue and a safe next action |

3. Use `comment` for anything confusing, such as a cue that would mean nothing to a non-specialist.
4. Save both files as CSV, then run this from the `phishing-detector` folder:

   ```bash
   .venv\Scripts\python scripts\score_rubric.py
   ```

5. Add the mean scores and Cohen's kappa to report Section 6.3, and add a row to
   `evidence/evidence_log.csv`.

Report this as an **expert rubric** only. It does not show that users understand the warnings.
`item_key.csv` links each item back to its challenge-set ID; 2 of the 20 are false alarms on
legitimate messages. Raters should not open it until they have finished.
