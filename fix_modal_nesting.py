
# Script to fix the nested modal issue in dashboard.html
path = 'templates/dashboard.html'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "<!-- Send Alert Modal -->"
target_index = -1
for i, line in enumerate(lines):
    if "<!-- Send Alert Modal -->" in line:
        target_index = i
        break

if target_index != -1:
    # Check if the previous line is just a closing div
    # We want to insert another closing div before the comment
    
    # Insert the closing div for addPatientModal
    lines.insert(target_index, "            </div>\n")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully added closing div for addPatientModal.")
else:
    print("Target line not found.")
