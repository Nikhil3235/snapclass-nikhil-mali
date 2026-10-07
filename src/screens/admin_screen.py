# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import altair as alt
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import get_admin_dashboard_data, get_subject_student_analytics

ADMIN_DEFAULT_PIN = "admin123"

def admin_login_view():
    header_dashboard()
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.image("assets/principal.png", width=110)
            st.subheader("🏛️ Principal / Dean Portal Access")
            st.caption("Secure Administrative Access for College Executive Leadership")
            
            entered_pin = st.text_input(
                "Enter Administrative Passkey / PIN",
                type="password",
                placeholder="Enter admin passkey (Default: admin123)",
                key="admin_pin_input"
            )
            
            col_btn, col_back = st.columns(2)
            with col_btn:
                if st.button("Access Dashboard", type="primary", width="stretch", key="admin_login_btn"):
                    if entered_pin.strip() == ADMIN_DEFAULT_PIN:
                        st.session_state.is_admin_logged_in = True
                        st.toast("Welcome, Principal / Dean!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Administrative Passkey! (Default is 'admin123')")
            with col_back:
                if st.button("Back to Home", type="secondary", width="stretch", key="admin_back_home_btn"):
                    st.session_state['login_type'] = None
                    st.rerun()

def admin_dashboard():
    c1, c2 = st.columns([3, 1], vertical_alignment='center')
    with c1:
        st.subheader("🏛️ Principal / Dean Executive Dashboard")
        st.caption("Real-Time College-wide Faculty, Courses, Enrollment & Attendance Oversight")
    with c2:
        if st.button("Logout", type='secondary', key='admin_logout_btn', width="stretch"):
            st.session_state['is_logged_in'] = False
            st.session_state['login_type'] = None
            st.session_state['is_admin_logged_in'] = False
            st.rerun()

    st.markdown("---")

    with st.spinner("Compiling institutional analytics..."):
        metrics, subject_summaries, teachers = get_admin_dashboard_data()

    # 1. Executive KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        with st.container(border=True):
            st.metric("👨‍🏫 Faculty", metrics['total_teachers'])
    with k2:
        with st.container(border=True):
            st.metric("🎓 Students", metrics['total_students'])
    with k3:
        with st.container(border=True):
            st.metric("📚 Courses", metrics['total_subjects'])
    with k4:
        with st.container(border=True):
            st.metric("📊 Avg Attendance", f"{metrics['institute_avg_attendance']:.1f}%")
    with k5:
        with st.container(border=True):
            st.metric(
                "⚠️ Low Classes", 
                metrics['low_attendance_classes'],
                delta=f"{metrics['low_attendance_classes']} (<75%)" if metrics['low_attendance_classes'] > 0 else "All Safe",
                delta_color="inverse" if metrics['low_attendance_classes'] > 0 else "normal"
            )

    st.markdown("---")

    # Tabs for structured viewing
    tab_overview, tab_drilldown, tab_export = st.tabs([
        "📊 Faculty & Subject Overview",
        "🔍 Class & Student Drill-Down",
        "📑 Institutional Audit & Reports"
    ])

    with tab_overview:
        st.subheader("Faculty Performance & Course Attendance Breakdown")
        
        if not subject_summaries:
            st.info("ℹ️ No courses or subjects have been registered in the system yet.")
        else:
            df_subjects = pd.DataFrame(subject_summaries)

            # Interactive filter
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                faculty_names = ["All Faculty"] + sorted(list(set(df_subjects['teacher_name'].dropna())))
                selected_faculty = st.selectbox("Filter by Faculty Member", options=faculty_names, key="admin_fac_filter")
            with f_col2:
                show_low_only = st.checkbox("Show Only Low Attendance Classes (<75%)", key="admin_low_filter")

            filtered_df = df_subjects.copy()
            if selected_faculty != "All Faculty":
                filtered_df = filtered_df[filtered_df['teacher_name'] == selected_faculty]
            if show_low_only:
                filtered_df = filtered_df[filtered_df['average_attendance'] < 75.0]

            if filtered_df.empty:
                st.info("No courses match the selected filter criteria.")
            else:
                # Graphical Bar Chart comparing subject attendance
                chart_df = filtered_df.copy()
                chart_df['Subject_Label'] = chart_df['subject_name'] + " (" + chart_df['subject_code'] + ") - Sec " + chart_df['section'] + " [" + chart_df['teacher_name'] + "]"
                
                color_scale = alt.Scale(
                    domain=['🟢 Safe (≥75%)', '🟠 Warning (60-74%)', '🔴 Low Attendance (<60%)'],
                    range=['#22c55e', '#f97316', '#ef4444']
                )

                bars = alt.Chart(chart_df).mark_bar(cornerRadiusEnd=5, height=24).encode(
                    y=alt.Y('Subject_Label:N', title='Course & Faculty', sort='x'),
                    x=alt.X('average_attendance:Q', title='Average Attendance (%)', scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color('health_status:N', scale=color_scale, legend=alt.Legend(title="Attendance Health", orient="bottom")),
                    tooltip=[
                        alt.Tooltip('subject_name:N', title='Course'),
                        alt.Tooltip('subject_code:N', title='Code'),
                        alt.Tooltip('section:N', title='Section'),
                        alt.Tooltip('teacher_name:N', title='Faculty'),
                        alt.Tooltip('enrolled_students:Q', title='Enrolled Students'),
                        alt.Tooltip('classes_conducted:Q', title='Classes Held'),
                        alt.Tooltip('average_attendance:Q', title='Avg Attendance %', format='.1f'),
                        alt.Tooltip('health_status:N', title='Status')
                    ]
                )

                text = alt.Chart(chart_df).mark_text(
                    align='left',
                    baseline='middle',
                    dx=5,
                    fontSize=11,
                    fontWeight='bold'
                ).encode(
                    y=alt.Y('Subject_Label:N', sort='x'),
                    x=alt.X('average_attendance:Q'),
                    text=alt.Text('average_attendance:Q', format='.1f')
                )

                rule_df = pd.DataFrame({'Threshold': [75.0], 'Label': ['75% Mandatory Target']})
                rule = alt.Chart(rule_df).mark_rule(color='#ef4444', strokeDash=[5, 5], size=2).encode(x='Threshold:Q')
                rule_label = alt.Chart(rule_df).mark_text(
                    align='center', baseline='bottom', dy=-10, color='#ef4444', fontSize=11, fontWeight='bold'
                ).encode(x='Threshold:Q', text='Label:N')

                inst_chart = (bars + text + rule + rule_label).properties(
                    title="Course Attendance Distribution Across Faculty",
                    height=max(180, len(chart_df) * 36)
                ).configure_view(strokeWidth=0)

                st.altair_chart(inst_chart, use_container_width=True)

            # Faculty Directory Grouping
            st.markdown("#### 👨‍🏫 Faculty-wise Courses & Enrollment Directory")
            unique_teachers = {t['teacher_id']: t['name'] for t in teachers}
            
            for t_id, t_name in unique_teachers.items():
                t_courses = [s for s in subject_summaries if s['teacher_id'] == t_id]
                t_enrolled = sum(s['enrolled_students'] for s in t_courses)
                t_classes = sum(s['classes_conducted'] for s in t_courses)
                t_avg = round(sum(s['average_attendance'] for s in t_courses) / len(t_courses), 1) if t_courses else 0.0

                with st.expander(f"Prof. {t_name} — {len(t_courses)} Course(s) | {t_enrolled} Total Enrolled | Avg: {t_avg}%"):
                    if not t_courses:
                        st.info("No courses created by this faculty member yet.")
                    else:
                        t_df = pd.DataFrame(t_courses)[[
                            'subject_name', 'subject_code', 'section', 'enrolled_students', 
                            'classes_conducted', 'average_attendance', 'health_status'
                        ]].rename(columns={
                            'subject_name': 'Course Name',
                            'subject_code': 'Code',
                            'section': 'Section / Batch',
                            'enrolled_students': 'Enrolled Students',
                            'classes_conducted': 'Classes Held',
                            'average_attendance': 'Attendance %',
                            'health_status': 'Status'
                        })
                        st.dataframe(t_df, use_container_width=True, hide_index=True)

    with tab_drilldown:
        st.subheader("🔍 Class-Level & Student Attendance Inspection")
        if not subject_summaries:
            st.info("No courses available to inspect.")
        else:
            course_opts = {
                f"{s['subject_name']} ({s['subject_code']}) - Sec {s['section']} [Faculty: {s['teacher_name']}]": s['subject_id']
                for s in subject_summaries
            }
            selected_course_label = st.selectbox("Select Course & Section to Inspect Students", options=list(course_opts.keys()), key="drill_course_select")
            selected_sid = course_opts[selected_course_label]

            with st.spinner("Fetching enrolled students and attendance records..."):
                analytics, total_sess = get_subject_student_analytics(selected_sid)

            if not analytics:
                st.info("ℹ️ No students are currently enrolled in this course section.")
            else:
                c_df = pd.DataFrame(analytics)
                c_enrolled = len(c_df)
                c_avg = round(c_df['Percentage'].mean(), 1) if c_enrolled > 0 else 0.0
                c_safe = sum(1 for a in analytics if a['Percentage'] >= 75.0)
                c_warn = sum(1 for a in analytics if 60.0 <= a['Percentage'] < 75.0)
                c_def = sum(1 for a in analytics if a['Percentage'] < 60.0)

                d1, d2, d3, d4, d5 = st.columns(5)
                with d1:
                    st.metric("Enrolled in Section", c_enrolled)
                with d2:
                    st.metric("Classes Held", total_sess)
                with d3:
                    st.metric("Section Average", f"{c_avg:.1f}%")
                with d4:
                    st.metric("🟢 Safe (≥75%)", c_safe)
                with d5:
                    st.metric("🔴 Defaulters (<60%)", c_def)

                # Student Bar Chart
                color_scale = alt.Scale(
                    domain=['🟢 Safe (>=75%)', '🟠 Warning (60-74%)', '🔴 Defaulter (<60%)'],
                    range=['#22c55e', '#f97316', '#ef4444']
                )

                s_bars = alt.Chart(c_df).mark_bar(cornerRadiusEnd=5, height=20).encode(
                    y=alt.Y('Student:N', title='Student Name', sort='-x'),
                    x=alt.X('Percentage:Q', title='Attendance Percentage (%)', scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color('Status:N', scale=color_scale, legend=alt.Legend(title="Attendance Status", orient="bottom")),
                    tooltip=[
                        alt.Tooltip('Student:N', title='Student'),
                        alt.Tooltip('Roll Number:N', title='Roll No'),
                        alt.Tooltip('Percentage:Q', title='Attendance %', format='.1f'),
                        alt.Tooltip('Attended:Q', title='Classes Attended'),
                        alt.Tooltip('Total Classes:Q', title='Total Classes'),
                        alt.Tooltip('Status:N', title='Status')
                    ]
                )

                s_rule = alt.Chart(pd.DataFrame({'Threshold': [75.0]})).mark_rule(
                    color='#ef4444', strokeDash=[5, 5], size=2
                ).encode(x='Threshold:Q')

                s_chart = (s_bars + s_rule).properties(
                    title=f"Student Attendance Details — {selected_course_label}",
                    height=max(180, len(analytics) * 30)
                ).configure_view(strokeWidth=0)

                st.altair_chart(s_chart, use_container_width=True)

                st.markdown("##### Detailed Student Marksheet")
                st_display_df = c_df[['Roll Number', 'Student', 'Attended', 'Total Classes', 'Percentage', 'Status']].sort_values(by='Roll Number')
                st.dataframe(st_display_df, use_container_width=True, hide_index=True)

    with tab_export:
        st.subheader("📑 Consolidated Institutional Attendance Audit Report")
        if not subject_summaries:
            st.info("No attendance data to export.")
        else:
            audit_df = pd.DataFrame(subject_summaries)[[
                'subject_name', 'subject_code', 'section', 'teacher_name',
                'enrolled_students', 'classes_conducted', 'total_logs',
                'average_attendance', 'health_status'
            ]].rename(columns={
                'subject_name': 'Course Name',
                'subject_code': 'Course Code',
                'section': 'Section / Batch',
                'teacher_name': 'Faculty In-Charge',
                'enrolled_students': 'Total Enrolled',
                'classes_conducted': 'Classes Conducted',
                'total_logs': 'Attendance Records Logged',
                'average_attendance': 'Class Average Attendance %',
                'health_status': 'Status Category'
            })
            
            st.dataframe(audit_df, use_container_width=True, hide_index=True)
            
            csv_data = audit_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Institute-Wide Attendance Report (CSV)",
                data=csv_data,
                file_name="Institute_Attendance_Audit_Report.csv",
                mime="text/csv",
                key="admin_dl_all_csv",
                type="primary"
            )

    footer_dashboard()

def admin_screen():
    style_background_dashboard()
    style_base_layout()

    if st.session_state.get('is_admin_logged_in'):
        admin_dashboard()
    else:
        admin_login_view()
