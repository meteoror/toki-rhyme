import csv, json, time
from gradio_client import Client

client = Client("elliewall/english-tokipona-translator")

SOURCE = "English"      # keep whatever values worked in your test
TARGET = "Toki Pona"
NUM_RESULTS = 3


def raw_translate(word):
    """Send one word to the Space and return the raw string result."""
    return client.predict(
        word, SOURCE, TARGET, NUM_RESULTS,
        fn_index=0,
    )


def split_candidates(text):
    """Results arrive as one string separated by newlines."""
    return [line.strip() for line in text.split("\n") if line.strip()]


pairs = []
with open("625-words-fluent-forever.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)  # remove this line if your CSV has no header row
    for row in reader:
        if not row or not row[0].strip():
            continue
        word = row[0].strip()
        try:
            result = raw_translate(word)
        except Exception as e:
            print(f"Failed on {word!r}: {e}")
            pairs.append({"original": word, "translation": None})
            continue

        candidates = split_candidates(result)
        shortest = min(candidates, key=len) if candidates else None
        pairs.append({"original": word, "translation": shortest})
        print(f"{word} -> {shortest}")
        time.sleep(0.5)

with open("translations.json", "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print(f"Done: {len(pairs)} words written to translations.json")