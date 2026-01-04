# safety.py

def is_safe_for_any_user(text: str) -> bool:
    """
    Basic safety filter to block clearly dangerous or emergency queries.
    Applies to both public and clinician modes.
    """
    banned_keywords = [
        "suicide", "kill myself", "kill someone", "overdose",
        "self harm", "self-harm", "hurt myself", "hurt someone"
    ]
    t = text.lower()
    return not any(word in t for word in banned_keywords)


def is_safe_for_public(text: str) -> bool:
    """
    Additional restrictions for general public mode.
    We block direct diagnosis / medication / emergency-style queries.
    """
    banned_keywords = [
        "diagnose", "diagnosis", "what disease", "do i have",
        "should i take", "dose", "dosage", "prescribe", "prescription",
        "emergency", "chest pain", "heart attack", "stroke"
    ]
    t = text.lower()
    return is_safe_for_any_user(t) and not any(word in t for word in banned_keywords)


def is_safe_for_clinician(text: str) -> bool:
    """
    For clinician mode we are still cautious, but allow more clinical language.
    We still block obviously harmful/emergency self-harm content.
    """
    return is_safe_for_any_user(text)
