import json

# step 1 open the input file and load it into python
# "with open" opens the file and closes it again for us when we are done
# encoding utf-8 makes sure special characters are read correctly
with open("linku_words.json", encoding="utf-8") as f:
    # json.load turns the json text into a python dictionary
    # the keys are the toki pona words and the values are dictionaries of info
    linku = json.load(f)

# step 2 make an empty list to hold our new pairs
# a list in python uses square brackets and keeps items in order
formatted = []

# step 3 loop over every entry in the linku dictionary
# .items() gives us two things per entry
# word is the key like "a" and info is the dictionary inside it
for word, info in linku.items():

    # info is a dictionary so we can look up a value by its name
    # .get("definition", "") means get the definition and use an empty string if it is missing
    # this stops the script from crashing if an entry has no definition
    definition = info.get("definition", "")

    # step 4 build one new dictionary in the format we want
    # original is the english side so it gets the definition
    # translation is the toki pona side so it gets the word
    # we simply never copy the commentary and etymology so they get dropped
    pair = {
        "original": definition,
        "translation": word,
    }

    # step 5 add the new pair to the end of our list
    formatted.append(pair)

# step 6 write the list out to a new file
# the "w" means write mode which creates the file or replaces it if it exists
with open("formatted_linku.json", "w", encoding="utf-8") as f:
    # json.dump turns the python list back into json text and writes it
    # indent 2 makes it nicely spaced so it is easy to read
    # ensure_ascii False keeps special characters as they are instead of escaping them
    json.dump(formatted, f, ensure_ascii=False, indent=2)

# step 7 print a short message so we know it worked
print(f"wrote {len(formatted)} entries to formatted_linku.json")