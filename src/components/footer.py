# pyrefly: ignore [missing-import]
import streamlit as st


def footer_home():
    st.markdown("""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center">
        <p style="font-weight:bold; color:white; margin:0;"> Created with ❤️ by </p>  
        <span style="font-weight:800; font-size:1.15rem; color:#E0E3FF; letter-spacing:0.5px;">AI_AVENGERS</span>
        </div>
                
                """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center">
        <p style="font-weight:bold; color:black; margin:0;"> Created with ❤️ by </p>  
        <span style="font-weight:800; font-size:1.15rem; color:#5865F2; letter-spacing:0.5px;">AI_AVENGERS</span>
        </div>
                
                """, unsafe_allow_html=True)