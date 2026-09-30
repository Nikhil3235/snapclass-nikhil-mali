# pyrefly: ignore [missing-import]
import streamlit as st
import base64
import os


def _get_logo_base64():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logo_path = os.path.join(base_dir, "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://i.ibb.co/YTYGn5qV/logo.png"


def header_home():

    logo_url = _get_logo_base64()
    landing_page_url = "https://snap-class-landing-page-ruby.vercel.app/"
    
    st.markdown(f"""
        <!-- Top Right Landing Page Link Button -->
        <style>
            .landing-btn-container {{
                position: fixed;
                top: 20px;
                right: 25px;
                z-index: 999999 !important;
            }}
            .landing-btn {{
                display: inline-flex !important;
                align-items: center !important;
                gap: 8px !important;
                background-color: #E0E3FF !important;
                color: #5865F2 !important;
                text-decoration: none !important;
                padding: 10px 20px !important;
                border-radius: 2rem !important;
                font-family: 'Outfit', sans-serif !important;
                font-size: 15px !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
                transition: all 0.25s ease-in-out !important;
                border: 2px solid rgba(255, 255, 255, 0.6) !important;
                cursor: pointer !important;
            }}
            .landing-btn:hover {{
                transform: scale(1.08) !important;
                background-color: #ffffff !important;
                color: #5865F2 !important;
                box-shadow: 0 6px 22px rgba(0, 0, 0, 0.3) !important;
            }}
        </style>
        <div class="landing-btn-container">
            <a href="{landing_page_url}" target="_blank" rel="noopener noreferrer" class="landing-btn" title="Go to Landing Page">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5865F2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
                <span>Landing Page</span>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5865F2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M7 17L17 7M7 7h10v10"/>
                </svg>
            </a>
        </div>

        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px">
            <img src='{logo_url}' style='height:100px;' />
            <h1 style='text-align:center; color:#E0E3FF'>SNAP<br/>CLASS</h1>
        </div>   
                
                """, unsafe_allow_html=True)


def header_dashboard():

    logo_url = _get_logo_base64()
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:10px">
            <img src='{logo_url}' style='height:85px;' />
            <h2 style='text-align:left; color:#5865F2'>SNAP<br/>CLASS</h1>
        </div>   
                
                """, unsafe_allow_html=True)