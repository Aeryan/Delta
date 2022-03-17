# language = any

import re
from components.levenshtein import manual_levenshtein


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


def remove_intent_words(text, intent_words):
    text_list = text.split(" ")
    for word in text.split(" "):
        if word == "I":
            continue
        # best_match = process.extractOne(word, self.intent_words)
        best_match = manual_levenshtein(word, intent_words)
        if best_match[1] < 2:
            text_list.remove(word)
    return " ".join(text_list)


# Funktsioon SQLisõbralike sõnede loomiseks
def stringify(string):
    return "'" + string.replace("'", "''") + "'"
