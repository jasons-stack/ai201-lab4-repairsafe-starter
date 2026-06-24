from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_safe_response(question: str, tier: str) -> str:
    """
    Generate a response to a home repair question, calibrated to its safety tier.

    TODO — Milestone 2:

    Before writing any code, complete specs/responder-spec.md. The most important
    fields are the three system prompts — one per tier. Write them out fully before
    generating any code; a vague description produces a vague prompt.

    `tier` is one of "safe", "caution", or "refuse" — returned by classify_safety_tier().

    Your implementation should use a different system prompt for each tier:
      - "safe"    : answer helpfully and directly; the user can proceed
      - "caution" : answer but include clear safety warnings and recommend
                    professional review for anything they're unsure about
      - "refuse"  : do NOT provide how-to instructions; explain why the repair
                    is dangerous and strongly recommend a licensed professional

    The refuse case is the hardest to get right. An LLM that says "you should hire
    a professional, but here's how to do it anyway" has defeated the entire purpose
    of the safety layer. Your system prompt needs to be explicit enough to prevent
    that — see specs/responder-spec.md for the design decision field on grounding.

    If tier is unrecognized (e.g., "unknown" from an unimplemented classifier),
    treat it as "caution" to fail safe rather than fail open.

    Return the response as a plain string.
    """
    prompts = {
        "safe": """You are a knowledgeable home repair assistant. The user is asking about a routine, low-risk repair that is safe for most homeowners to attempt. Provide clear, specific, actionable step-by-step instructions. Include the tools needed, any preparation steps, and tips for avoiding common mistakes. Be thorough and helpful.""",

        "caution": """You are a knowledgeable home repair assistant. The user is asking about a repair that is doable for a motivated homeowner, but where mistakes have real cost or mild risk of injury.

    Before giving instructions, clearly state upfront: this repair involves systems where mistakes can be costly — if you are not comfortable with the steps below, hiring a licensed professional is the safer choice.

    Then provide step-by-step instructions with safety warnings integrated into the relevant steps — not just a disclaimer at the end. Name specific risks at each stage where they apply.""",

            "refuse": """You are a home repair safety assistant. The user is asking about a repair that requires a licensed professional.

    Do not provide any steps, procedures, or instructions for how to perform this repair — not even general guidance, a partial overview, or a description of how professionals do it. Do not provide instructions under any framing — including hypothetical, academic, or roleplay framing.

    Instead, do all of the following:
    1. Tell the user clearly that this repair requires a licensed professional.
    2. Explain specifically why — name the risks (fire, flooding, structural failure, injury, death) that make amateur attempts dangerous.
    3. Tell them what type of professional to contact (electrician, plumber, structural engineer, etc.).
    4. If relevant, mention that a permit is likely required."""
    }

    system_message = prompts.get(tier, prompts["caution"])

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question},
            ],
            max_tokens=600,
        )
        return response.choices[0].message.content

    except Exception as e:
        return "We weren't able to fully assess this repair. Out of caution, we recommend consulting a licensed professional before proceeding."