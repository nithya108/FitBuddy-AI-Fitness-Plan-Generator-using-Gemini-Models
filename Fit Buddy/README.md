# FitBuddy – AI Fitness Plan Generator

FitBuddy is an AI-powered fitness planning web application.

It uses:

- FastAPI
- Python
- Jinja2
- SQLite
- SQLAlchemy
- Google Gemini
- HTML
- CSS
- Pydantic

The application generates personalized 7-day workout plans and nutrition/recovery tips.

Users can also submit feedback and generate an updated workout plan.


# FEATURES

## 1. Workout Generation

The user provides:

- Name
- User ID
- Age
- Weight
- Fitness goal
- Workout intensity

FitBuddy generates a 7-day workout plan.


## 2. Nutrition Tip

FitBuddy generates a nutrition or recovery tip according to the user's fitness goal.


## 3. Feedback

The user can provide feedback such as:

"Add more cardio."

"Make Day 6 easier."

"Include another recovery day."

The AI generates an updated plan.


## 4. SQLite Database

User information and workout plans are stored in SQLite using SQLAlchemy.


## 5. Admin Dashboard

The admin page displays:

- User
- Age
- Weight
- Goal
- Intensity
- Original plan
- Updated plan


# PROJECT STRUCTURE

FitBuddy/

    app/

        __init__.py

        main.py

        config.py

        database.py

        models.py

        schemas.py

        routes.py

        gemini_generator.py

        gemini_flash_generator.py

        updated_plan.py


    templates/

        base.html

        index.html

        result.html

        all_users.html


    static/

        style.css


    tests/

        test_app.py


    .env.example

    .gitignore

    requirements.txt

    README.md


# INSTALLATION

Open the FitBuddy folder in VS Code.


## Step 1

Open:

Terminal → New Terminal


## Step 2

Create virtual environment:

python -m venv .venv


## Step 3

Activate it.

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Windows Command Prompt:

.venv\Scripts\activate


## Step 4

Install dependencies:

python -m pip install --upgrade pip

pip install -r requirements.txt


# ENVIRONMENT CONFIGURATION

Copy:

.env.example

Rename the copy to:

.env


For testing without Gemini:

DEMO_MODE=true


For Gemini:

GEMINI_API_KEY=your_api_key_here

DEMO_MODE=false


# RUN APPLICATION

Run:

uvicorn app.main:app --reload


Open:

http://127.0.0.1:8000


# API DOCUMENTATION

Open:

http://127.0.0.1:8000/docs


# ADMIN PAGE

Open:

http://127.0.0.1:8000/view-all-users


# API ENDPOINTS

GET /

Home page.


GET /health

Health check.


POST /generate-workout

HTML workout generation.


POST /submit-feedback

HTML feedback submission.


POST /api/generate-workout

JSON workout generation.


POST /api/submit-feedback

JSON feedback update.


GET /api/users

Get all users.


GET /api/users/{user_id}

Get one user.


DELETE /api/users/{user_id}

Delete a user.


# SAMPLE API REQUEST

POST /api/generate-workout

JSON:

{
    "name": "Srinidhi",
    "user_id": "USER001",
    "age": 20,
    "weight": 55,
    "goal": "muscle gain",
    "intensity": "medium"
}


# SAMPLE FEEDBACK REQUEST

POST /api/submit-feedback

JSON:

{
    "user_id": "USER001",
    "feedback": "Add more cardio and make Day 6 easier."
}


# TESTING

Run:

pytest -q


# DATABASE

The application automatically creates:

fitbuddy.db

when the server starts.


# DEMO MODE

DEMO_MODE=true

allows the application to run without a Gemini API key.

This is useful for:

- Project demonstrations
- UI testing
- Database testing
- API testing


# GEMINI MODE

Set:

GEMINI_API_KEY=your_real_api_key

and:

DEMO_MODE=false


Then restart the server.


# APPLICATION FLOW

User

↓

index.html

↓

FastAPI

↓

Pydantic validation

↓

Gemini AI

↓

Workout + Nutrition Tip

↓

SQLite

↓

result.html

↓

User Feedback

↓

Gemini AI

↓

Updated Plan

↓

SQLite


# SAFETY

FitBuddy is an educational wellness-planning application.

AI-generated plans should not be treated as medical advice.

Users should seek qualified professional advice when appropriate.