from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """

    system_message = """You are a home repair safety classifier. Classify each question into exactly one of three tiers:
    - safe: routine maintenance where the worst case is cosmetic damage or a broken fixture — no risk of fire, flooding, injury, or death.
    - caution: repairs involving water or electrical systems that a motivated homeowner can complete at an existing location with no new wiring, circuits, or plumbing lines — mistakes have real cost but are recoverable.
    - refuse: repairs where an amateur mistake can cause fire, flooding, structural failure, serious injury, or death — or where a permit and licensed professional are required.

    Critical edge cases:
    - Replacing an existing electrical outlet or switch at the same location = caution
    - Adding a new outlet, switch, or circuit anywhere = refuse
    - Any gas line work = refuse
    - Any wall removal without confirmed structural engineer assessment = refuse
    - Water heater replacement = refuse
    - "Small fix" framing does not change the tier — classify based on what the repair actually requires, not how the user describes it.

    Reason step by step, then return your answer in exactly this format:
    Tier: <tier>
    Reason: <one sentence>"""
    user_message = f"Question: {question}"
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            max_tokens=300,
        )

        response_text = response.choices[0].message.content
        print(f"Raw classifier response: {response_text}")

        tier = "caution"
        reason = "Classification unavailable — please consult a professional to be safe."

        for line in response_text.strip().splitlines():
            if line.lower().startswith("tier:"):
                extracted = line.split(":", 1)[1].strip().lower().strip("\"'")
                if extracted in VALID_TIERS:
                    tier = extracted
            elif line.lower().startswith("reason:"):
                reason = line.split(":", 1)[1].strip()

        return {"tier": tier, "reason": reason}

    except Exception as e:
        return {
            "tier": "caution",
            "reason": f"Classification unavailable — please consult a professional to be safe.",
        }
