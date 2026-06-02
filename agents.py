"""
agents.py – LLM logic for the Fraud Investigator and EDD Evaluator
            Powered by Groq (free tier) with a precise 28 req/min rate limiter
"""
import json
import re
import time
import collections
from groq import Groq

from config import (
    GROQ_API_KEY,
    FRAUD_AGENT_MODEL,
    EDD_EVALUATOR_MODEL,
    WEIGHT_HALLUCINATION,
    WEIGHT_COMPLIANCE,
    WEIGHT_CALIBRATION,
    API_MAX_RETRIES,
    API_RETRY_DELAY,
    RATE_LIMIT_RPM,
)

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)


# ── Sliding-window rate limiter ───────────────────────────────────────────────
class RateLimiter:
    """
    Ensures we never exceed RATE_LIMIT_RPM calls in any 60-second window.

    Uses a deque of timestamps. Before every call:
      1. Drop timestamps older than 60 s.
      2. If the window is already full, sleep until the oldest call
         is exactly 60 s old (i.e. falls out of the window).
      3. Record the new call's timestamp and proceed.
    """
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self._window = collections.deque()   # timestamps of recent calls

    def wait(self):
        now = time.monotonic()
        window_start = now - 60.0

        # Evict calls older than 60 s
        while self._window and self._window[0] <= window_start:
            self._window.popleft()

        # If at the limit, sleep until the oldest call leaves the window
        if len(self._window) >= self.max_per_minute:
            sleep_for = 60.0 - (now - self._window[0]) + 0.05  # +50 ms safety margin
            if sleep_for > 0:
                print(f"  🕐 Rate limit: {self.max_per_minute} req/min reached — "
                      f"waiting {sleep_for:.1f}s…")
                time.sleep(sleep_for)

        self._window.append(time.monotonic())


# One shared limiter for the entire process
_limiter = RateLimiter(RATE_LIMIT_RPM)


# ── Core Groq call ────────────────────────────────────────────────────────────
def _call_groq(model_name: str, prompt: str, max_tokens: int = 1024) -> str:
    """
    Waits for a rate-limit slot, then calls Groq.
    Retries up to API_MAX_RETRIES times on transient errors.
    """
    for attempt in range(1, API_MAX_RETRIES + 1):
        _limiter.wait()          # blocks only when the window is full
        try:
            response = client.chat.completions.create(
                model=model_name,
                temperature=0.0,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise financial-crime analyst. "
                            "Always respond with a single raw JSON object — "
                            "no markdown fences, no extra text, no explanation outside the JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as exc:
            if attempt == API_MAX_RETRIES:
                raise
            print(f"  ⚠️  Groq error (attempt {attempt}/{API_MAX_RETRIES}): {exc}"
                  f"  – retrying in {API_RETRY_DELAY}s…")
            time.sleep(API_RETRY_DELAY)


def _extract_json(text: str) -> dict:
    """Pulls the first JSON object out of a model reply."""
    # Using `{3}` instead of triple backticks to prevent python syntax errors on copy/paste
    clean = re.sub(r"`{3}(?:json)?", "", text, flags=re.IGNORECASE).strip()
    start = clean.find("{")
    end   = clean.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in model output:\n{text}")
    return json.loads(clean[start:end])


# ── Agent 1: Frontline Fraud Investigator ────────────────────────────────────
def investigate_transaction(txn_data: dict) -> dict:
    prompt = f"""
Review the bank transaction below and classify it as one of:
  - "Fraud"
  - "Legitimate"
  - "Escalate"
  
CRITICAL DEFINITIONS FOR YOUR DECISION:
- "Legitimate": The transaction aligns with the user's historical behavior, shows normal velocity, and originates from consistent location/device data.
- "Fraud": There are glaring, undeniable indicators of malicious activity (e.g., impossible travel, massive velocity spikes, uncharacteristic high-risk merchants with unknown devices).
- "Escalate": The transaction is highly ambiguous and requires manual human review. Use this label STRICTLY for conflicting signals. Examples: A very high-value purchase but originating from a known device; a mismatched IP address but normal merchant category; or an uncharacteristic purchase on a brand-new account where fraud isn't definitively proven.

Return ONLY a JSON object with exactly two keys:
  "decision"  : one of "Fraud", "Legitimate", or "Escalate"
  "reasoning" : a concise explanation citing specific data points from the transaction

Transaction Data:
{json.dumps(txn_data, indent=2)}
"""
    try:
        return _extract_json(_call_groq(FRAUD_AGENT_MODEL, prompt, max_tokens=512))
    except Exception as e:
        return {"decision": "Escalate", "reasoning": f"API or parsing failure: {str(e)}"}


# ── Agent 2: EDD Compliance Auditor ──────────────────────────────────────────
def evaluate_investigation(txn_data: dict, agent_decision: str, agent_reasoning: str) -> dict:
    prompt = f"""
You are an EDD (Enhanced Due Diligence) compliance auditor.
Score the frontline analyst's response out of 100 on each dimension:

  hallucination_score : Did the agent invent or misrepresent facts not in the data?
                        (100 = no hallucinations, 0 = severe fabrication)
  compliance_score    : Did the agent follow standard fraud-detection logic?
                        (100 = textbook-correct reasoning)
  calibration_score   : Is the stated risk level proportionate to the evidence?
                        (100 = perfectly calibrated)

Transaction Data  : {json.dumps(txn_data)}
Agent Decision    : {agent_decision}
Agent Reasoning   : {agent_reasoning}

Return ONLY a JSON object in this exact format (integer values 0-100):
{{"hallucination_score": 90, "compliance_score": 85, "calibration_score": 95}}
"""
    try:
        scores = _extract_json(_call_groq(EDD_EVALUATOR_MODEL, prompt, max_tokens=128))
        final_score = (
            scores.get("hallucination_score", 0) * float(WEIGHT_HALLUCINATION)
            + scores.get("compliance_score",   0) * float(WEIGHT_COMPLIANCE)
            + scores.get("calibration_score",  0) * float(WEIGHT_CALIBRATION)
        )
        scores["final_edd_score"] = round(final_score, 2)
        return scores
    except Exception:
        return {"hallucination_score": 0, "compliance_score": 0,
                "calibration_score": 0, "final_edd_score": 0.0}