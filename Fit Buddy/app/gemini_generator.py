from google import genai
from google.genai import types

from .config import settings


_client_instance = None

def _client() -> genai.Client:
    global _client_instance
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    if _client_instance is None:
        _client_instance = genai.Client(
            api_key=settings.gemini_api_key
        )
    return _client_instance


def _demo_plan(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> str:

    return f"""
FITBUDDY 7-DAY WORKOUT PLAN

Profile
-------
Name: {name}
Age: {age}
Weight: {weight:g} kg
Goal: {goal}
Intensity: {intensity}


DAY 1 – FULL BODY FOUNDATION
--------------------------------
Warm-up:
7 minutes brisk walking and mobility.

Main Workout:
• Bodyweight squats – 3 sets × 10 reps
• Incline push-ups – 3 sets × 8 reps
• Glute bridges – 3 sets × 12 reps
• Plank – 3 sets × 20 seconds

Cooldown:
5 minutes easy walking and gentle stretching.


DAY 2 – CARDIO + CORE
-------------------------
Warm-up:
5 minutes easy walking.

Main Workout:
• Brisk walking or cycling – 20 minutes
• Dead bug – 3 × 10 each side
• Bird dog – 3 × 10 each side

Cooldown:
5 minutes relaxed movement.


DAY 3 – RECOVERY
--------------------
• 20–30 minutes easy walking
• Gentle mobility exercises
• Light stretching

Keep the effort comfortable.


DAY 4 – LOWER BODY
----------------------
Warm-up:
7 minutes mobility.

Main Workout:
• Squats – 3 × 10
• Reverse lunges – 3 × 8 each side
• Hip hinge – 3 × 10
• Calf raises – 3 × 15

Cooldown:
5–8 minutes stretching.


DAY 5 – UPPER BODY + CORE
-----------------------------
Warm-up:
5–7 minutes.

Main Workout:
• Incline push-ups – 3 × 8
• Resistance rows – 3 × 10
• Shoulder press – 3 × 10
• Side plank – 3 × 15 seconds each side

Cooldown:
5 minutes easy stretching.


DAY 6 – GOAL-FOCUSED CONDITIONING
-------------------------------------
Warm-up:
5 minutes.

Main Workout:
5 rounds:
• 2 minutes moderate cardio
• 1 minute easy recovery

Then:
• 2 comfortable core exercises

Cooldown:
5–10 minutes.


DAY 7 – REST / ACTIVE RECOVERY
--------------------------------
• Easy walk
• Light stretching
• Hydration
• Good sleep


GENERAL GUIDANCE
--------------------
• Focus on good exercise form.
• Stop if you experience pain.
• Adjust the workload according to your experience.
• Allow adequate recovery.
"""


def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> str:

    # Demo mode allows the application to run without Gemini.
    if settings.demo_mode or not settings.gemini_api_key:
        return _demo_plan(
            name,
            age,
            weight,
            goal,
            intensity
        )

    prompt = f"""
Create a safe and practical personalized 7-day fitness plan.

USER INFORMATION

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Preferred workout intensity: {intensity}


REQUIREMENTS

1. Give Day 1 through Day 7.
2. Each training day should include:
   - Warm-up
   - Main workout
   - Exercise names
   - Sets and repetitions or duration
   - Cooldown/recovery
3. Include at least one recovery/rest day.
4. Make the plan realistic for a general beginner/intermediate user.
5. Keep the plan easy to read.
6. Do not diagnose medical conditions.
7. Do not prescribe medical treatment.
8. Do not recommend dangerous exercise practices.
9. Do not recommend starvation or dehydration.
10. Avoid extreme recommendations.
11. Provide general wellness guidance only.
"""

    response = _client().models.generate_content(
        model=settings.gemini_workout_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.6,
            max_output_tokens=3000,
            system_instruction=(
                "You are FitBuddy, a cautious fitness-planning "
                "assistant. Provide general wellness guidance, "
                "not medical diagnosis or treatment."
            )
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty workout plan."
        )

    return response.text.strip()