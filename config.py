"""
config.py  –  Central configuration loader
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── API ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

FRAUD_AGENT_MODEL   = os.getenv("FRAUD_AGENT_MODEL",   "llama-3.3-70b-versatile")
EDD_EVALUATOR_MODEL = os.getenv("EDD_EVALUATOR_MODEL", "llama-3.3-70b-versatile")

# ── Storage ───────────────────────────────────────────────────────────────────
DB_PATH   = os.getenv("DB_PATH",   "fraud_investigation.db")
DATA_PATH = os.getenv("DATA_PATH", "synthetic_transactions.json")

# ── Scoring weights (must sum to 1.0) ────────────────────────────────────────
WEIGHT_HALLUCINATION = 0.35
WEIGHT_COMPLIANCE    = 0.40
WEIGHT_CALIBRATION   = 0.25

# ── Verdict thresholds ────────────────────────────────────────────────────────
VERDICT_PASS_THRESHOLD   = 75.0
VERDICT_REVIEW_THRESHOLD = 50.0

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_RPM = 28   # max API calls per 60-second sliding window

# ── Retry config ─────────────────────────────────────────────────────────────
API_MAX_RETRIES  = 3
API_RETRY_DELAY  = 5  # seconds between retries on error

# ── Validate critical settings on import ─────────────────────────────────────
if not GROQ_API_KEY:
    raise EnvironmentError(
        "\n\n❌  GROQ_API_KEY is not set.\n"
        "    1. Copy .env.example → .env\n"
        "    2. Get a FREE key from https://console.groq.com\n"
        "    3. Add:  GROQ_API_KEY=your_key_here  to your .env file\n"
    )