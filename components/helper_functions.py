import re


def parse_nlu(intents_iterable):
    intent_words = []
    for intent in intents_iterable:
        with open("data/nlu.yml") as f:
            relevant = False
            for line in f.readlines():
                if relevant:
                    if line.startswith("- intent:"):
                        relevant = False
                        continue
                    if line == "  examples: |\n":
                        continue
                    for word in re.sub(r"\[[^\]]+\]\([^\)]+\)", "", line.replace("    - ", "").replace("\n", "")).split(" "):
                        intent_words.append(word)
                if line == intent:
                    relevant = True

    return intent_words


# Funktsioon SQLisõbralike sõnede loomiseks
def stringify(string):
    return "'" + string.replace("'", "''") + "'"
