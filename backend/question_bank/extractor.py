import re
from typing import List, Dict, Any, Optional
from backend.question_bank.normalizer import strip_marks_suffix


QUESTION_START_REGEX = re.compile(
    r"^(?:"
    r"(?:Q(?:uestion)?|Que)?\.?\s*(?:\d{1,3}|[A-Za-z])[\.\)\:\-]\s*"
    r"|\((?:\d{1,3}|[a-zA-Z]|[ivxlcdmIVXLCDM]+)\)\s*"
    r"|\[(?:\d{1,3}|[a-zA-Z])\]\s*"
    r")",
    re.IGNORECASE,
)

SECTION_REGEX = re.compile(
    r"^(?:SECTION|PART|MODULE|UNIT)\s*[-:]?\s*([A-Za-z0-9]+)",
    re.IGNORECASE,
)

IGNORE_HEADERS_REGEX = re.compile(
    r"^(?:time\s*allowed|duration|maximum\s*marks|max\s*marks|total\s*marks|"
    r"instructions|note|roll\s*no|semester|examination|paper\s*code|course\s*code|"
    r"department\s*of|university|college|faculty\s*of|subject\s*code)\b",
    re.IGNORECASE,
)


def extract_questions_from_text(
    raw_text: str,
    paper_name: str = "Unknown Paper",
    paper_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Parse exam question paper text into individual questions with numbers, marks, and sections.
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        return []

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    questions = []

    current_section = None
    current_q_num = None
    current_q_lines = []
    current_marks = None

    def flush_question():
        nonlocal current_q_num, current_q_lines, current_marks
        if not current_q_lines:
            return

        full_q_text = " ".join(current_q_lines).strip()
        cleaned_text, marks = strip_marks_suffix(full_q_text)
        assigned_marks = marks or current_marks

        # Filter out short fragments or exam metadata accidentally matched
        if len(cleaned_text.split()) >= 3 and not IGNORE_HEADERS_REGEX.match(cleaned_text):
            questions.append({
                "paper_id": paper_id,
                "paper_name": paper_name,
                "original_number": current_q_num or f"Q{len(questions) + 1}",
                "original_text": full_q_text,
                "cleaned_text": cleaned_text,
                "marks": assigned_marks,
                "section": current_section,
            })

        current_q_num = None
        current_q_lines = []
        current_marks = None

    for line in lines:
        # Check if line is an exam header to skip
        if IGNORE_HEADERS_REGEX.match(line):
            continue

        # Check for Section / Part header
        sec_match = SECTION_REGEX.match(line)
        if sec_match:
            flush_question()
            current_section = f"Section {sec_match.group(1).upper()}"
            continue

        # Check for Question start
        q_match = QUESTION_START_REGEX.match(line)
        if q_match:
            flush_question()
            current_q_num = q_match.group(0).strip()
            # Remainder of the line is the start of the question text
            remainder = line[q_match.end():].strip()
            if remainder:
                current_q_lines.append(remainder)
        else:
            # Check if line ends with a question mark and we are accumulating
            if current_q_lines:
                current_q_lines.append(line)
            else:
                # If question didn't have standard numbering but ends with '?'
                if line.endswith("?") and len(line.split()) >= 4:
                    flush_question()
                    current_q_num = f"Q{len(questions) + 1}"
                    current_q_lines.append(line)
                    flush_question()

    flush_question()
    return questions


def extract_questions_from_pdf_result(
    pdf_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extract questions from the output of backend.resource_processing.pdf_handler.extract_pdf()
    """
    paper_name = pdf_result.get("source_name", "Unknown Paper")
    paper_id = pdf_result.get("resource_id")
    full_text_list = []

    for page in pdf_result.get("pages", []):
        if page.get("has_text") and page.get("text"):
            full_text_list.append(page["text"])

    combined_text = "\n\n".join(full_text_list)
    return extract_questions_from_text(combined_text, paper_name=paper_name, paper_id=paper_id)


def extract_questions_from_docx_result(
    docx_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extract questions from the output of backend.resource_processing.docx_handler.extract_docx()
    """
    paper_name = docx_result.get("source_name", "Unknown Paper")
    paper_id = docx_result.get("resource_id")
    text_parts = []

    for elem in docx_result.get("elements", []):
        if elem.get("has_text") and elem.get("text"):
            text_parts.append(elem["text"])

    combined_text = "\n\n".join(text_parts)
    return extract_questions_from_text(combined_text, paper_name=paper_name, paper_id=paper_id)
