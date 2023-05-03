import enchant  # PyEnchant library for spell-checking
import pandas as pd
# Create a dictionary for spell-checking
d = enchant.Dict("en_US")


df = pd.read_excel('dataset.xlsx', usecols='C')
print(df)

# print(df)
# # Arrays for specific phrases
trueForItWas = []
falseForItWas = []

# trueForCausedBy = []
# falseForCausedBy = []

# # A function to check if a sentence contains a specific phrase


# # A function to check if a sentence contains a specific phrase, with spell-checking
def contains_phrase(sentence, phrase):
    # Create variations of the phrase with and without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for an exact match or variations with case-insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True

        # If the variation is not an exact match, try spell-checking it
        suggestions = d.suggest(variation)
        for suggestion in suggestions:
            if suggestion.lower() in sentence.lower():
                return True

    # If no match is found, return False
    return False


# Check each sentence for the phrases "it was" and "caused by"
for sentence in df:
    if contains_phrase(sentence, "it was"):
        trueForItWas.append(sentence)
    else:
        falseForItWas.append(sentence)

# Print the results
print("IT_WAS ARRAYS:")
print("True statements:", trueForItWas)
print("False statements:", falseForItWas)
