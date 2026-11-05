#!/usr/bin/env bash
# Downloads the three datasets into data/raw/. Run from the project root:
#   bash scripts/get_data.sh
# Check each source's licence and terms before redistributing the data.
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
mkdir -p data/raw/sms data/raw/url data/raw/email

echo "[1/3] SMS: UCI SMS Spam Collection (Almeida et al. [3]) - GitHub mirror of the UCI file"
git clone --depth 1 -q https://github.com/justmarkham/pycon-2016-tutorial.git "$TMP/sms"
cp "$TMP/sms/data/sms.tsv" data/raw/sms/SMSSpamCollection.tsv
#   Official source: https://archive.ics.uci.edu/dataset/228/sms+spam+collection

echo "[2/3] URL: phishing / legitimate URL lists released with Sahingoz et al. [2]"
git clone --depth 1 -q https://github.com/ebubekirbbr/pdd.git "$TMP/pdd"
cp "$TMP/pdd/input/data_phishing_37175.json" "$TMP/pdd/input/data_legitimate_36400.json" \
   "$TMP/pdd/input/allbrands.txt" data/raw/url/

echo "[3/3] E-mail: Nazario phishing corpus [12] + Enron ham [13] (CSV mirror)"
git clone --depth 1 -q https://github.com/rokibulroni/Phishing-Email-Dataset.git "$TMP/email"
cp "$TMP/email/Nazario.csv" "$TMP/email/Enron.csv" data/raw/email/

rm -rf "$TMP"
echo "Done. Next: python -m phishdetect.train   (run inside src/ or with PYTHONPATH=src)"
