Job Application Tracker API

This is a FastAPI-based REST API that allows users to register, log in, and track their job applications. It uses JSON files (user.json and applications.json) for simple persistent storage.

🚀 Features

User Registration: Create a new account with email, username, and password.

User Login: Authenticate and receive a JWT token for secure access.

Add Job Applications: Users can add job applications with job title, company, date applied, and status.

View Applications: Retrieve all job applications for the logged-in user.

File Handling: JSON-based storage for users and applications, auto-created if missing.

📂 Project Structure
project/
│── main.py                 # FastAPI routes
│── dep.py                  # Dependencies, models, helper functions
│── sec.py                  # Security constants (SECRET_KEY, ALGORITHM)
│── user.json               # User storage (auto-created)
│── applications.json       # Job applications storage (auto-created)
│── README.md               # Project documentation