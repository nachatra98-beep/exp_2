# Habit Tracker Web Application 💛

A modern, responsive Habit Tracker web application built with **ReactJS** (Vite) and **Django REST Framework**, following the **SRS v1.0 specification** and matching the warm pastel yellow UI design.

![Habit Tracker Banner](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react)
![Django](https://img.shields.io/badge/Backend-Django%20%2B%20DRF-092E20?style=for-the-badge&logo=django)

---

## ✨ Features

- **Authentication & Security (SRS FR-1 to FR-8)**:
  - Register with username, email, and password.
  - Sign in with JWT token authentication (access & refresh tokens).
  - Single-toggle between Sign In and Create Account on `/login`.
  - Protected routes redirect unauthenticated users to `/login`.
- **Habit Management (SRS FR-9 to FR-17)**:
  - List active habits with streak counters and daily status.
  - One-click check / uncheck for today with celebratory confetti!
  - Daily progress bar and completion percentage.
  - Add & Edit habits (`/add` and `/add?id=<id>`).
  - Delete habits with confirmation dialog.
- **Streak Calculation Logic (SRS Section 4.4)**:
  - Consecutive days ending today (or yesterday if today is pending).
  - Resets to 0 if neither today nor yesterday has a check-in.
  - Tracks both current streak and all-time longest streak.
- **UI Design (Matched from Design Mockup)**:
  - Warm pastel yellow theme with sunburst trophy banner (`You're on a roll! 7 Day Streak Keep going! 🔥`).
  - Habit cards with category icons, frequency, and goal indicators.
  - Interactive **Calendar** view with month navigation & check-in day highlights.
  - Interactive **Statistics** view with animated donut chart, metric cards, and cheering star mascot.
  - **Profile** view with avatar, notifications toggle, appearance mode, and logout.
  - Bottom navigation bar with floating center `+` button.

---

## 🚀 Quick Start Guide

### 1. Backend (Django REST Framework)

```bash
cd backend

# Run migrations (already generated)
python manage.py migrate

# (Optional) Seed demo user & habits matching the mockup:
python manage.py seed_demo

# Run tests
python manage.py test

# Start the Django development server
python manage.py runserver 127.0.0.1:8000
```

> **Demo User Credentials**:
> - **Username**: `Nachatra`
> - **Password**: `Password123!`

---

### 2. Frontend (React + Vite)

```bash
cd frontend

# Install dependencies (already installed)
npm install

# Start Vite development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📁 Project Structure

```
EX_2/
├── backend/
│   ├── manage.py
│   ├── config/             # Django settings, URLs, WSGI
│   ├── accounts/           # User registration, login, JWT views & tests
│   └── habits/             # Habit & HabitLog models, streak logic, views & tests
│       └── management/commands/seed_demo.py
└── frontend/
    ├── package.json
    ├── vite.config.js      # Proxy configured for /api to Django
    ├── index.html
    └── src/
        ├── api/            # Axios instance with JWT interceptors
        ├── context/        # AuthContext (login, register, logout, me)
        ├── components/     # HabitCard, StreakBanner, ProgressBar, BottomNav, ProtectedRoute
        ├── pages/          # Login.jsx, Home.jsx, AddHabit.jsx, CalendarView.jsx, StatsView.jsx, ProfileView.jsx
        ├── App.jsx         # App router configuration
        └── index.css       # Complete warm pastel yellow styling
```

---

## 📡 REST API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user | No |
| `POST` | `/api/auth/login/` | Obtain access & refresh JWT tokens | No |
| `POST` | `/api/auth/refresh/` | Refresh access token | No |
| `GET` | `/api/auth/me/` | Current user profile | Yes |
| `GET` | `/api/habits/` | List all user's habits with streaks & today's status | Yes |
| `POST` | `/api/habits/` | Create a new habit | Yes |
| `GET` | `/api/habits/{id}/` | Retrieve habit details | Yes |
| `PUT/PATCH` | `/api/habits/{id}/` | Update an existing habit | Yes |
| `DELETE` | `/api/habits/{id}/` | Delete a habit | Yes |
| `POST` | `/api/habits/{id}/check/` | Check-in habit for date (default: today) | Yes |
| `DELETE` | `/api/habits/{id}/check/` | Undo check-in for date | Yes |
| `GET` | `/api/habits/stats/` | Habit summary, streak, success rates & calendar dates | Yes |
