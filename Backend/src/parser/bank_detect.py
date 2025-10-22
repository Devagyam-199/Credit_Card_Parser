import re

def bank_detect(text):
    patterns = {
        "axis": re.compile(r"(Axis Bank|AXIS BANK|Neo Credit Card|MyZone Credit Card|Flipkart Axis Bank Credit Card)", re.IGNORECASE),
        "icici": re.compile(r"(ICICI Bank|ICICI Bank Credit Card Statement)", re.IGNORECASE),
        "hdfc": re.compile(r"(HDFC Bank|HDFC Bank Credit Card Statement)", re.IGNORECASE),
        # ✅ IDFC FIRST BANK (replaces Kotak)
        "idfc": re.compile(r"(IDFC\s*FIRST\s*Bank|IDFC FIRST Bank Credit Card Statement|IDFC Bank)", re.IGNORECASE),
    }

    max_confidence = 0
    detected_bank = None

    for bank, pattern in patterns.items():
        matches = len(pattern.findall(text))
        confidence = matches * 10  # Simple scoring logic
        if confidence > max_confidence:
            max_confidence = confidence
            detected_bank = bank

    return (detected_bank, max_confidence)
