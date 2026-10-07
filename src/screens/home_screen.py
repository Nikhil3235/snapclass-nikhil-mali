# pyrefly: ignore [missing-import]
import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home
def home_screen():


    header_home()
    style_base_layout()
    style_background_home()

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("<div class='portal-title'>I'm Student</div>", unsafe_allow_html=True)
        st.image("assets/student.png", width=140)
        if st.button('Student Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width="stretch"):
            st.session_state['login_type']='student'
            st.rerun()

    with col2:
        st.markdown("<div class='portal-title'>I'm Teacher</div>", unsafe_allow_html=True)
        st.image("assets/teacher.png", width=140)
        if st.button('Teacher Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width="stretch"):
            st.session_state['login_type']='teacher'
            st.rerun()

    with col3:
        st.markdown("<div class='portal-title'>I'm Principal</div>", unsafe_allow_html=True)
        st.image("assets/principal.png", width=140)
        if st.button('Principal Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width="stretch"):
            st.session_state['login_type']='admin'
            st.rerun()

    footer_home()