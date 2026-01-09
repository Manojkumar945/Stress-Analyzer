
import os

# Read app4.py
with open('app4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the insertion point
insert_marker = '@app.route("/history")'
insert_code = '''
@app.route("/api/detailed_history")
@login_required
def detailed_history():
    try:
        hours = request.args.get('hours', default=24, type=int)
        session_id = request.args.get('session_id', type=int)
        limit = request.args.get('limit', default=1000, type=int)
        
        conn = get_db_connection()
        
        # Base query
        query = """
            SELECT r.*, s.patient_id, p.patient_name
            FROM readings r
            JOIN monitoring_sessions s ON r.session_id = s.id
            JOIN patients p ON s.patient_id = p.id
            WHERE p.caretaker_id = ?
        """
        params = [session['user_id']]
        
        # Add time filter
        if hours:
            query += " AND r.timestamp >= datetime('now', '-' || ? || ' hours')"
            params.append(hours)
            
        # Add session filter
        if session_id:
            query += " AND r.session_id = ?"
            params.append(session_id)
            
        query += " ORDER BY r.timestamp DESC LIMIT ?"
        params.append(limit)
        
        readings = conn.execute(query, params).fetchall()
        
        # Get time range stats
        stats_query = """
            SELECT MIN(timestamp) as start_time, MAX(timestamp) as end_time, COUNT(*) as count
            FROM readings r
            JOIN monitoring_sessions s ON r.session_id = s.id
            JOIN patients p ON s.patient_id = p.id
            WHERE p.caretaker_id = ?
        """
        stats_params = [session['user_id']]
        
        if hours:
            stats_query += " AND r.timestamp >= datetime('now', '-' || ? || ' hours')"
            stats_params.append(hours)
            
        stats = conn.execute(stats_query, stats_params).fetchone()
        conn.close()
        
        # Format readings
        formatted_readings = []
        for r in readings:
            # Parse prediction JSON if stored as string, or use as is
            try:
                import json
                prediction_data = json.loads(r['prediction']) if isinstance(r['prediction'], str) else r['prediction']
            except:
                prediction_data = {"prediction": "unknown"}

            formatted_readings.append({
                "id": r['id'],
                "timestamp": r['timestamp'],
                "eeg_value": r['eeg_value'],
                "prediction": prediction_data,
                "patient_name": r['patient_name']
            })
            
        return jsonify({
            "readings": formatted_readings,
            "time_range": {
                "start": stats['start_time'],
                "end": stats['end_time']
            },
            "total_count": stats['count']
        })
        
    except Exception as e:
        print(f"Error in detailed_history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/history")
@login_required
def api_history():
    try:
        hours = request.args.get('hours', default=24, type=int)
        conn = get_db_connection()
        
        # Get sessions for user's patients
        query = """
            SELECT s.*, p.patient_name, COUNT(r.id) as reading_count
            FROM monitoring_sessions s
            JOIN patients p ON s.patient_id = p.id
            LEFT JOIN readings r ON s.id = r.session_id
            WHERE p.caretaker_id = ?
            AND s.start_time >= datetime('now', '-' || ? || ' hours')
            GROUP BY s.id
            ORDER BY s.start_time DESC
        """
        sessions = conn.execute(query, (session['user_id'], hours)).fetchall()
        conn.close()
        
        history_data = []
        for s in sessions:
            history_data.append({
                "session_id": s['id'],
                "patient_name": s['patient_name'],
                "start_time": s['start_time'],
                "end_time": s['end_time'],
                "status": s['status'],
                "reading_count": s['reading_count']
            })
            
        return jsonify({"history": history_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

'''

if insert_marker in content:
    new_content = content.replace(insert_marker, insert_code + insert_marker)
    with open('app4.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added history API routes.")
else:
    print("Could not find insertion marker.")
