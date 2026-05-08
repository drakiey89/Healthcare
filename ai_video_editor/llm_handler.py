import json
import logging
import os
import time

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert video editor. Given a word-level transcript, produce a JSON editing plan.

Rules:
- No cuts — the original video plays as one continuous take with overlays applied.
- Available transitions: slide_left, slide_right, push_up, push_down, flash_frame
- Available caption styles: modern_lower_third, kinetic_type, pop_up_caption, minimalist_overlay

Return ONLY valid JSON matching this schema:
{
  "music": {"mood": "<string>", "volume": <0.0-1.0>},
  "clips": [
    {
      "start": <float>,
      "end": <float>,
      "b_roll_keyword": "<string or null>",
      "transition": "<transition_type or null>",
      "caption": "<text or null>",
      "caption_style": "<style or null>",
      "sound_effect": "<query or null>"
    }
  ]
}"""


def generate_editing_script(transcript: list[dict]) -> dict:
    """Send transcript to LLM and return a structured editing plan."""
    import litellm

    model = os.environ["LITELLM_MODEL"]
    api_key = os.environ["LITELLM_API_KEY"]

    transcript_text = " ".join(w["word"] for w in transcript)
    timed_entries = json.dumps(transcript, indent=2)
    user_message = f"Transcript:\n{transcript_text}\n\nWord timestamps:\n{timed_entries}"

    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            response = litellm.completion(
                model=model,
                api_key=api_key,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            if attempt == max_attempts:
                raise
            wait = 2 ** attempt
            logger.warning(f"LLM attempt {attempt} failed ({e}). Retrying in {wait}s…")
            time.sleep(wait)
