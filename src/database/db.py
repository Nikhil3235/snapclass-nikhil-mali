from src.database.config import supabase
# pyrefly: ignore [missing-import]
import bcrypt



def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    username = username.strip()
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0 


def check_student_exists_by_roll(roll_number):
    # Returns true if a student with this roll number already exists
    if not roll_number:
        return False
    response = supabase.table("students").select("roll_number").eq("roll_number", str(roll_number).strip()).execute()
    return len(response.data) > 0



def create_teacher(username, password, name):
    username = username.strip()
    data = { "username" : username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    username = username.strip()
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None


def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

def create_student(new_name, roll_number, password=None, face_embedding=None, voice_embedding=None):
    data = {
        'name': new_name, 
        'roll_number': str(roll_number).strip(),
        'face_embedding': face_embedding, 
        "voice_embedding": voice_embedding
    }
    if password:
        data['password'] = hash_pass(password)
    response = supabase.table('students').insert(data).execute()
    return response.data


def update_student_password(student_id, new_password):
    hashed = hash_pass(new_password)
    response = supabase.table('students').update({'password': hashed}).eq('student_id', student_id).execute()
    return response.data


def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data


    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions


        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects


def  enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response= supabase.table('subject_students').insert(data).execute()
    return response.data


def  unenroll_student_to_subject(student_id, subject_id):
    response= supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data



def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def get_student_attendance(student_id):
    response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def create_attendance(logs):
    response = supabase.table('attendance_logs').insert(logs).execute()
    return response.data

def get_attendance_for_teacher(teacher_id):
    response = supabase.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    return response.data


def get_subject_student_analytics(subject_id):
    enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', subject_id).execute()
    enrolled = enrolled_res.data or []

    logs_res = supabase.table('attendance_logs').select("*").eq('subject_id', subject_id).execute()
    logs = logs_res.data or []

    sessions = set(log.get('timestamp') for log in logs if log.get('timestamp'))
    total_sessions = len(sessions)

    analytics = []
    for item in enrolled:
        st_data = item.get('students') or {}
        st_id = st_data.get('student_id')
        name = st_data.get('name', 'Unknown')
        roll = st_data.get('roll_number', 'N/A')

        attended = sum(1 for log in logs if log.get('student_id') == st_id and log.get('is_present'))
        percentage = round((attended / total_sessions * 100), 1) if total_sessions > 0 else 0.0

        if percentage >= 75.0:
            status = '🟢 Safe (>=75%)'
            color = '#22c55e'
        elif percentage >= 60.0:
            status = '🟠 Warning (60-74%)'
            color = '#f97316'
        else:
            status = '🔴 Defaulter (<60%)'
            color = '#ef4444'

        analytics.append({
            'Student': name,
            'Roll Number': roll,
            'Attended': attended,
            'Total Classes': total_sessions,
            'Percentage': percentage,
            'Status': status,
            'Color': color
        })

    return analytics, total_sessions


def get_admin_dashboard_data():
    teachers_res = supabase.table('teachers').select('*').execute()
    teachers = teachers_res.data or []
    
    students_res = supabase.table('students').select('*').execute()
    students = students_res.data or []

    subjects_res = supabase.table('subjects').select('*, teachers(name, username), subject_students(count), attendance_logs(timestamp, is_present)').execute()
    raw_subjects = subjects_res.data or []

    subject_summaries = []
    total_classes_all = 0
    total_present_all = 0
    total_attendance_records_all = 0

    for sub in raw_subjects:
        teacher_info = sub.get('teachers') or {}
        teacher_name = teacher_info.get('name') or teacher_info.get('username') or 'Unknown Faculty'
        
        enrolled_count = sub.get('subject_students', [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        
        logs = sub.get('attendance_logs') or []
        sessions = set(log.get('timestamp') for log in logs if log.get('timestamp'))
        total_sessions = len(sessions)
        
        presents = sum(1 for log in logs if log.get('is_present'))
        total_logs = len(logs)
        
        avg_pct = round((presents / total_logs * 100), 1) if total_logs > 0 else 0.0
        
        if avg_pct >= 75.0:
            health = '🟢 Safe (≥75%)'
            color = '#22c55e'
        elif avg_pct >= 60.0:
            health = '🟠 Warning (60-74%)'
            color = '#f97316'
        else:
            health = '🔴 Low Attendance (<60%)'
            color = '#ef4444'

        total_classes_all += total_sessions
        total_present_all += presents
        total_attendance_records_all += total_logs

        subject_summaries.append({
            'subject_id': sub.get('subject_id'),
            'subject_name': sub.get('name', 'Unknown'),
            'subject_code': sub.get('subject_code', 'N/A'),
            'section': sub.get('section', 'A'),
            'teacher_name': teacher_name,
            'teacher_id': sub.get('teacher_id'),
            'enrolled_students': enrolled_count,
            'classes_conducted': total_sessions,
            'total_logs': total_logs,
            'average_attendance': avg_pct,
            'health_status': health,
            'color': color
        })

    inst_avg = round((total_present_all / total_attendance_records_all * 100), 1) if total_attendance_records_all > 0 else 0.0
    low_attendance_classes = sum(1 for s in subject_summaries if s['average_attendance'] < 75.0 and s['classes_conducted'] > 0)

    summary_metrics = {
        'total_teachers': len(teachers),
        'total_students': len(students),
        'total_subjects': len(raw_subjects),
        'total_classes_conducted': total_classes_all,
        'institute_avg_attendance': inst_avg,
        'low_attendance_classes': low_attendance_classes
    }

    return summary_metrics, subject_summaries, teachers