
import os

# Update app4.py
with open('app4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the email config
new_content = content.replace("'SENDER_EMAIL': 'hariviki7895@gmail.com'", "'SENDER_EMAIL': 'cybertechguard28@gmail.com'")

with open('app4.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated app4.py email config.")

# Update dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove the button
new_lines = []
skip = False
for line in lines:
    if 'id="sendAlertBtn"' in line:
        skip = True
    
    if skip and '</button>' in line:
        skip = False
        continue
        
    if not skip:
        new_lines.append(line)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Removed Send Alert button from dashboard.html")
