
with open('app4.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 500 to 519 (0-based index 499 to 518)
# We want to keep lines[:499] (lines 1-499)
# And lines[519:] (lines 520-end)

new_lines = lines[:499] + lines[519:]

with open('app4.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleaned up app4.py")
