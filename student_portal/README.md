📚 Student Grades API (FastAPI)

A small FastAPI service for student registration, authentication (JWT), and retrieving a student's grades.
Data is persisted in local JSON files for simplicity: student.json (users) and student_result.json (grades). This is intended as a learning/demo project.

✨ Features

Register students (email, username, password accepted)

Login to receive a JWT token

Protected endpoint to retrieve the logged-in student’s grades

Automatic creation of required JSON files if missing

Note: This is a demo implementation. Authentication and password handling are intentionally minimal — see Security & Improvements below.

📁 File Structure (expected)
.
├─ main.py                  # FastAPI routes: /register, /login, /grades
├─ dep.py                   # models and helpers (check_filepath, auth, etc.)
├─ sec.py                   # SECRET_KEY, ALGORITHM
├─ student.json             # auto-created, stores registered users
├─ student_result.json      # auto-created, stores list of grade records

