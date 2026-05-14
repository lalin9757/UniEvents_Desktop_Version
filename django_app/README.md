# BUBT UniEvents — University Club & Events Management System

A comprehensive University Event and Club Management System for **Bangladesh University of Business and Technology (BUBT)**, built with **Django**. This platform allows students, club presidents, and administrators to manage university clubs, organize events, and handle memberships seamlessly.

---

## Quick Start Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

---

### Step 1 — Install Dependencies

```bash
cd Uni_Events_Management
pip install -r requirements.txt
```

---

### Step 2 — Run Database Migrations

```bash
python manage.py migrate
```

---

### Step 3 — Create Super Admin

```bash
python manage.py createsuperuser
```

When prompted, use:
- **Username:** `superadmin`
- **Email:** `superadmin@bubt.edu.bd`
- **Password:** `superadmin` *(or any password you prefer)*

Or run the automated setup:

```bash
python create_superadmin.py
```

---

### Step 4 — Seed the Database with BUBT Club Data

This script will:
- Delete all previous club/event/member data
- Keep Super Admin and Admin accounts intact
- Create 15 official BUBT clubs (from bubt.edu.bd navbar)
- Assign 1 unique President per club
- Add 5 members per club
- Create 1 ongoing event per club

```bash
python seed_data.py
```

---

### Step 5 — Start the Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## Login Credentials After Seeding

| Role | Username | Password |
|------|----------|----------|
| Super Admin | `superadmin` | `superadmin` |
| President (EEE Club) | `eeeclub_pres` | `EEEClub@2025` |
| President (IT Club) | `itclub_pres` | `ITClub@2025` |
| President (Business Club) | `bizclub_pres` | `BizClub@2025` |
| President (Cultural Club) | `cultural_pres` | `CulturalClub@2025` |
| President (Sports Club) | `sports_pres` | `SportsClub@2025` |
| President (English Club) | `english_pres` | `EnglishClub@2025` |
| President (Photography) | `photo_pres` | `PhotoClub@2025` |
| President (Social Welfare) | `welfare_pres` | `WelfareClub@2025` |
| President (Debating) | `debate_pres` | `DebateClub@2025` |
| President (Economics) | `eco_pres` | `EcoClub@2025` |
| President (IEEE) | `ieee_pres` | `IEEEBUBT@2025` |
| President (BNCC) | `bncc_pres` | `BNCCBUBT@2025` |
| President (Moot Court) | `moot_pres` | `MootBUBT@2025` |
| President (Rover Scout) | `scout_pres` | `ScoutBUBT@2025` |
| President (BASIS) | `basis_pres` | `BasisBUBT@2025` |
| Student | `it_m1` | `Student@123` |
| Student | `eee_m1` | `Student@123` |

---

## BUBT Clubs Included (from bubt.edu.bd Navbar)

1. BUBT EEE Club
2. BUBT Rover Scout Group
3. BUBT IT Club
4. BUBT Business Club
5. BUBT Cultural Club
6. BUBT Sports Club
7. BUBT English Language Club
8. BUBT Photography Club
9. BUBT Social Welfare Club
10. BUBT Debating Club
11. BUBT Economics Club
12. IEEE Student Branch BUBT
13. Bangladesh National Cadet Corps BUBT
14. BUBT Moot Court Society
15. BASIS Students Forum BUBT Chapter

---

## Features

- **Role-based Access** — Super Admin, Admin, Club President, Student
- **Club Management** — Create, edit, manage clubs with categories
- **Event Management** — Create events, handle registrations, event requests workflow
- **Member Management** — Presidents manage their club members and join requests
- **Statistics Dashboard** — Admin overview of platform activity
- **REST API** — Full API at `/api/` for programmatic access
- **Premium UI** — Dark professional theme with SVG icons

---

## Tech Stack

- **Backend:** Django 4.2
- **API:** Django REST Framework
- **Frontend:** Django Templates (custom CSS, no Bootstrap dependency)
- **Database:** SQLite (default)
- **Image Handling:** Pillow

---

## Project Structure

```
├── accounts/       # User management and profiles
├── api/            # REST API endpoints
├── clubs/          # Club management and memberships
├── config/         # Django settings
├── events/         # Event management and registrations
├── templates/      # HTML templates (dark premium UI)
├── seed_data.py    # Database seeding script
├── manage.py       # Django management script
└── requirements.txt
```

---

## Troubleshooting

**Issue:** `No module named 'django'`
**Fix:** `pip install -r requirements.txt`

**Issue:** Database errors
**Fix:** `python manage.py migrate`

**Issue:** Port already in use
**Fix:** `python manage.py runserver 8080`

---

© 2026 BUBT UniEvents
