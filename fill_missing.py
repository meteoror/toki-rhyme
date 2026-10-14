import csv, json, os, shutil, sys

CSV_FILE = "words.csv"
SYLLABIC_FILE = "syllabic_translations.json"
ORIGINAL_FILE = "translations.json"   # only used to show you the earlier result as a hint
VOWELS = set("aeiouAEIOU")


def clean_translation(text):
    """Same cleaning as before: strip punctuation, drop the standalone word 'o'."""
    text = "".join(ch for ch in text if ch.isalpha() or ch.isspace())
    words = [w for w in text.split() if w.lower() != "o"]
    return " ".join(words)


def count_syllables(text):
    return sum(1 for ch in text if ch in VOWELS)


def save(entries):
    with open(SYLLABIC_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


# ---- Words from the CSV ----
with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    next(reader, None)  # remove this line if your CSV has no header row
    words = [row[0].strip() for row in reader if row and row[0].strip()]
words = list(dict.fromkeys(words))  # remove repeats, keep order

# ---- Current syllabic file ----
with open(SYLLABIC_FILE, encoding="utf-8") as f:
    entries = json.load(f)

have = set()   # English words already present
used = {}      # Toki Pona translation -> English words using it
for entry in entries:
    for t, inner in entry.items():
        have.add(inner["english"])
        used.setdefault(t, []).append(inner["english"])

# ---- Earlier raw results, just for context ----
old = {}
if os.path.exists(ORIGINAL_FILE):
    with open(ORIGINAL_FILE, encoding="utf-8") as f:
        for item in json.load(f):
            old[item["original"]] = item.get("translation")

missing = [w for w in words if w not in have]
if not missing:
    print("Nothing is missing. Every word in the CSV is in the syllabic file.")
    sys.exit(0)

shutil.copy(SYLLABIC_FILE, SYLLABIC_FILE + ".bak")  # safety backup
print(f"{len(missing)} words are missing from {SYLLABIC_FILE}.")
print("Type a Toki Pona translation for each. Enter = skip, q = quit.\n")

added = 0
for n, word in enumerate(missing, 1):
    prev = old.get(word)
    print(f"[{n}/{len(missing)}] {word}" + (f"   (earlier result: {prev!r})" if prev else ""))

    while True:
        raw = input("  Toki Pona: ").strip()
        if raw.lower() == "q":
            print(f"\nStopped. Added {added} entries. Rerun to continue with the rest.")
            sys.exit(0)
        if not raw:
            break  # skip this word

        cleaned = clean_translation(raw)
        if not cleaned:
            print("  Nothing left after cleaning. Try again.")
            continue

        if cleaned in used:
            print(f"  Note: '{cleaned}' is already used for: {', '.join(used[cleaned])}")

        syllables = count_syllables(cleaned)
        entries.append({cleaned: {"english": word, "syllables": syllables}})
        used.setdefault(cleaned, []).append(word)
        save(entries)
        added += 1
        print(f"  Added '{cleaned}' ({syllables} syllables)\n")
        break

print(f"\nDone. Added {added} entries to {SYLLABIC_FILE}.")