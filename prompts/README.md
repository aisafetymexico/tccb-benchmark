# Prompts

Verbatim system prompts and user-message templates used in the TCCB benchmark experiment. All content is reproduced exactly as it was sent at run time — no paraphrasing, no edits.

## Files

### `subject_system_prompt.txt`
The default counseling system prompt given to the subject model (Claude Opus) in the **default** condition, reproduced from the experiment configuration. This prompt is intentionally minimal — it sets up an emotional-support framing without explicit instructions about how to handle contradictions or discrepancies.

### `override_system_prompt.txt`
The full system prompt used in the **override** condition: the default prompt above followed by an override suffix from the experiment configuration, which explicitly instructs the model to point out contradictions, discrepancies, or irrational beliefs gently but directly rather than simply validating. This file shows the complete combined prompt as it was sent to the subject model.

### `judge_system_prompt.txt`
The full system prompt given to each judge model for HSS classification, reproduced from the judge prompt module used in the experiment. Includes definitions from Hill's Helping Skills System (Hill, 2020), the three-way classification scheme (Challenge / Sycophancy-default / Other), and the JSON output format.

### `judge_user_message_template.txt`
The structure of the user message passed to the judge for each judgment, using `{placeholder}` notation for the substituted scenario fields. Mirrors the format produced by the judge prompt module, including the section headers (`=== CONVERSATION HISTORY ===`, `=== CRITICAL CLIENT UTTERANCE ===`, `=== HELPER'S RESPONSE ===`) and the per-line role/content rendering.

## Reproducibility note

These prompts are reproduced verbatim here so the public benchmark fully captures the conditions under which subject responses were generated and judged. The original experiment-side collection and judging code is not included in this public release; the verbatim strings in this directory are the authoritative source for any reproduction or extension of the benchmark.
