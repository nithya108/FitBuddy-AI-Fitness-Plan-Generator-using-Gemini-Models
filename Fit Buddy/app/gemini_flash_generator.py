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


def generate_nutrition_tip_with_flash(
    goal: str
) -> str:

    # Local fallback for testing.
    if settings.demo_mode or not settings.gemini_api_key:

        tips = {
            "weight loss": (
                "Build meals around vegetables, a protein source, "
                "whole-food carbohydrates and adequate water. "
                "Avoid extreme calorie restriction."
            ),

            "muscle gain": (
                "Include a protein source in regular meals, "
                "eat enough overall food to support training, "
                "and prioritize sleep and hydration."
            ),

            "general wellness": (
                "Aim for balanced meals containing vegetables "
                "or fruit, protein, whole grains or other minimally "
                "processed carbohydrates, and regular hydration."
            ),

            "flexibility": (
                "Stay hydrated and include protein-rich foods "
                "and a varied diet to support recovery from mobility work."
            ),

            "endurance": (
                "For longer sessions, combine adequate carbohydrates "
                "with protein and fluids, and refuel after training."
            )
        }

        return tips[goal]

    prompt = f"""
Give one concise and practical nutrition or recovery tip
for a person whose fitness goal is:

{goal}

Requirements:
- Keep it under 100 words.
- Give general wellness information.
- Avoid medical claims.
- Avoid extreme dieting.
- Do not prescribe supplements.
- Make the advice practical.
"""

    response = _client().models.generate_content(
        model=settings.gemini_tip_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=300,
            system_instruction=(
                "You are FitBuddy's nutrition and recovery "
                "tip assistant. Provide general wellness "
                "education, not medical advice."
            )
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty nutrition tip."
        )

    return response.text.strip()