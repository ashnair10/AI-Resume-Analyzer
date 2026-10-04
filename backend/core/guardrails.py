import re
from dataclasses import dataclass

EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)")


@dataclass
class GuardrailResult:
    pii_detected: bool
    pii_types: list[str]
    prompt_injection_signals: list[str]


def inspect_input(text: str) -> GuardrailResult:
    pii_types: list[str] = []
    if EMAIL.search(text):
        pii_types.append("email")
    if PHONE.search(text):
        pii_types.append("phone")

    lower = text.lower()
    injection_phrases = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "developer message",
        "reveal your prompt",
    ]
    prompt_injection_signals = [phrase for phrase in injection_phrases if phrase in lower]
    return GuardrailResult(bool(pii_types), pii_types, prompt_injection_signals)
