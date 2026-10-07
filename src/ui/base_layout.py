# pyrefly: ignore [missing-import]
import streamlit as st


def style_background_home():

    st.markdown("""
        <style>

                .stApp {
                    background: #5865F2 !important;
                }

                /* Space out the 3 portal cards */
                .stApp div[data-testid="stHorizontalBlock"] {
                    gap: 1.8rem !important;
                    align-items: stretch !important;
                }

                /* Card container with identical height and width */
                .stApp div[data-testid="stColumn"] {
                    background-color: #E0E3FF !important;
                    padding: 2.2rem 1.2rem !important;
                    border-radius: 4rem !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: space-between !important;
                    text-align: center !important;
                    min-height: 480px !important;
                    box-shadow: 0 12px 30px rgba(0,0,0,0.12) !important;
                }

                /* Headings: never break words into separate lines */
                .stApp div[data-testid="stColumn"] h2 {
                    font-family: 'Climate Crisis', sans-serif !important;
                    font-size: 1.45rem !important;
                    line-height: 1.2 !important;
                    white-space: nowrap !important;
                    word-break: keep-all !important;
                    overflow: visible !important;
                    margin: 0.2rem 0 1rem 0 !important;
                    text-align: center !important;
                }

                /* Standardize avatar sizing and round corners */
                .stApp div[data-testid="stColumn"] img {
                    border-radius: 1.5rem !important;
                    margin: 0 auto !important;
                    display: block !important;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.2) !important;
                }

                /* Button: keep label on single line without truncation */
                .stApp div[data-testid="stColumn"] button {
                    white-space: nowrap !important;
                    font-size: 0.95rem !important;
                    font-weight: 600 !important;
                    padding: 10px 14px !important;
                    margin-top: 1rem !important;
                    width: 100% !important;
                }
        </style>  

                """
            ,unsafe_allow_html=True)
    

def style_background_dashboard():

    st.markdown("""
        <style>

                .stApp {
                    background: #E0E3FF !important;
                }

        </style>  

                """
            ,unsafe_allow_html=True)
    

    

def style_base_layout():
# asdasd
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

                
         /* Hide Top Bar of streamlit */
                
            #MainMenu, footer, header {
                visibility: hidden;
            }
                
            .block-container {
                padding-top:1.5rem !important;    
            }

            h1 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height:1.1 1important;
                margin-bottom:0rem !important;
            }
                

            h2 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 2rem !important;
                line-height:0.9 !important;
                margin-bottom:0rem !important;
            }
                
            h3, h4, p {
                font-family: 'Outfit', sans-serif;    
            }
                

            button{
                border-radius: 1.5rem !important;
                background-color: #5865F2 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="secondary"]{
                border-radius: 1.5rem !important;
                background-color: #EB459E !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="tertiary"]{
                border-radius: 1.5rem !important;
                background-color: black !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button:hover{
                transform :scale(1.05)}
        </style>  

                """
            ,unsafe_allow_html=True)