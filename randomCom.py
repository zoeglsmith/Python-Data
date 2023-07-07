import random
import openpyxl

# Define the issue code prefixes
prefixes = ['CXF', 'GROOVY', 'HARMONY', 'CASSANDRA', 'INFRA']

# Generate a list of 365 random issue codes with the specified prefixes
selected_issue_codes = []
while len(selected_issue_codes) < 365:
    prefix = random.choice(prefixes)
    issue_number = random.randint(1, 9999)
    issue_code = f"{prefix}-{issue_number:04}"
    if issue_code not in selected_issue_codes:
        selected_issue_codes.append(issue_code)

# Print the selected issue codes
for issue_code in selected_issue_codes:
    print(issue_code)

# Create a new Excel workbook
workbook = openpyxl.Workbook()

# Select the active sheet
sheet = workbook.active

# Write the issue codes to the Excel sheet
for i, issue_code in enumerate(selected_issue_codes, start=1):
    sheet.cell(row=i, column=1, value=issue_code)

# Save the workbook
workbook.save("selected_issue_codes.xlsx")

print("Issue codes printed and exported to an Excel sheet.")
