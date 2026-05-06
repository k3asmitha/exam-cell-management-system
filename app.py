from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'exam_cell_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'ExamCellAutomation'
}

def get_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM exams")
    e_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM faculty")
    f_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM rooms")
    r_count = cursor.fetchone()[0]
    conn.close()
    return render_template('dashboard.html', e_count=e_count, f_count=f_count, r_count=r_count)

# This route MUST be present for the JavaScript to get the student count
@app.route('/get_course_details/<int:course_id>')
def get_course_details(course_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Ensure 'student_count' is the exact column name in your courses table
    cursor.execute("SELECT student_count FROM courses WHERE id = %s", (course_id,))
    course = cursor.fetchone()
    conn.close()
    
    if course:
        return jsonify(course) # Returns {"student_count": 50}
    return jsonify({"student_count": 0})

@app.route('/create-exam', methods=['GET', 'POST'])
def create_exam():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        exam_name = request.form.get('name')
        start_date = request.form.get('start_date')
        slot = request.form.get('slot')
        course_id = request.form.get('course_id')

        try:
            # 1. Register Exam
            cursor.execute("INSERT INTO exams (exam_name, start_date, end_date, exam_date, slot) VALUES (%s, %s, %s, %s, %s)", 
                           (exam_name, start_date, start_date, start_date, slot))
            exam_id = cursor.lastrowid

            # 2. Get Student Count
            cursor.execute("SELECT course_name, student_count FROM courses WHERE id = %s", (course_id,))
            course_data = cursor.fetchone()
            total_students = course_data['student_count']
            remaining_students = total_students

            # 3. Fetch Rooms (Minimization Logic: Largest First)
            cursor.execute("""
                SELECT id, room_name, capacity FROM rooms 
                WHERE id NOT IN (
                    SELECT room_id FROM allocations a 
                    JOIN rooms r ON a.room_id = r.id 
                    WHERE e.exam_date = %s AND e.slot = %s
                ) ORDER BY capacity DESC
            """, (start_date, slot))
            available_rooms = cursor.fetchall()

            # 4. Fetch Faculty (Conflict Check)
            cursor.execute("""
                SELECT id, name FROM faculty 
                WHERE assigned_duties < max_duties 
                AND id NOT IN (
                    SELECT faculty_id FROM allocations a 
                    JOIN exams e ON a.exam_id = e.id 
                    WHERE e.exam_date = %s AND e.slot = %s
                ) ORDER BY assigned_duties ASC
            """, (start_date, slot))
            available_faculty = cursor.fetchall()

            allocation_summary = []
            f_idx = 0
            
            for room in available_rooms:
                if remaining_students <= 0:
                    break
                
                if f_idx < len(available_faculty):
                    faculty = available_faculty[f_idx]
                    
                    # Store Allocation
                    cursor.execute("INSERT INTO allocations (exam_id, course_id, room_id, faculty_id) VALUES (%s, %s, %s, %s)", 
                                   (exam_id, course_id, room['id'], faculty['id']))
                    cursor.execute("UPDATE faculty SET assigned_duties = assigned_duties + 1 WHERE id = %s", (faculty['id'],))
                    
                    # Logic Documentation
                    allocation_summary.append({
                        'room': room['room_name'],
                        'capacity': room['capacity'],
                        'reason': f"Optimized: Using large capacity ({room['capacity']}) to minimize room count."
                    })
                    
                    remaining_students -= room['capacity']
                    f_idx += 1

            conn.commit()
            flash(f"Allocated for {total_students} students across {len(allocation_summary)} rooms.", "success")
            return redirect(url_for('reports'))
            
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}", "danger")
        finally:
            conn.close()

    # Dropdown Data
    cursor.execute("SELECT DISTINCT branch FROM courses")
    branches = [row['branch'] for row in cursor.fetchall()]
    cursor.execute("SELECT id, course_name, branch, course_code FROM courses")
    all_courses = cursor.fetchall()
    conn.close()
    return render_template('create_exam.html', branches=branches, courses=all_courses)

@app.route('/reports')
def reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.exam_name, c.course_name, r.room_name, r.capacity, f.name as faculty_name, e.exam_date, e.slot
        FROM allocations a
        JOIN exams e ON a.exam_id = e.id
        JOIN courses c ON a.course_id = c.id
        JOIN rooms r ON a.id = r.id
        JOIN faculty f ON a.faculty_id = f.id
        ORDER BY e.exam_date DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return render_template('reports.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
