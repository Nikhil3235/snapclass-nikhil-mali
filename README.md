# 📸 SnapClass - AI Powered Attendance System

**SnapClass** is a modern, automated attendance management system that leverages Artificial Intelligence to make classroom attendance faster, more secure, and paperless. Built with Streamlit and Supabase, it uses Face Recognition and Voice Analysis to identify students instantly.

---

## 🚀 Key Features

### 👨‍🏫 Teacher Portal
- **Secure Login**: Password-protected access for teachers.
- **Subject Management**: Create and manage multiple subjects with unique join codes.
- **AI Face Attendance**: Upload classroom photos and let the AI identify all present students automatically.
- **Voice Attendance**: Use voice biometrics for an alternative hands-free attendance method.
- **Attendance Records**: View and export detailed attendance logs and statistics.

### 🎓 Student Portal
- **FaceID Login**: No passwords needed! Students log in securely using their face.
- **Easy Enrollment**: Join subjects using codes shared by teachers.
- **Attendance Tracking**: Students can view their own attendance percentage for each subject.
- **Voice Enrollment**: Optional voice registration for multi-modal verification.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python-based Web Framework)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL with Realtime features)
- **AI/ML**:
  - **Face Recognition**: `dlib`, `face_recognition_models`, and `scikit-learn`.
  - **Voice Analysis**: `resemblyzer` and `librosa`.
- **Security**: `bcrypt` for password hashing and secure session management.

---

## 📥 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nikhil3235/snapclass-nikhil-mali.git
   cd snapclass-nikhil-mali
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets**:
   Create a `.streamlit/secrets.toml` file and add your Supabase credentials:
   ```toml
   SUPABASE_URL = "your_supabase_url"
   SUPABASE_KEY = "your_supabase_anon_key"
   ```

4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

---

## 📝 Database Schema
The project uses a relational structure in Supabase with the following tables:
- `teachers`: Login credentials and names.
- `students`: Face/Voice embeddings and Roll Numbers.
- `subjects`: Course details and join codes.
- `subject_students`: Enrollment mapping.
- `attendance_logs`: Real-time attendance history.

---

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## 📄 License
This project is for educational purposes.

*Developed with ❤️ by **Team BizTechX***
