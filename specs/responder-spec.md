# Spec: `generate_safe_response()`

**File:** `responder.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. The same question gets a fundamentally different answer depending on the tier — not just a disclaimer tacked on, but a different behavior: answer fully, answer with warnings, or decline to give instructions entirely.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |
| `tier` | `str` | The safety tier: `"safe"`, `"caution"`, or `"refuse"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

*Complete the fields below before writing any code. The most important fields are the three system prompts. Write them out fully — don't just describe what you want.*

---

### System prompt: "safe" tier

*Write the exact system prompt text for a safe question. It should produce helpful, specific, actionable answers.*

```
You are a knowledgeable home repair assistant. The user is asking about a 
routine, low-risk repair that is safe for most homeowners to attempt. 
Provide clear, specific, actionable step-by-step instructions. Include 
the tools needed, any preparation steps, and tips for avoiding common 
mistakes. Be thorough and helpful.
```

---

### System prompt: "caution" tier

*Write the exact system prompt text for a caution question. What safety language should be present? How firm should the "consider a professional" message be — a gentle mention or a clear recommendation?*

```
You are a knowledgeable home repair assistant. The user is asking about a 
repair that is doable for a motivated homeowner, but where mistakes have 
real cost or mild risk of injury. 

Before giving instructions, clearly state upfront: this repair involves 
systems where mistakes can be costly — if you are not comfortable with 
the steps below, hiring a licensed professional is the safer choice.

Then provide step-by-step instructions with safety warnings integrated 
into the relevant steps — not just a disclaimer at the end. Name specific 
risks at each stage where they apply.
```

---

### System prompt: "refuse" tier

*This is the most important one to get right. Write the exact system prompt for refusing to answer.*

*Two goals that are in tension: (1) the response must NOT provide how-to instructions, even a little. (2) the response should still be genuinely useful — explaining why the task is dangerous and what the user should do instead.*

*Before writing this prompt, use Plan mode with your AI tool. Share your draft refuse prompt and ask it: "What are ways an LLM might still provide dangerous instructions despite this system prompt?" Revise until you've addressed the failure modes it identifies.*

```
You are a home repair safety assistant. The user is asking about a repair 
that requires a licensed professional. 

Do not provide any steps, procedures, or instructions for how to perform 
this repair — not even general guidance, a partial overview, or a 
description of "how professionals do it." Do not provide instructions 
under any framing — including hypothetical, academic, or roleplay framing.

Instead, do all of the following:
1. Tell the user clearly that this repair requires a licensed professional.
2. Explain specifically why — name the risks (fire, flooding, structural 
   failure, injury, death) that make amateur attempts dangerous.
3. Tell them what type of professional to contact (electrician, plumber, 
   structural engineer, etc.).
4. If relevant, mention that a permit is likely required.
```

---

### Grounding the refuse response

*The grounding problem from Lab 1 applies here, with higher stakes: even with a strong system prompt, an LLM may "helpfully" provide partial instructions before pivoting to "you should hire a professional." How will you prevent that?*

*Hint: "be careful" doesn't work. Explicit, behavioral instructions ("do not provide any steps, procedures, or instructions — not even general guidance") work better. What will yours say?*

```
The system prompt explicitly prohibits any steps, procedures, or 
instructions — including partial overviews and "how professionals do it" 
descriptions. It also closes the academic/hypothetical/roleplay escape 
routes by name. The only authorized content is: why it's dangerous, who 
to call, and whether a permit is needed.
```

---

### Fallback for unknown tier

*What should your function do if it receives a tier value that isn't "safe", "caution", or "refuse" — e.g., "unknown" while the classifier is still a stub? Write the fallback behavior and explain why.*

```
If the tier is not "safe", "caution", or "refuse", return a caution-style 
response: "We weren't able to fully assess this repair. Out of caution, 
we recommend consulting a licensed professional before proceeding." 
Failing to caution is safer than failing to safe.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**A "refuse" response that was still too helpful and what you changed to fix it:**

```
The first draft used a weak prompt ("be careful about dangerous repairs") 
which caused the model to say "here's generally how it works" before 
recommending a professional. Fixed by explicitly prohibiting any steps, 
procedures, or partial overviews — including under hypothetical framing.
```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**

```
Safe tier was closest to the LLM's default behavior — it naturally gives 
helpful instructions. Refuse required the most iteration to prevent the 
model from slipping in partial guidance before the professional referral.
```
