# pyrefly: ignore [missing-import]
import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time

@st.dialog("Enroll in Subject", key="auto_enroll_dialog")
def auto_enroll_dialog(join_code):
    # Fetch subject details using the join_code
    res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()
    
    if res.data:
        subject = res.data[0]
        st.write(f"You are about to enroll in **{subject['name']}** ({subject['subject_code']}).")
        
        # Check if student data is in session state
        if 'student_data' not in st.session_state or not st.session_state.student_data:
            st.warning("Please log in as a student to enroll.")
            if st.button("Close", width="stretch"):
                st.query_params.clear()
                st.rerun()
            return

        student_id = st.session_state.student_data['student_id']
        
        # Check if already enrolled
        check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
        
        if check.data:
            st.warning('You are already enrolled in this subject.')
            if st.button("Close", width="stretch"):
                st.query_params.clear()
                st.rerun()
        else:
            if st.button('Confirm Enrollment', type='primary', width='stretch'):
                enroll_student_to_subject(student_id, subject['subject_id'])
                st.success(f"Successfully enrolled in {subject['name']}!")
                time.sleep(1.5)
                # Clear query params so the dialog doesn't pop up again
                st.query_params.clear()
                st.rerun()
    else:
        st.error(f"Invalid subject code: {join_code}")
        if st.button("Close", width="stretch"):
            st.query_params.clear()
            st.rerun()