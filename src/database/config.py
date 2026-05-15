# pyrefly: ignore [missing-import]
import streamlit as st


# pyrefly: ignore [missing-import]
from supabase import create_client, Client

supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)