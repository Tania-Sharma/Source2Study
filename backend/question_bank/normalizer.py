import re
import string


def clean_spaces(text: str) -> str:
    """Collapse tabs, newlines, and multiple spaces into a single space."""
    return re.sub(r"\s+", " ", text).strip()


def strip_question_prefixes(text: str) -> str:
    """
    Remove leading question numbers/labels like:
    - "1.", "1)", "1:", "(1)", "[1]"
    - "Q1.", "Q.1:", "Question 1 -", "Que 1."
    - "(a)", "a)", "a.", "i.", "(i)"
    """
    cleaned = text.strip()
    # Remove Section headers if prepended
    cleaned = re.sub(r"^(?:Section|Part)\s+[A-Za-z0-9]+\s*[:-]?\s*", "", cleaned, flags=re.IGNORECASE)
    # Remove question numbers
    pattern = r"^(?:(?:Q(?:uestion)?|Que)?\.?\s*(?:\d+|[a-zA-Z]|\([0-9a-zA-ZivxlcdmIVXLCDM]+\)|[ivxlcdmIVXLCDM]+)[\.\)\:\-]\s*)+"
    cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def strip_marks_suffix(text: str) -> tuple[str, str | None]:
    """
    Extract and strip marks annotations from the end of questions.
    Examples:
        - "What is machine learning? [5 Marks]" -> ("What is machine learning?", "5")
        - "Explain supervised learning (10M)" -> ("Explain supervised learning", "10M")
        - "Define DBMS. (5)" -> ("Define DBMS.", "5")
    """
    marks = None
    pattern = r"[\(\[\{]\s*(\d+\s*(?:marks?|pts?|m)?)\s*[\)\]\}]\s*$"
    match = re.search(pattern, text.strip(), re.IGNORECASE)
    cleaned = text
    if match:
        marks = match.group(1).strip()
        cleaned = text[:match.start()].strip()
    return cleaned, marks


def normalize_for_exact_match(text: str) -> str:
    """
    Normalize question text for robust exact duplicate matching.
    Handles:
    - Leading numbering ("1.", "Q2:")
    - Marks suffixes ("[5 Marks]")
    - Inconsistent capitalization
    - Extra whitespace and linebreaks
    - Minor punctuation differences (question marks, periods, commas, quotes)
    """
    if not isinstance(text, str):
        return ""

    without_prefix = strip_question_prefixes(text)
    without_marks, _ = strip_marks_suffix(without_prefix)

    # Lowercase
    normalized = without_marks.lower()

    # Normalize unicode quotes and dashes
    normalized = (
        normalized.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("—", "-")
        .replace("–", "-")
    )

    # Remove all punctuation
    translator = str.maketrans("", "", string.punctuation)
    normalized = normalized.translate(translator)

    # Collapse whitespace
    normalized = clean_spaces(normalized)
    return normalized


def normalize_for_semantic_match(text: str) -> str:
    """
    Strip common question starter phrases so semantic embeddings or comparison
    focus on the substantive inquiry.
    e.g. "What do you mean by artificial intelligence?" -> "artificial intelligence"
    "Define artificial intelligence." -> "artificial intelligence"
    """
    normalized = normalize_for_exact_match(text)

    # Common prefixes to strip for semantic concept comparison
    prefix_patterns = [
        r"^what\s+(?:is|are|was|were|do\s+you\s+mean\s+by|do\s+you\s+understand\s+by)\s+",
        r"^(?:explain|describe|define|state|discuss|illustrate|elaborate|clarify)\s+(?:the\s+concept\s+of\s+|the\s+term\s+|the\s+)?",
        r"^write\s+(?:a\s+)?(?:short\s+)?notes?\s+(?:on|about)\s+",
        r"^give\s+(?:a\s+)?(?:brief\s+)?(?:overview|account|introduction)\s+(?:of|to)\s+",
        r"^differentiate\s+between\s+",
        r"^distinguish\s+between\s+",
        r"^compare\s+and\s+contrast\s+",
    ]

    for pat in prefix_patterns:
        match = re.search(pat, normalized)
        if match:
            remainder = normalized[match.end():].strip()
            if remainder:
                return remainder

    return normalized


def check_safeguards_allow_merge(q1: str, q2: str) -> tuple[bool, str]:
    """
    Guard against false-positive merges.
    Checks:
    1. Numerical differences: e.g. "3 stages" vs "5 stages"
    2. Polarity / Negation differences: e.g. "is advantageous" vs "is disadvantageous" or "not"
    3. Distinct directional keywords: e.g. "BFS" vs "DFS", "client" vs "server", "TCP" vs "UDP"
    """
    n1 = normalize_for_exact_match(q1)
    n2 = normalize_for_exact_match(q2)

    # Extract all digits in both questions
    digits1 = set(re.findall(r"\b\d+\b", n1))
    digits2 = set(re.findall(r"\b\d+\b", n2))
    if digits1 != digits2:
        return False, f"Different numeric values detected: {digits1} vs {digits2}"

    # Polarity check
    negations = {"not", "no", "never", "without", "disadvantage", "disadvantages", "limitations"}
    words1 = set(n1.split())
    words2 = set(n2.split())
    neg1 = words1 & negations
    neg2 = words2 & negations
    if neg1 != neg2:
        return False, f"Difference in negative/limitation words: {neg1} vs {neg2}"

    return True, "Safe to compare"
