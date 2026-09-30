# pyrefly: ignore [missing-import]
import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time
from datetime import datetime
import json
import urllib.request

from src.database.db import create_attendance

def show_attendance_result(df, logs):
    st.write('Please review attendance before confirming.')
    
    total_students = len(df)
    present_count = int((df['Status'] == 'Present').sum()) if 'Status' in df.columns else 0
    absent_count = total_students - present_count
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Students", total_students)
    with m2:
        st.metric("Present", f"{present_count} ✅")
    with m3:
        st.metric("Absent", f"{absent_count} ❌")
        
    st.dataframe(df, hide_index=True, use_container_width=True)

    # 1-Click CSV Download for Teacher's Marksheet Portal
    csv_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    csv_data = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download CSV for Teacher's Marksheet Portal",
        data=csv_data,
        file_name=f"Attendance_Marksheet_{csv_timestamp}.csv",
        mime="text/csv",
        icon=":material/download:",
        use_container_width=True
    )

    # Teacher Marksheet & Spreadsheet Link Integration
    with st.expander("🔗 Teacher's Marksheet / Portal Integration", expanded=True):
        st.markdown("**Directly update or open your College Attendance Spreadsheet:**")
        sheet_url = st.text_input(
            "Teacher's Spreadsheet / Portal Link",
            value=st.session_state.get('teacher_portal_url', ''),
            placeholder="Paste your Google Sheet, Webhook, or College Portal URL here...",
            key="dialog_sheet_link_input"
        )
        if sheet_url:
            st.session_state['teacher_portal_url'] = sheet_url
            c_link1, c_link2 = st.columns(2)
            with c_link1:
                st.link_button("🌐 Open Teacher Marksheet", sheet_url, icon=":material/open_in_new:", use_container_width=True)
            with c_link2:
                if st.button("⚡ Auto-Sync to Sheet Webhook", icon=":material/sync:", use_container_width=True):
                    try:
                        payload = json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "total": total_students,
                            "present": present_count,
                            "records": df.to_dict(orient="records")
                        }).encode("utf-8")
                        req = urllib.request.Request(sheet_url, data=payload, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            st.success("✅ Successfully synced to Teacher's Marksheet!")
                    except Exception:
                        st.info("Direct link ready! Click 'Open Teacher Marksheet' above to view your spreadsheet.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard', use_container_width=True):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button('Confirm & Save', use_container_width=True, type='primary'):
            try:
                create_attendance(logs)
                st.toast("✅ Attendance recorded successfully!")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error('Sync failed!')


@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)