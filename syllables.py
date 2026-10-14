import json, os, sys

IN_FILE = "translations.json"
OUT_FILE = "syllabic_translations.json"
DECISIONS_FILE = "duplicate_decisions.json"  # remembers your choices so you can quit and resume
VOWELS = set("aeiouAEIOU")


def clean_translation(text):
    """Strip punctuation, then drop the standalone word 'o'."""
    text = "".join(ch for ch in text if ch.isalpha() or ch.isspace())
    words = [w for w in text.split() if w.lower() != "o"]
    return " ".join(words)


def count_syllables(text):
    """In Toki Pona, syllables = vowels."""
    return sum(1 for ch in text if ch in VOWELS)


def save_decisions(decisions):
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2)


# ---- Load and clean ----
with open(IN_FILE, encoding="utf-8") as f:
    data = json.load(f)

entries = []   # [{"translation": cleaned, "english": original}, ...] in original order
skipped = []
for item in data:
    english = item.get("original")
    raw = item.get("translation")
    cleaned = clean_translation(raw) if raw else ""
    if not cleaned:
        skipped.append(english)
        continue
    entries.append({"translation": cleaned, "english": english})

# ---- Group duplicates (same cleaned Toki Pona) ----
groups = {}
for e in entries:
    groups.setdefault(e["translation"], []).append(e["english"])

decisions = {}
if os.path.exists(DECISIONS_FILE):
    with open(DECISIONS_FILE, encoding="utf-8") as f:
        decisions = json.load(f)

dupes = [t for t, eng in groups.items() if len(eng) > 1]
print(f"{len(entries)} usable entries, {len(dupes)} translations with duplicates.\n")

for n, t in enumerate(dupes, 1):
    englishes = groups[t]

    # Reuse an earlier decision if there is one
    if t in decisions:
        kept = [e for e in englishes if e in decisions[t]]
        if kept:
            groups[t] = kept
            continue

    print(f"[{n}/{len(dupes)}] '{t}' is used for:")
    for i, eng in enumerate(englishes, 1):
        print(f"  {i}) {eng}")

    while True:
        choice = input("Keep which? (number(s) like 1 or 1,3 | a = keep all | q = save and quit): ").strip().lower()
        if choice == "q":
            save_decisions(decisions)
            print("Progress saved. Rerun the script to continue.")
            sys.exit(0)
        if choice == "a":
            kept = englishes
            break
        try:
            picks = {int(x) for x in choice.replace(" ", "").split(",")}
        except ValueError:
            print("  Please enter numbers separated by commas, 'a', or 'q'.")
            continue
        if picks and all(1 <= p <= len(englishes) for p in picks):
            kept = [englishes[p - 1] for p in sorted(picks)]
            break
        print(f"  Numbers must be between 1 and {len(englishes)}.")

    groups[t] = kept
    decisions[t] = kept
    save_decisions(decisions)
    print()

# ---- Build the output in the original order ----
output = []
for e in entries:
    t, eng = e["translation"], e["english"]
    if eng in groups[t]:
        output.append({t: {"english": eng, "syllables": count_syllables(t)}})

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(output)} entries to {OUT_FILE}")
if skipped:
    print(f"Skipped {len(skipped)} entries with no usable translation: {skipped}")