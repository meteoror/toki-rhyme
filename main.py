import csv, json, os, sys, time
from gradio_client import Client

client = Client("elliewall/english-tokipona-translator")

SOURCE = "English"      # keep whatever values worked in your test
TARGET = "toki pona"
NUM_RESULTS = 3
DELAY = 1.5             # seconds between requests; raise it if you keep getting 429s
OUT_FILE = "translations.json"


def raw_translate(word):
    """Send one word to the Space and return the raw string result."""
    return client.predict(
        word, SOURCE, TARGET, NUM_RESULTS,
        fn_index=0,
    )


def split_candidates(text):
    """Results arrive as one string separated by newlines."""
    return [line.strip() for line in text.split("\n") if line.strip()]


def save(done):
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(done.values()), f, ensure_ascii=False, indent=2)


# Load earlier progress (dict keeps the original CSV order)
done = {}
if os.path.exists(OUT_FILE):
    with open(OUT_FILE, encoding="utf-8") as f:
        for pair in json.load(f):
            done[pair["original"]] = pair

# Read the words from the CSV
with open("625-words-fluent-forever.csv", newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    next(reader, None)  # remove this line if your CSV has no header row
    words = [row[0].strip() for row in reader if row and row[0].strip()]

for word in words:
    existing = done.get(word)
    if existing and existing["translation"] is not None:
        continue  # already translated

    try:
        result = raw_translate(word)
    except Exception as e:
        if "429" in str(e):
            save(done)
            print(f"\nRate limited on {word!r}. Progress saved to {OUT_FILE}.")
            print("Wait a while, then rerun the script to continue from this word.")
            sys.exit(1)
        print(f"Failed on {word!r}: {type(e).__name__}: {e!r}")
        done[word] = {"original": word, "translation": None}
        save(done)
        continue

    candidates = split_candidates(result)
    shortest = min(candidates, key=len) if candidates else None
    done[word] = {"original": word, "translation": shortest}
    save(done)
    print(f"{word} -> {shortest}")
    time.sleep(DELAY)

print(f"Done: {len(done)} words in {OUT_FILE}")