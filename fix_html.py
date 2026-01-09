
lines_to_remove = range(235, 263) # 1-based index 235 to 262

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if (i + 1) not in lines_to_remove:
            f.write(line)

print("Successfully removed duplicate modal lines.")
