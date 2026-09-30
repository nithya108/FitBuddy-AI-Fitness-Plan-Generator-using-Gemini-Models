import os


# Use a separate database for tests.
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"

# Use demo mode so tests do not require Gemini.
os.environ["DEMO_MODE"] = "true"


from fastapi.testclient import TestClient

from app.main import app

from app.database import (
    Base,
    engine
)


client = TestClient(app)


def setup_module():

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )


def teardown_module():

    Base.metadata.drop_all(
        bind=engine
    )

    try:

        os.remove(
            "test_fitbuddy.db"
        )

    except FileNotFoundError:

        pass


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_feedback_retrieve_delete():

    payload = {

        "name": "Test User",

        "user_id": "TEST001",

        "age": 22,

        "weight": 60,

        "goal": "muscle gain",

        "intensity": "medium"
    }


    # Generate workout
    response = client.post(
        "/api/generate-workout",
        json=payload
    )


    assert response.status_code == 200


    data = response.json()


    assert "Day 1" in data["original_plan"]


    assert (
        data["user"]["user_id"]
        == "TEST001"
    )


    # Submit feedback
    response = client.post(
        "/api/submit-feedback",
        json={
            "user_id": "TEST001",

            "feedback":
                "Add more cardio and keep "
                "one extra recovery day."
        }
    )


    assert response.status_code == 200


    assert response.json()["updated_plan"]


    # Retrieve user
    response = client.get(
        "/api/users/TEST001"
    )


    assert response.status_code == 200


    # Delete user
    response = client.delete(
        "/api/users/TEST001"
    )


    assert response.status_code == 204


    # Confirm deletion
    response = client.get(
        "/api/users/TEST001"
    )


    assert response.status_code == 404