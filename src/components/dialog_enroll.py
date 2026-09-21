# pyrefly: ignore [missing-import]
import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write('Enter the subject code provided by your teacher to enroll')
    join_code = st.text_input('Subject Code', placeholder='Eg. 25AF1245PCL05')

    if st.button('Enroll now', type='primary', width='stretch'):
        if join_code and join_code.strip():
            code_clean = join_code.strip()
            # Case-insensitive lookup using ilike
            res = supabase.table('subjects').select('subject_id, name, subject_code').ilike('subject_code', code_clean).execute()
            if res.data:
                subject = res.data[0]
                if 'student_data' not in st.session_state or not st.session_state.student_data:
                    st.error("Student session not found. Please log in again.")
                    return
                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                if check.data:
                    st.warning(f"You are already enrolled in **{subject['name']}** ({subject['subject_code']})")
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success(f"Successfully enrolled in **{subject['name']}** ({subject['subject_code']})!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error(f"Subject code '{code_clean}' not found! Please check the code and try again.")
        else:
            st.warning('Please enter a subject code')