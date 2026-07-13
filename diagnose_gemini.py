"""
GEMINI ROOT CAUSE DIAGNOSTIC
Mirrors the exact execution path of generate_chat_response() step-by-step.
Prints precise exception class, message, and full traceback.
Does NOT touch production code or fallback logic.
"""
import sys
import os
import traceback
import socket
import logging

# Bootstrap: project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("gemini_diagnostic")
SEP = "=" * 65

def section(title, ok=True, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"\n{SEP}\n  [{tag}] {title}")
    if detail:
        print(f"  INFO : {detail}")
    print(SEP)

# ─── STEP 1: Load API key ────────────────────────────────────────────────────
print("\n>>> STEP 1: Load settings.GEMINI_API_KEY")
try:
    from src.config.settings import settings
    key = settings.GEMINI_API_KEY
    present = bool(key and key != "your_gemini_api_key_here")
    preview = (key[:6] + "..." + key[-4:]) if (key and len(key) > 10) else repr(key)
    section("settings.GEMINI_API_KEY", present,
            f"present={present}  preview={preview}  len={len(key) if key else 0}")
    if not present:
        print("ABORT: API key is missing. Fix .env first.")
        sys.exit(1)
except Exception:
    section("settings.GEMINI_API_KEY", False, traceback.format_exc())
    sys.exit(1)

# ─── STEP 2: Import google.generativeai ─────────────────────────────────────
print("\n>>> STEP 2: import google.generativeai as genai")
try:
    import google.generativeai as genai
    import google.api_core.exceptions
    section("import google.generativeai", True)
except Exception:
    section("import google.generativeai", False, traceback.format_exc())
    sys.exit(1)

# ─── STEP 3: genai.configure() ──────────────────────────────────────────────
print("\n>>> STEP 3: genai.configure(api_key=settings.GEMINI_API_KEY)")
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    section("genai.configure()", True)
except Exception:
    section("genai.configure()", False, traceback.format_exc())
    sys.exit(1)

# ─── STEP 4: GenerativeModel() ──────────────────────────────────────────────
MODEL_NAME = "gemini-2.0-flash"
print(f"\n>>> STEP 4: genai.GenerativeModel('{MODEL_NAME}')")
try:
    model = genai.GenerativeModel(MODEL_NAME)
    section("GenerativeModel instantiated", True, str(model))
except Exception:
    section("GenerativeModel instantiated", False, traceback.format_exc())
    sys.exit(1)

# ─── STEP 5: Build minimal prompt ───────────────────────────────────────────
print("\n>>> STEP 5: Building test prompt")
PROMPT = (
    "You are the ACKO Insurance Policy Bot. Answer ONLY using the context below.\n\n"
    "CONTEXT:\nTo file a claim, submit a completed form, original bills, "
    "discharge summary, and policy copy.\n\n"
    "Question: What documents do I need to file a medical claim?\nAnswer:"
)
section("Prompt built", True,
        f"model={MODEL_NAME}  key_present=True  prompt_len={len(PROMPT)}")
print(f"\n--- Prompt preview ---\n{PROMPT[:300]}\n---")

# ─── STEP 6: generate_content() — RAW, no retry, no fallback ────────────────
print(f"\n>>> STEP 6: model.generate_content(prompt)  [raw — raise on error]")
try:
    response = model.generate_content(PROMPT)
    section("generate_content() SUCCEEDED", True, response.text[:300])
    print(f"\nFull response text:\n{response.text}")

except Exception as exc:
    exc_class   = type(exc).__name__
    exc_module  = type(exc).__module__
    exc_message = str(exc)

    print(f"\n{SEP}")
    print("  EXCEPTION from generate_content()")
    print(f"  Class  : {exc_module}.{exc_class}")
    print(f"  Message: {exc_message}")
    print(f"{SEP}")
    print("\n--- FULL TRACEBACK ---")
    traceback.print_exc()
    print("--- END TRACEBACK ---\n")

    # Classification
    msg = exc_message.lower()
    fqn = (exc_module + "." + exc_class).lower()
    print("--- ROOT CAUSE CLASSIFICATION ---")
    if "resourceexhausted" in fqn or "429" in exc_message or "quota" in msg:
        print("  RESULT: HTTP 429 ResourceExhausted — quota exceeded or daily limit reached")
        print("  FIX   : Wait for reset, enable billing, or use a different/new API key")
    elif "unauthenticated" in fqn or "401" in exc_message or "api_key_invalid" in msg:
        print("  RESULT: HTTP 401 Unauthenticated — API key is invalid or revoked")
    elif "403" in exc_message or "permission" in msg or "forbidden" in msg:
        print("  RESULT: HTTP 403 Forbidden — API key lacks permission for this model")
    elif "notfound" in fqn or "404" in exc_message or "not found" in msg or "no longer available" in msg:
        print("  RESULT: HTTP 404 Not Found — model name unavailable for this project/key")
    elif "500" in exc_message or "internal" in msg:
        print("  RESULT: HTTP 500 Internal Server Error (transient, retry later)")
    elif "ssl" in msg or "certificate" in msg:
        print("  RESULT: SSL/TLS error — certificate problem")
    elif "timeout" in msg or "deadline" in msg:
        print("  RESULT: Timeout / DeadlineExceeded")
    elif "getaddrinfo" in msg or "nodename" in msg or "name or service not known" in msg:
        print("  RESULT: DNS failure — no internet or proxy blocking the endpoint")
    else:
        print(f"  RESULT: UNCLASSIFIED — {exc_module}.{exc_class}: {exc_message[:200]}")
    print("--- END CLASSIFICATION ---\n")

# ─── STEP 7: TCP connectivity ────────────────────────────────────────────────
print("\n>>> STEP 7: TCP connect to generativelanguage.googleapis.com:443")
try:
    sock = socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=6)
    sock.close()
    section("TCP connectivity", True, "generativelanguage.googleapis.com:443 is REACHABLE")
except Exception as conn_err:
    section("TCP connectivity", False, f"{type(conn_err).__name__}: {conn_err}")

print("\n\n>>> DIAGNOSTIC COMPLETE\n")
