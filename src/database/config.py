# pyrefly: ignore [missing-import]
import streamlit as st


# pyrefly: ignore [missing-import]
from supabase import create_client, Client

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://hvxmtobkfkzohbbruthv.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2eG10b2JrZmt6b2hiYnJ1dGh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4NDAyNTcsImV4cCI6MjA5NDQxNjI1N30.Q6jlzsFaOaSSRM1FOZ-3CsbVbQt7B3yCrEtW0o6JybE")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)