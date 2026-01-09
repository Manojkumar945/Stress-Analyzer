
import os

# Read dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the insertion point
insert_marker = '<i class="fas fa-cloud"></i> EEG Activity\n                </a>'
insert_code = '\n                <a href="/therapy" class="menu-item">\n                    <i class="fas fa-music"></i> Smart Therapy\n                </a>'

if insert_marker in content:
    # We want to insert AFTER the closing </a> tag of EEG Activity
    # The marker ends with </a>, so we can replace marker with marker + code
    new_content = content.replace(insert_marker, insert_marker + insert_code)
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added Smart Therapy link.")
else:
    print("Could not find insertion marker.")
