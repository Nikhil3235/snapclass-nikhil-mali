# pyrefly: ignore [missing-import]
import streamlit as st
import importlib
import src.components.footer

# Ensure latest team branding (AI_AVENGERS) is fresh in memory
importlib.reload(src.components.footer)

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.screens.admin_screen import admin_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon="assets/logo.png"
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    join_code = st.query_params.get('join-code')
    if join_code:
        st.session_state['login_type'] = 'student'

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case 'admin':
            admin_screen()
        
        case None:
            home_screen()


    if join_code:
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)
main()