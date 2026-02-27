# """AI service: live OpenAI call with deterministic stub fallback."""
# from typing import Optional
# import json

# from config import settings


# STUB_DESCRIPTION = (
#     "This task involves researching, planning, and implementing the core feature. "
#     "Break it down into subtasks: (1) gather requirements, (2) design the approach, "
#     "(3) implement incrementally, (4) write tests, (5) review and iterate."
# )

# STUB_DAILY_PLAN = {
#     "plan": [
#         {"time": "09:00", "activity": "Review backlog and pick top 3 tasks"},
#         {"time": "09:30", "activity": "Deep work block — tackle highest-priority task"},
#         {"time": "12:00", "activity": "Lunch + async comms (email/Slack)"},
#         {"time": "13:00", "activity": "Continue top-priority task or start second task"},
#         {"time": "15:30", "activity": "Code review / collaboration / unblocking teammates"},
#         {"time": "16:30", "activity": "Wrap up, update task statuses, log time"},
#         {"time": "17:00", "activity": "Plan tomorrow — update estimates.csv"},
#     ],
#     "source": "stub",
# }


# def _use_stub() -> bool:
#     return settings.USE_AI_STUB or not settings.OPENAI_API_KEY


# async def generate_task_description(title: str) -> dict:
#     """Generate a task description from a short title."""
#     if _use_stub():
#         return {
#             "title": title,
#             "description": f"[STUB] {STUB_DESCRIPTION}",
#             "source": "stub",
#         }

#     try:
#         from openai import AsyncOpenAI

#         client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
#         response = await client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a helpful engineering project manager. "
#                         "Given a short task title, write a clear, concise task description "
#                         "(2-4 sentences) that explains what needs to be done and why it matters. "
#                         "Be specific and actionable."
#                     ),
#                 },
#                 {"role": "user", "content": f"Task title: {title}"},
#             ],
#             max_tokens=200,
#             temperature=0.7,
#         )
#         description = response.choices[0].message.content.strip()
#         return {"title": title, "description": description, "source": "openai"}
#     except Exception as exc:
#         # Graceful degradation: fall back to stub on any error
#         return {
#             "title": title,
#             "description": STUB_DESCRIPTION,
#             "source": "stub-fallback",
#             "error": str(exc),
#         }


# async def generate_daily_plan(username: str, tasks: list[dict]) -> dict:
#     """Return a concise daily plan for the signed-in user."""
#     if _use_stub():
#         return {**STUB_DAILY_PLAN, "user": username}

#     try:
#         from openai import AsyncOpenAI

#         client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
#         task_summary = json.dumps(
#             [{"title": t["title"], "status": t["status"], "minutes": t["total_minutes"]} for t in tasks],
#             indent=2,
#         )
#         response = await client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are an expert engineering coach. Given a user's current tasks, "
#                         "produce a concise daily schedule in JSON with a 'plan' array of "
#                         "objects with 'time' (HH:MM) and 'activity' fields. Max 8 items. "
#                         "Respond ONLY with valid JSON."
#                     ),
#                 },
#                 {
#                     "role": "user",
#                     "content": f"User: {username}\nTasks:\n{task_summary}",
#                 },
#             ],
#             max_tokens=400,
#             temperature=0.5,
#             response_format={"type": "json_object"},
#         )
#         plan_data = json.loads(response.choices[0].message.content)
#         return {**plan_data, "user": username, "source": "openai"}
#     except Exception as exc:
#         return {**STUB_DAILY_PLAN, "user": username, "source": "stub-fallback", "error": str(exc)}
"""AI service: custom trained model with stub fallback."""
from typing import Optional
import json
import torch

from config import settings

# ── Load custom model once at startup ─────────────────────────────────────
_model = None
_tokenizer = None

def load_custom_model():
    global _model, _tokenizer
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel

        print("Loading custom SprintSync model...")
        MODEL_PATH = "./LLM_model_trainig/sprintsync-model/final"
        BASE_MODEL  = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

        base = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
        _model = PeftModel.from_pretrained(base, MODEL_PATH)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model.eval()
        print("Custom model loaded successfully!")
    except Exception as e:
        print(f"Custom model failed to load: {e}")
        print("Will use stub fallback.")


def _generate_with_model(title: str) -> str:
    prompt = f"Task title: {title}\n\nDescription:"
    inputs = _tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            pad_token_id=_tokenizer.eos_token_id,
        )

    full_text = _tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the description part after "Description:"
    description = full_text.split("Description:")[-1].strip()
    # Clean up — stop at end of text token if present
    description = description.split("<|endoftext|>")[0].strip()
    return description


# ── Stub fallbacks ─────────────────────────────────────────────────────────
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
    return settings.USE_AI_STUB or _model is None


# ── Public functions ───────────────────────────────────────────────────────
async def generate_task_description(title: str) -> dict:
    """Generate a task description using custom trained model."""
    if _use_stub():
        return {
            "title": title,
            "description": f"[STUB] {STUB_DESCRIPTION}",
            "source": "stub",
        }

    try:
        description = _generate_with_model(title)
        return {
            "title": title,
            "description": description,
            "source": "custom-model",   # shows custom-model in UI
        }
    except Exception as exc:
        return {
            "title": title,
            "description": STUB_DESCRIPTION,
            "source": "stub-fallback",
            "error": str(exc),
        }


async def generate_daily_plan(username: str, tasks: list[dict]) -> dict:
    """Daily plan — still uses OpenAI if available, else stub."""
    if settings.USE_AI_STUB or not settings.OPENAI_API_KEY:
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