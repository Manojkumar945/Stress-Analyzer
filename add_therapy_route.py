
import os

# Read app4.py
with open('app4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the insertion point
insert_marker = '@app.route("/api/send_alert", methods=[\'POST\'])'
insert_code = '''
@app.route("/therapy")
@login_required
def therapy():
    conn = get_db_connection()
    # Get user's patients for the sidebar/context if needed
    patients = conn.execute(
        'SELECT * FROM patients WHERE caretaker_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('therapy.html', 
                         user_name=session['user_name'],
                         patients=patients,
                         monitoring_active=monitoring_active,
                         latest_prediction=latest_prediction,
                         current_song=current_song)

'''

if insert_marker in content:
    new_content = content.replace(insert_marker, insert_code + insert_marker)
    with open('app4.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added therapy route.")
else:
    print("Could not find insertion marker.")
