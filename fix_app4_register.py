
import os

# Read app4.py
with open('app4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old block to replace (I'll try to match a unique part of it)
old_block_start = '@app.route("/register", methods=[\'GET\', \'POST\'])'
old_block_end = "return render_template('register.html')"

# Define the new block
new_block = '''@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['name']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('caretaker_registration.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('caretaker_registration.html')
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (email, password, full_name) VALUES (?, ?, ?)',
                (email, hash_password(password), full_name)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'danger')
        finally:
            conn.close()
    
    return render_template('caretaker_registration.html')'''

# Find start and end indices
start_idx = content.find(old_block_start)
if start_idx != -1:
    # Find the end of the function block. 
    # The original code ends with "return render_template('register.html')"
    end_idx = content.find(old_block_end, start_idx)
    
    if end_idx != -1:
        end_idx += len(old_block_end)
        
        # Replace
        new_content = content[:start_idx] + new_block + content[end_idx:]
        
        with open('app4.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated register function in app4.py")
    else:
        print("Could not find end of register function")
else:
    print("Could not find start of register function")
