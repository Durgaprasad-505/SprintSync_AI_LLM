"""AI service: live OpenAI call with deterministic stub fallback."""
from typing import Optional
import json

from config import settings


STUB_DESCRIPTION = (
    "This task involves researching, planning, and implementing the core feature. "
    "Break it down into subtasks: (1) gather requirements, (2) design the approach, "
    "(3) implement incrementally, (4) write tests, (5) review and iterate."
)

STUB_DAILY_PLAN = {
    "plan": [
        {"time": "09:00", "activity": "Review backlog and pick top 3 tasks"},
        {"time": "09:30", "activity": "Deep work block — tackle highest-priority task"},
        {"time": "12:00", "activity": "Lunch + async comms (email/Slack)"},
        {"time": "13:00", "activity": "Continue top-priority task or start second task"},
        {"time": "15:30", "activity": "Code review / collaboration / unblocking teammates"},
        {"time": "16:30", "activity": "Wrap up, update task statuses, log time"},
        {"time": "17:00", "activity": "Plan tomorrow — update estimates.csv"},
    ],
    "source": "stub",
}


def _use_stub() -> bool:
    return settings.USE_AI_STUB or not settings.OPENAI_API_KEY


async def generate_task_description(title: str) -> dict:
    """Generate a task description from a short title."""
    if _use_stub():
        return {
            "title": title,
            "description": f"[STUB] {STUB_DESCRIPTION}",
            "source": "stub",
        }

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful engineering project manager. "
                        "Given a short task title, write a clear, concise task description "
                        "(2-4 sentences) that explains what needs to be done and why it matters. "
                        "Be specific and actionable."
                    ),
                },
                {"role": "user", "content": f"Task title: {title}"},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        description = response.choices[0].message.content.strip()
        return {"title": title, "description": description, "source": "openai"}
    except Exception as exc:
        # Graceful degradation: fall back to stub on any error
        return {
            "title": title,
            "description": STUB_DESCRIPTION,
            "source": "stub-fallback",
            "error": str(exc),
        }


async def generate_daily_plan(username: str, tasks: list[dict]) -> dict:
    """Return a concise daily plan for the signed-in user."""
    if _use_stub():
        return {**STUB_DAILY_PLAN, "user": username}

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        task_summary = json.dumps(
            [{"title": t["title"], "status": t["status"], "minutes": t["total_minutes"]} for t in tasks],
            indent=2,
        )
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert engineering coach. Given a user's current tasks, "
                        "produce a concise daily schedule in JSON with a 'plan' array of "
                        "objects with 'time' (HH:MM) and 'activity' fields. Max 8 items. "
                        "Respond ONLY with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": f"User: {username}\nTasks:\n{task_summary}",
                },
            ],
            max_tokens=400,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        plan_data = json.loads(response.choices[0].message.content)
        return {**plan_data, "user": username, "source": "openai"}
    except Exception as exc:
        return {**STUB_DAILY_PLAN, "user": username, "source": "stub-fallback", "error": str(exc)}
