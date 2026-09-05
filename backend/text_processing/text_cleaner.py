import re


def clean_text(text, remove_artifacts=True):
    """
    Conservatively clean raw extracted text before chunking.

    This function is intentionally cautious: it normalizes whitespace
    and removes obvious extraction artifacts, but does NOT rewrite,
    reflow, or reword content. Headings, lists, equations, and code
    should survive this step unchanged (aside from whitespace).

    Args:
        text (str): Raw text extracted from a PDF/DOCX/etc.
        remove_artifacts (bool): Whether to strip repeated-symbol
            artifacts (e.g. "------", "......") that are typically
            page-break/divider noise, not real content.

    Returns:
        str: Cleaned text.
    """

    if not isinstance(text, str):
        raise ValueError("text must be a string.")

    if not text.strip():
        return ""

    cleaned = text

    # --- Step 1: Normalize whitespace (always safe) ---
    # Replace tabs and multiple spaces with a single space.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Collapse 3+ consecutive blank lines into just 2
    # (keeps paragraph separation, removes excessive gaps).
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Remove trailing whitespace at the end of each line.
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)

    # --- Step 2: Optional artifact removal ---
    if remove_artifacts:
        # Lines made up entirely of repeated symbols (dividers/noise),
        # e.g. "------", "......", "______"
        # Only matches a WHOLE line of 4+ repeated symbol characters,
        # so it won't touch things like "y = x----1" or code operators.
        cleaned = re.sub(r"^[\-_.=~*#]{4,}$", "", cleaned, flags=re.MULTILINE)

    # --- Step 3: Trim leading/trailing whitespace of the whole text ---
    cleaned = cleaned.strip()

    return cleaned