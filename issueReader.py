# import enchant  # PyEnchant library for spell-checking
import pandas as pd
import openpyxl

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('dataset.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

# Arrays for specific phrases
trueForItWas = []
falseForItWas = []

trueForCausedBy = []
falseForCausedBy = []

trueForIssue = []
falseForIssue = []

# A function to check if a sentence contains a specific phrase, with spell-checking


def contains_phrase(sentence, phrase):
    # Create variations of the phrase with and without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for an exact match or variations with case-insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True


# Check each sentence for the phrases "it was" and "caused by"
for cell in sheet['C']:
    sentence = str(cell.value)
    if contains_phrase(sentence, "it was"):
        trueForItWas.append(sentence)
    else:
        falseForItWas.append(sentence)

for cell in sheet['C']:
    sentence = str(cell.value)
    if contains_phrase(sentence, "cause"):
        trueForCausedBy.append(sentence)
    else:
        falseForCausedBy.append(sentence)


for cell in sheet['C']:
    sentence = str(cell.value)
    if contains_phrase(sentence, "issue"):
        trueForIssue.append(sentence)
    else:
        falseForIssue.append(sentence)
# Print the results
print("\nIT_WAS ARRAYS:")
print("\nTRUE IT WAS statements:\n", trueForItWas)
print("\nFALSE IT WAS statements:\n", falseForItWas)

print("\nCAUSED_BY ARRAYS:")
print("\nTRUE CAUSED BY statements:\n", trueForCausedBy)
print("\nFALSE CAUSED BY statements:\n", falseForCausedBy)

print("\nISSUE ARRAYS:")
print("\nTRUE ISSUE statements:\n", trueForIssue)
print("\nFALSE ISSUE statements:\n", falseForIssue)
