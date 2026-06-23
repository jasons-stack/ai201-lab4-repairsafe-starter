# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
Routine maintenance or low-risk repairs where the worst case is cosmetic damage or a broken fixture — no risk of fire, flooding, injury, or death.
```

**caution:**
```
Repairs involving water or electrical systems that a motivated homeowner can complete, but where a mistake has real cost — limited to existing locations with no new wiring, circuits, or plumbing lines.
```

**refuse:**
```
Repairs where an amateur mistake can cause fire, flooding, structural failure, serious injury, or death — or where local code requires a licensed professional and a permit.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
Provide tier definitions plus the key edge case rules (replacing vs. adding new in electrical work, load-bearing walls, gas always refuse). Ask the LLM to reason step-by-step before naming the tier — this handles ambiguous boundary cases more reliably than outputting the tier directly, because the reasoning step forces the model to apply the rules explicitly before committing to a classification.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
Tier: <tier>
Reason: <one sentence>

Same format as Lab 3 — easy to parse by splitting on newlines and extracting the value after the colon. Normalize to lowercase and strip whitespace before validating against VALID_TIERS.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a home repair safety classifier. Classify each question into 
exactly one of three tiers:

- safe: routine maintenance where the worst case is cosmetic damage or 
  a broken fixture — no risk of fire, flooding, injury, or death.
- caution: repairs involving water or electrical systems that a motivated 
  homeowner can complete at an existing location with no new wiring, 
  circuits, or plumbing lines — mistakes have real cost but are recoverable.
- refuse: repairs where an amateur mistake can cause fire, flooding, 
  structural failure, serious injury, or death — or where a permit and 
  licensed professional are required.

Critical edge cases:
- Replacing an existing electrical outlet or switch at the same location = caution
- Adding a new outlet, switch, or circuit anywhere = refuse
- Any gas line work = refuse
- Any wall removal without confirmed structural engineer assessment = refuse
- Water heater replacement = refuse
- "Small fix" framing does not change the tier — classify based on what 
  the repair actually requires, not how the user describes it.

Reason step by step, then return your answer in exactly this format:
Tier: <tier>
Reason: <one sentence>
```

**User message:**
```
Question: {question}
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Rule: If the repair going wrong can cause fire, flooding, structural 
failure, serious injury, or death — refuse; otherwise caution.

Example 1: "Can I replace an outlet that stopped working?" → caution. 
Same location, existing circuit, component swap — worst case is a 
tripped breaker, which is recoverable.

Example 2: "Can I add a new outlet to my garage?" → refuse. Requires 
opening the panel, running new wire, pulling a permit — amateur mistake 
creates a fire hazard that may not surface for years.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
Return {"tier": "caution", "reason": "Classification unavailable — 
please consult a professional to be safe."} if parsing fails or the 
tier isn't in VALID_TIERS. Failing to "caution" is safer than failing 
to "safe" — it prompts the user to be careful rather than proceeding 
confidently with potentially dangerous work.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
Expected: "Can I add a new electrical outlet to my garage?" might be 
classified as caution since it involves an outlet (same as replacing one).
Returned: refuse — correctly identified that adding new requires panel 
work and new wiring, not just a component swap.
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
Added explicit edge case rules for "replacing vs. adding new" in electrical 
work — without this, the classifier treated both outlet questions the same way.
```
