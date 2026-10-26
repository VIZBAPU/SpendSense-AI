import re

PREFIXES = ("SQ *", "TST*", "POS ", "PAYPAL *", "INTERAC PURCHASE ")
PROVINCES = "AB|BC|MB|NB|NL|NS|NT|NU|ON|PE|QC|SK|YT"

STORE_NUMBER = re.compile(r"#\s*\d+")
LONG_NUMBER = re.compile(r"\b\d{3,}\b")
CITY_PROVINCE = re.compile(rf"\s+[A-Z]+\s+(?:{PROVINCES})$")
SPACES = re.compile(r"\s+")


def normalize_merchant(description: str) -> str:
    """Turn a raw bank description into a clean merchant name.

    Example: "SQ *BLUE BOTTLE #1234 TORONTO ON" -> "BLUE BOTTLE"
    """
    text = description.upper().strip()
    for prefix in PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    text = STORE_NUMBER.sub("", text)
    text = LONG_NUMBER.sub("", text)
    text = SPACES.sub(" ", text).strip()
    text = CITY_PROVINCE.sub("", text)
    return text.strip(" -*.,")
