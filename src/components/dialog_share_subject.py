# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "https://snapclass-nikhil.streamlit.app"
    join_url = f"{app_domain}/?join-code={subject_code}"

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'### Copy Link: {subject_name}')
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info(f'Copy this link to share on Whatsapp or Email to invite students to {subject_name}')

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption='QRCODE for class joining')

        