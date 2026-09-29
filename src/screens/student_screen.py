# pyrefly: ignore [missing-import]
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
# pyrefly: ignore [missing-import]
from PIL import Image
# pyrefly: ignore [missing-import]
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject, check_student_exists_by_roll
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='student_logout_btn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            st.session_state['login_type'] = None
            if 'student_data' in st.session_state:
                del st.session_state.student_data 
            st.rerun()


    st.space()

    c1, c2 =st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        percentage = (stats['attended'] / stats['total'] * 100) if stats['total'] > 0 else 0

        def unenroll_button():
                if st.button("Unenroll from tihs course", type='tertiary', width='stretch', icon=':material/delete_forever:', key=f"unenroll_{sid}"):
                    unenroll_student_to_subject(student_id, sid)
                    st.toast(f'Unenrolled from {sub['name']} successfully!')
                    st.rerun()

        with cols[i % 2]:

            card_stats = [
                ('📅', 'Total', stats['total']),
                ('✅', 'Attended', stats['attended']),
                ('📊', 'Attendance', f"{percentage:.1f}%"),
            ]

            if percentage < 75.0 and stats['total'] > 0:
                card_stats.append(('⚠️', 'Status', 'Low Attendance!'))

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = card_stats,
                footer_callback=unenroll_button
            )
            
            if percentage < 75.0 and stats['total'] > 0:
                st.warning(f"You need to increase attendance in {sub['name']} (Current: {percentage:.1f}%)")
    footer_dashboard()


def student_screen():


    style_background_dashboard()
    style_base_layout()


    if "student_data" in st.session_state:
        student_dashboard()
        return
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='student_login_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Student Portal', text_alignment='center')
    st.space()
    
    tab_login, tab_register = st.tabs(["🔑 FaceID Login", "📝 New Student Registration"])

    with tab_login:
        st.subheader("Login using FaceID")
        photo_source = st.camera_input("Position your face in the center", key="login_camera")

        if photo_source:
            img = np.array(Image.open(photo_source))

            with st.spinner('AI is scanning..'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('Face not found! Please adjust lighting or position.')
                elif num_faces > 1:
                    st.warning('Multiple faces found. Please ensure only one person is in front of the camera.')
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if s['student_id'] == student_id), None)

                        if student:
                            st.success(f"Recognized Face: **{student['name']}** (Roll: {student.get('roll_number', 'N/A')})")
                            st.info("Is this you? Please confirm to login:")
                            
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("Yes, Log Me In", type="primary", key="confirm_login_btn", width="stretch"):
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.session_state.student_data = student
                                    st.toast(f"Welcome Back {student['name']}!")
                                    time.sleep(1)
                                    st.rerun()
                            with col_no:
                                if st.button("No, this is not me", type="secondary", key="reject_login_btn", width="stretch"):
                                    st.warning("If you are a new student, please switch to the 'New Student Registration' tab to register.")
                        else:
                            st.info("Face recognized, but student profile not found in database.")
                    else:
                        st.info("Face not recognized! If you are a new student, please register under the 'New Student Registration' tab.")

    with tab_register:
        st.subheader("Register New Profile")
        with st.container(border=True):
            new_name = st.text_input("Enter your name", placeholder='E.g. Student Name', key="reg_name")
            new_roll = st.text_input("Enter your Roll Number", placeholder='E.g. 21BCS101', key="reg_roll")

            st.write("Take a photo of your face for FaceID registration:")
            reg_photo_source = st.camera_input("Capture registration photo", key="register_camera")

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your voice for voice-only attendance")

            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase like "I am present, My name is Akash."', key="reg_audio")
            except Exception:
                st.error('Audio Data failed!')

            bypass_check = st.checkbox("Bypass duplicate face detection (Use only if face matches someone else incorrectly)", key="bypass_dup_check")

            if st.button('Create Account', type='primary', key="reg_create_btn", width="stretch"):
                if new_name and new_roll:
                    if not reg_photo_source:
                        st.error("Please capture your face photo using the camera above to register.")
                    elif check_student_exists_by_roll(new_roll):
                        st.error(f'Roll Number {new_roll} is already registered! Please use your correct roll number.')
                    else:
                        with st.spinner('Creating profile..'):
                            img = np.array(Image.open(reg_photo_source))
                            
                            # Check for duplicate face if not bypassed
                            if not bypass_check:
                                detected, _, _ = predict_attendance(img)
                                if detected:
                                    student_id = list(detected.keys())[0]
                                    all_students = get_all_students()
                                    matched_student = next((s for s in all_students if s['student_id'] == student_id), None)
                                    if matched_student:
                                        st.error(f"❌ Registration Blocked: This face is already registered as **{matched_student['name']}** (Roll: {matched_student.get('roll_number', 'N/A')}).")
                                        st.info("💡 If this is you, please use the **🔑 FaceID Login** tab. If this is a false match, check the 'Bypass duplicate face detection' box above and click Create Account again.")
                                        st.stop()

                            encodings = get_face_embeddings(img)
                            if encodings:
                                face_emb = encodings[0].tolist()

                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embedding(audio_data.read())

                                try:
                                    response_data = create_student(new_name, new_roll, face_embedding=face_emb, voice_embedding=voice_emb)
                                except Exception as e:
                                    st.error(f"Failed to create profile: {e}")
                                    response_data = None

                                if response_data:
                                    train_classifier()
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.session_state.student_data = response_data[0]
                                    st.toast(f'Profile Created! Hi {new_name}!')
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error('Could not capture your facial features. Please position your face clearly in the camera and try again.')
                else:
                    st.warning('Please enter both your name and roll number!')

    footer_dashboard()