
import os

# Read app4.py
with open('app4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the insertion point
insert_marker = '@app.route("/therapy")'
insert_code = '''
@app.route("/history")
@login_required
def history():
    return render_template('history.html', user_name=session['user_name'])

'''

if insert_marker in content:
    new_content = content.replace(insert_marker, insert_code + insert_marker)
    with open('app4.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added history route.")
else:
    print("Could not find insertion marker.")
