from datetime import datetime, timezone
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import (
    Session,
    joinedload
)

from .database import get_db

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)

from .gemini_generator import (
    generate_workout_gemini
)

from .models import Plan, User

from .schemas import (
    FeedbackRequest,
    PlanResponse,
    UserInput
)

from .updated_plan import (
    update_workout_plan
)


router = APIRouter()


TEMPLATES = Jinja2Templates(
    directory=str(
        Path(__file__).resolve().parent.parent / "templates"
    )
)


def _get_user(
    db: Session,
    user_id: str
) -> User | None:

    return (
        db.query(User)
        .options(joinedload(User.plan))
        .filter(User.user_id == user_id)
        .first()
    )


def _plan_response(user: User) -> PlanResponse:

    if user.plan is None:
        raise RuntimeError(
            "User does not have a workout plan."
        )

    return PlanResponse(
        user={
            "id": user.id,
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        },

        original_plan=user.plan.original_plan,

        updated_plan=user.plan.updated_plan,

        nutrition_tip=user.plan.nutrition_tip,

        feedback=user.plan.feedback
    )


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return TEMPLATES.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        }
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "fitbuddy"
    }


# ---------------------------------------------------------
# GENERATE WORKOUT - API
# ---------------------------------------------------------

@router.post(
    "/api/generate-workout",
    response_model=PlanResponse
)
def api_generate(
    payload: UserInput,
    db: Session = Depends(get_db)
):

    try:

        workout = generate_workout_gemini(
            payload.name,
            payload.age,
            payload.weight,
            payload.goal,
            payload.intensity
        )

        tip = generate_nutrition_tip_with_flash(
            payload.goal
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI generation failed: {exc}"
        ) from exc


    user = _get_user(
        db,
        payload.user_id
    )


    # New user
    if user is None:

        user = User(
            **payload.model_dump()
        )

        db.add(user)

        db.flush()


    # Existing user
    else:

        for key, value in payload.model_dump().items():

            setattr(
                user,
                key,
                value
            )


    # Create plan
    if user.plan is None:

        user.plan = Plan(
            original_plan=workout,
            nutrition_tip=tip
        )


    # Replace previous generated plan
    else:

        user.plan.original_plan = workout

        user.plan.updated_plan = None

        user.plan.feedback = None

        user.plan.nutrition_tip = tip

        user.plan.updated_at = None


    db.commit()

    db.refresh(user)


    return _plan_response(user)


# ---------------------------------------------------------
# GENERATE WORKOUT - HTML FORM
# ---------------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout_form(
    request: Request,

    name: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        payload = UserInput(
            name=name,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )


        result = api_generate(
            payload,
            db
        )


        return TEMPLATES.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "data": result.model_dump(),
                "message": None,
                "error": None
            }
        )

    except Exception as exc:

        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            }
        )


# ---------------------------------------------------------
# FEEDBACK - API
# ---------------------------------------------------------

@router.post(
    "/api/submit-feedback",
    response_model=PlanResponse
)
def api_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db)
):

    user = _get_user(
        db,
        payload.user_id
    )


    if user is None or user.plan is None:

        raise HTTPException(
            status_code=404,
            detail="User or workout plan not found."
        )


    try:

        revised = update_workout_plan(
            user.plan.original_plan,
            payload.feedback,
            user.goal,
            user.intensity
        )


        tip = generate_nutrition_tip_with_flash(
            user.goal
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI update failed: {exc}"
        ) from exc


    user.plan.updated_plan = revised

    user.plan.feedback = payload.feedback

    user.plan.nutrition_tip = tip

    user.plan.updated_at = datetime.now(
        timezone.utc
    )


    db.commit()

    db.refresh(user)


    return _plan_response(user)


# ---------------------------------------------------------
# FEEDBACK - HTML FORM
# ---------------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback_form(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        result = api_feedback(
            FeedbackRequest(
                user_id=user_id,
                feedback=feedback
            ),
            db
        )


        return TEMPLATES.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "data": result.model_dump(),
                "message": (
                    "Your feedback was applied "
                    "and the plan was updated."
                ),
                "error": None
            }
        )

    except Exception as exc:

        user = _get_user(
            db,
            user_id
        )


        if user and user.plan:

            data = _plan_response(
                user
            ).model_dump()


            return TEMPLATES.TemplateResponse(
                request=request,
                name="result.html",
                context={
                    "data": data,
                    "message": None,
                    "error": str(exc)
                }
            )


        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            }
        )


# ---------------------------------------------------------
# GET ALL USERS - API
# ---------------------------------------------------------

@router.get(
    "/api/users",
    response_model=list[PlanResponse]
)
def api_users(
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .options(joinedload(User.plan))
        .order_by(User.created_at.desc())
        .all()
    )


    return [
        _plan_response(user)
        for user in users
        if user.plan
    ]


# ---------------------------------------------------------
# GET ONE USER - API
# ---------------------------------------------------------

@router.get(
    "/api/users/{user_id}",
    response_model=PlanResponse
)
def api_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = _get_user(
        db,
        user_id
    )


    if user is None or user.plan is None:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    return _plan_response(user)


# ---------------------------------------------------------
# DELETE USER - API
# ---------------------------------------------------------

@router.delete(
    "/api/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def api_delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = _get_user(
        db,
        user_id
    )


    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    db.delete(user)

    db.commit()


# ---------------------------------------------------------
# ADMIN HTML PAGE
# ---------------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .options(joinedload(User.plan))
        .order_by(User.created_at.desc())
        .all()
    )


    return TEMPLATES.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users
        }
    )


# ---------------------------------------------------------
# DELETE USER - ADMIN HTML
# ---------------------------------------------------------

@router.post(
    "/delete-user/{user_id}"
)
def delete_user_form(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = _get_user(
        db,
        user_id
    )


    if user:

        db.delete(user)

        db.commit()


    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )