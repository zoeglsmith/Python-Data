# import enchant  # PyEnchant library for spell-checking

# # Create a dictionary for spell-checking
# d = enchant.Dict("en_US")

# Bunch of sentances the code will analyze
sentences = ["It was a beautiful day.", "ItwasItwas", "it was", "itwas", "causedby", "causedBy", "causdBy",
             "The problem was caused by a server error.", "This is a sample sentence."]

# Arrays for specific phrases
trueForItWas = []
falseForItWas = []

trueForCausedBy = []
falseForCausedBy = []

# A function to check if a sentence contains a specific phrase


# A function to check if a sentence contains a specific phrase, with spell-checking
def contains_phrase(sentence, phrase):
    # Create variations of the phrase with and without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for an exact match or variations with case-insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True

    #     # If the variation is not an exact match, try spell-checking it
    #     suggestions = d.suggest(variation)
    #     for suggestion in suggestions:
    #         if suggestion.lower() in sentence.lower():
    #             return True

    # # If no match is found, return False
    return False


# Check each sentence for the phrases "it was" and "caused by"
for sentence in sentences:
    if contains_phrase(sentence, "it was"):
        trueForItWas.append(sentence)
    else:
        falseForItWas.append(sentence)

for sentence in sentences:
    if contains_phrase(sentence, "caused by"):
        trueForCausedBy.append(sentence)
    else:
        falseForCausedBy.append(sentence)

# Print the results
print("IT_WAS ARRAYS:")
print("True statements:", trueForItWas)
print("False statements:", falseForItWas)

print("CAUSED_BY ARRAYS:")
print("True statements:", trueForCausedBy)
print("False statements:", falseForCausedBy)
