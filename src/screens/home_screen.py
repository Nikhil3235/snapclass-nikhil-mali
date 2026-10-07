# pyrefly: ignore [missing-import]
import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home
def home_screen():


    header_home()
    style_background_home()
    style_base_layout()


    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.header("I'm Student")
        st.image("assets/student.png", width=120)
        if st.button('Student Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width="stretch"):
            st.session_state['login_type']='student'
            st.rerun()

    with col2:
        st.header("I'm Teacher")
        st.image("assets/teacher.png", width=145)
        if st.button('Teacher Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width="stretch"):
            st.session_state['login_type']='teacher'
            st.rerun()

    with col3:
        st.header("I'm Principal")
        st.image("assets/principal.png", width=130)
        if st.button('Principal Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width="stretch"):
            st.session_state['login_type']='admin'
            st.rerun()

    footer_home()