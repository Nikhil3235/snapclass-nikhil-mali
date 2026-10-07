# pyrefly: ignore [missing-import]
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists, create_teacher, teacher_login, 
    get_teacher_subjects, get_attendance_for_teacher,
    get_subject_student_analytics
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
# pyrefly: ignore [missing-import]
import numpy as np

from datetime import datetime

import pandas as pd
import altair as alt

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog
def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='teacher_logout_btn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            st.session_state['login_type'] = None
            if 'teacher_data' in st.session_state:
                del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    


    # Teacher Subject Attendance Analytics Section (Visible on scroll)
    teacher_subject_attendance_analytics()

    footer_dashboard()


def teacher_subject_attendance_analytics():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.markdown("---")
    st.subheader("\U0001f4ca Subject Attendance Analytics & Insights")

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.info("\u2139\ufe0f You haven't created any subjects yet. Create a subject above to view attendance analytics.")
        return

    subject_options = {
        f"{s['name']} ({s['subject_code']}) - Section {s.get('section', 'A')}": s['subject_id'] 
        for s in subjects
    }

    selected_label = st.selectbox(
        "Select Subject to View Student Attendance Breakdown",
        options=list(subject_options.keys()),
        key="analytics_subject_select"
    )
    selected_subject_id = subject_options[selected_label]

    with st.spinner("Analyzing student attendance data..."):
        analytics, total_sessions = get_subject_student_analytics(selected_subject_id)

    if not analytics:
        st.info("\u2139\ufe0f No students are enrolled in this subject yet. Share the subject code with students to enroll.")
        return

    df = pd.DataFrame(analytics)

    total_enrolled = len(df)
    avg_pct = round(df['Percentage'].mean(), 1) if total_enrolled > 0 else 0.0
    safe_count = sum(1 for a in analytics if a['Percentage'] >= 75.0)
    warning_count = sum(1 for a in analytics if 60.0 <= a['Percentage'] < 75.0)
    defaulter_count = sum(1 for a in analytics if a['Percentage'] < 60.0)

    # KPI summary cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Enrolled Students", total_enrolled)
    with k2:
        st.metric("Classes Conducted", total_sessions)
    with k3:
        st.metric("Batch Average", f"{avg_pct:.1f}%")
    with k4:
        st.metric("\U0001f7e2 Safe (>=75%)", safe_count)
    with k5:
        st.metric("\U0001f534 Defaulters (<60%)", defaulter_count)

    if total_sessions == 0:
        st.warning("\u26a0\ufe0f No attendance sessions have been conducted for this subject yet. Take attendance above to see graphical charts.")
        return

    # Altair Chart: Student Attendance Percentage
    color_scale = alt.Scale(
        domain=['\U0001f7e2 Safe (>=75%)', '\U0001f7e0 Warning (60-74%)', '\U0001f534 Defaulter (<60%)'],
        range=['#22c55e', '#f97316', '#ef4444']
    )

    bars = alt.Chart(df).mark_bar(cornerRadiusEnd=5, height=22).encode(
        y=alt.Y('Student:N', title='Student Name', sort='-x'),
        x=alt.X('Percentage:Q', title='Attendance Percentage (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Status:N', scale=color_scale, legend=alt.Legend(title="Attendance Status", orient="bottom")),
        tooltip=[
            alt.Tooltip('Student:N', title='Student'),
            alt.Tooltip('Roll Number:N', title='Roll No'),
            alt.Tooltip('Percentage:Q', title='Attendance %', format='.1f'),
            alt.Tooltip('Attended:Q', title='Present Classes'),
            alt.Tooltip('Total Classes:Q', title='Total Classes'),
            alt.Tooltip('Status:N', title='Status')
        ]
    )

    text = alt.Chart(df).mark_text(
        align='left',
        baseline='middle',
        dx=5,
        fontSize=11,
        fontWeight='bold'
    ).encode(
        y=alt.Y('Student:N', sort='-x'),
        x=alt.X('Percentage:Q'),
        text=alt.Text('Percentage:Q', format='.1f')
    )

    # 75% Criteria Line
    rule_df = pd.DataFrame({'Threshold': [75.0], 'Label': ['75% Target Line']})
    rule = alt.Chart(rule_df).mark_rule(
        color='#ef4444',
        strokeDash=[5, 5],
        size=2
    ).encode(
        x='Threshold:Q'
    )
    rule_label = alt.Chart(rule_df).mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        color='#ef4444',
        fontSize=11,
        fontWeight='bold'
    ).encode(
        x='Threshold:Q',
        text='Label:N'
    )

    chart = (bars + text + rule + rule_label).properties(
        title="Student-wise Attendance Overview",
        height=max(200, len(analytics) * 34)
    ).configure_view(strokeWidth=0)

    st.altair_chart(chart, use_container_width=True)

    with st.expander("\U0001f4cb View Detailed Student Table & Export"):
        display_df = df[['Roll Number', 'Student', 'Attended', 'Total Classes', 'Percentage', 'Status']].sort_values(by='Roll Number')
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="\U0001f4e5 Download Subject Attendance Report (CSV)",
            data=csv,
            file_name=f"{selected_label.split(' ')[0]}_attendance_report.csv",
            mime="text/csv",
            key=f"dl_csv_{selected_subject_id}"
        )


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "Roll Number": student['roll_number'],
                            "Subject": selected_subject_label.split(" - ")[0],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)











def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
        def share_btn():
            if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                share_subject_dialog(sub['name'], sub['subject_code'])
            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats=stats,
            footer_callback=share_btn
        )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


def teacher_tab_attendance_records():
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })


    df = pd.DataFrame(data)



    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()

    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " /"
        + summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = ( summary.sort_values(by='ts_group' ,ascending=False)
                  [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
                  )
    
    st.dataframe(display_df, width='stretch', hide_index=True)

    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        csv_records = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All Records CSV",
            data=csv_records,
            file_name=f"All_Attendance_Records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            icon=":material/download:",
            use_container_width=True
        )
    with c_dl2:
        saved_sheet = st.session_state.get('teacher_portal_url', '')
        if saved_sheet:
            st.link_button("🌐 Open Teacher's Marksheet Portal", saved_sheet, icon=":material/open_in_new:", use_container_width=True)
        else:
            st.info("💡 Set your marksheet link when taking attendance to enable 1-click sync.")


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False


def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='teacher_login_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username.strip(), teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='teacher_reg_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username.strip(), teacher_name.strip(), teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()

