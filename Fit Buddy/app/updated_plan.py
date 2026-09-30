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


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
) -> str:

    # Demo mode.
    if settings.demo_mode or not settings.gemini_api_key:

        return f"""
UPDATED FITBUDDY PLAN

USER FEEDBACK
-------------
{feedback}


ORIGINAL PLAN
-------------
{original_plan}


ADJUSTMENT NOTE
---------------
Your feedback has been recorded.

The updated plan should apply the requested changes
gradually while maintaining at least one recovery day.

Always adjust intensity if recovery becomes difficult.
"""

    prompt = f"""
Revise the workout plan below using the user's feedback.

FITNESS GOAL:
{goal}

INTENSITY:
{intensity}


ORIGINAL PLAN
-------------
{original_plan}


USER FEEDBACK
-------------
{feedback}


REQUIREMENTS
------------

1. Return a complete Day 1 through Day 7 plan.
2. Do not return only a list of changes.
3. Preserve useful parts of the original plan.
4. Implement the user's feedback where safe and reasonable.
5. Keep at least one recovery/rest day.
6. Do not provide medical diagnosis.
7. Do not provide medical treatment.
8. Do not recommend dangerous exercise.
9. Do not recommend extreme dieting.
10. Keep the result easy to read.
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
            "Gemini returned an empty updated plan."
        )

    return response.text.strip()