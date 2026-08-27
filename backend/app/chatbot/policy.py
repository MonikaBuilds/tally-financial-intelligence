import re


READ_ONLY_MESSAGE = (
    "This assistant has read-only access to Tally. "
    "I can retrieve and explain financial information, "
    "but I cannot create, modify, update, or delete "
    "accounting records."
)


WRITE_PATTERNS = (
    r"\bdelete\b",
    r"\bremove\b",
    r"\bupdate\b",
    r"\bmodify\b",
    r"\bedit\b",
    r"\bchange\b",
    r"\balter\b",
    r"\bcreate\b",
    r"\binsert\b",
    r"\badd\s+(?:a\s+)?(?:voucher|invoice|ledger|payment)\b",
    r"\bpost\s+(?:a\s+)?payment\b",
    r"\bcancel\s+(?:a\s+)?(?:invoice|voucher)\b",
)


def is_write_request(message: str) -> bool:
    normalized_message = message.strip().lower()

    return any(
        re.search(
            pattern,
            normalized_message,
            flags=re.IGNORECASE
        )
        for pattern in WRITE_PATTERNS
    )