import re
from datetime import datetime

def parse(text):
    """
    Truly Universal Credit Card Statement Parser (improved).
    Uses multiple strategies and picks the best result for each field.
    """
    result = {}
    lines = [ln.rstrip() for ln in text.splitlines()]

    # 1. CARDHOLDER NAME
    result["cardholder_name"] = extract_name(text, lines)

    # 2. CARD NUMBER
    result["card_number"] = extract_card_number(text)

    # 3. STATEMENT DATE
    result["statement_date"] = extract_statement_date(text)

    # 4. PAYMENT DUE DATE
    result["payment_due_date"] = extract_due_date(text)

    # 5. TOTAL AMOUNT DUE
    result["total_amount_due"] = extract_total_due(text)

    # 6. MINIMUM AMOUNT DUE
    result["minimum_amount_due"] = extract_minimum_due(text)

    # 7. CREDIT LIMIT
    result["credit_limit"] = extract_credit_limit(text)

    # 8. TRANSACTIONS
    result["transactions"] = extract_transactions(text)[:50]

    return result


# ----------------------------- Utilities -------------------------------------

def normalize_money(s):
    """Normalize monetary values to 'x.xx' string. Accepts commas."""
    if not s:
        return "0.00"
    s2 = str(s).replace(",", "").strip()
    # remove trailing non-digits (like Dr/Cr if accidently passed)
    s2 = re.sub(r"[^\d\.]", "", s2)
    if s2 == "":
        return "0.00"
    if "." not in s2:
        return f"{s2}.00"
    # pad decimal to 2
    parts = s2.split(".")
    if len(parts[1]) == 1:
        parts[1] = parts[1] + "0"
    elif len(parts[1]) == 0:
        parts[1] = "00"
    return f"{parts[0]}.{parts[1][:2]}"


def normalize_date(date_str):
    """Return date in DD/MM/YYYY when recognizable, else return original trimmed."""
    if not date_str:
        return "N/A"
    s = date_str.strip()
    # dd/mm/yyyy or d/m/yyyy
    m = re.match(r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', s)
    if m:
        dd, mm, yy = m.groups()
        return f"{int(dd):02d}/{int(mm):02d}/{yy}"
    # dd-Mon-YYYY
    m = re.match(r'(\d{1,2})-([A-Za-z]{3})-(\d{4})', s)
    if m:
        try:
            dt = datetime.strptime(s, "%d-%b-%Y")
            return dt.strftime("%d/%m/%Y")
        except:
            return s
    # Month DD, YYYY
    try:
        dt = datetime.strptime(s, "%B %d, %Y")
        return dt.strftime("%d/%m/%Y")
    except:
        pass
    return s


def find_amounts_with_drcr(block):
    """
    Returns list of tuples (amount_str, drcr) found in text block in order.
    Accepts amounts with commas and optional decimals, optionally followed/preceded by Dr/Cr.
    """
    pat = re.compile(r"([\d]{1,3}(?:[,]\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)\s*(?:([Dd]r|[Cc]r))?")
    res = []
    for m in pat.finditer(block):
        amt = m.group(1)
        drcr = m.group(2) or ""
        res.append((amt, drcr.upper()))
    return res


# ------------------------- NAME EXTRACTION -----------------------------------

def extract_name(text, lines):
    """
    Heuristics:
    1) Try label-based 'Name' first.
    2) Else scan top ~80 lines for an uppercase name line that:
       - Is not a header / bank word
       - Is followed by an address-like line (makes it likely the name above address)
       - Has 2-4 tokens that look like name tokens (len 2..20)
    """
    # Label-based attempts (common)
    label_patterns = [
        r"(?:Cardholder|Card Holder|Card Holder Name|Name|Account Name)\s*[:\-]\s*([A-Z][A-Z\s]{3,80}?)\b",
    ]
    for pat in label_patterns:
        m = re.search(pat, text[:2000], re.IGNORECASE | re.MULTILINE)
        if m:
            candidate = m.group(1).strip()
            if is_valid_name(candidate):
                return candidate

    # Fallback: scan lines near top
    skip_tokens = {
        "PAYMENT", "STATEMENT", "PAGE", "CONTACT", "CUSTOMER", "CREDIT",
        "ACCOUNT", "CARD", "LIMIT", "SUMMARY", "GST", "IMPORTANT", "BANK",
        "DUPLICATE", "GENERATION", "DATE", "PERIOD", "FLIPKART", "AXIS",
        "HDFC", "ICICI", "KOTAK", "WELCOME", "DEAR", "MR", "MS", "MRS", "NAME"
    }

    address_tokens = {"NR", "NEAR", "RD", "ROAD", "STREET", "APT", "FLAT", "PIN", "PINCODE", "B-", "NO", "BLDG", "VILL", "DIST", "TEHSIL"}

    candidates = []
    top_n = min(len(lines), 120)
    for idx in range(top_n):
        s = lines[idx].strip()
        if not s:
            continue
        s_up = s.upper()
        # strong candidate: all caps, length, not contain digits-heavy
        if s_up == s and 5 <= len(s) <= 60:
            # skip lines that include skip tokens
            if any(re.search(r'\b' + re.escape(tok) + r'\b', s_up) for tok in skip_tokens):
                continue
            # skip lines with many digits (likely pin or acc)
            if len(re.findall(r'\d', s_up)) > 3:
                continue

            # check next line — if next line has address tokens, then current is likely name
            next_line = lines[idx + 1].strip().upper() if idx + 1 < len(lines) else ""
            has_address_next = any(re.search(r'\b' + re.escape(tok) + r'\b', next_line) for tok in address_tokens)
            # ensure tokens of the candidate look like personal name tokens
            tokens = [t for t in re.sub(r'[^\w ]', ' ', s_up).split() if t]
            name_like_tokens = [t for t in tokens if 2 <= len(t) <= 18 and not re.search(r'\d', t)]
            if len(name_like_tokens) >= 2:
                score = 90
                if has_address_next:
                    score += 10
                # extra boost if contains one token with typical initial pattern (e.g., K, K.)
                if any(len(t) == 1 for t in tokens):
                    score += 5
                candidates.append((s.strip(), score))
                # if strong (address next), early accept
                if has_address_next:
                    break

    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    return "N/A"


def is_valid_name(name):
    if not name or len(name) < 5:
        return False
    if len(name.split()) < 2:
        return False
    # disallow if mostly digits / contains typical address tokens
    if re.search(r'\d{4,}', name):
        return False
    if re.search(r'\b(PIN|ROAD|STREET|FLAT|NO|B-|APT)\b', name.upper()):
        return False
    return True


# ------------------------- CARD NUMBER -------------------------------------

def extract_card_number(text):
    """
    Tolerant card number detection for masked formats:
    Examples matched:
      53346700****1060
      5334 6700 **** 1060
      5334****1060
      5334XXXXXXXX1060
    """
    patterns = [
        r"(?:Card\s*(?:No\.?|Number)\s*[:\-]?\s*)([0-9]{4,8}[\s\*Xx]{2,12}[0-9]{4})",
        r"([0-9]{4,8}\*{2,12}[0-9]{4})",
        r"([0-9]{4}(?:[\sXx\*]{2,12})[0-9]{4})",
        r"(\d{4}\s+\d{4}\s+\*+\s+\d{4})"
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            # basic sanity: must contain stars or X or spaces masking
            if re.search(r'[\*Xx]', cand) or (' ' in cand and len(cand.replace(' ', '')) >= 12):
                # normalize spaces
                return re.sub(r'\s+', ' ', cand)
    # final fallback: any masked chunk of length >=12 with stars
    m = re.search(r"([0-9]{4,8}\*{4,10}[0-9]{4})", text)
    if m:
        return m.group(1).strip()
    return "N/A"


# ------------------------- DATES -------------------------------------------

def extract_statement_date(text):
    patterns = [
        r"Statement\s+(?:Generation\s+)?Date\s*[:\-]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
        r"Statement\s+Date\s*[:\-]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
        r"Generated\s+(?:on|date)\s*[:\-]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
        r"Statement\s+for\s+period.*?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
    ]
    for p in patterns:
        m = re.search(p, text[:4000], re.IGNORECASE | re.DOTALL)
        if m:
            return normalize_date(m.group(1))
    # fallback: try to pick a date after the statement period if present
    period = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})\s*[-to]+\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", text)
    if period:
        # often statement date appears nearby; search window after period
        after = text[period.end(): period.end() + 200]
        m = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", after)
        if m:
            return normalize_date(m.group(1))
    return "N/A"


def extract_due_date(text):
    # Try label-based first
    patterns = [
        r"Payment\s*Due\s*Date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
        r"Due\s*Date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})",
    ]
    for p in patterns:
        m = re.search(p, text[:5000], re.IGNORECASE)
        if m:
            return normalize_date(m.group(1))

    # Try PAYMENT SUMMARY block: there are usually multiple dates/nums; pick the date-like token
    m = re.search(r"(PAYMENT\s+SUMMARY|Payment\s+Summary)", text, re.IGNORECASE)
    if m:
        block = text[m.start(): m.start() + 500]
        dm = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", block)
        if dm:
            return normalize_date(dm.group(1))
    return "N/A"


# ------------------------- AMOUNTS -----------------------------------------

def extract_total_due(text):
    """
    Priority:
      1. Look in PAYMENT SUMMARY slice for amounts with Dr/Cr and map first positive (or Dr) to total due.
      2. Label-based search 'Total Payment Due' etc.
      3. Table fallback scanning near 'Previous Balance - Payments - Credits + Purchase ... = Total Payment Due' pattern.
    """
    # 1) PAYMENT SUMMARY block
    m = re.search(r"(PAYMENT\s+SUMMARY|Payment\s+Summary)", text, re.IGNORECASE)
    if m:
        block = text[m.start(): m.start() + 800]
        amts = find_amounts_with_drcr(block)
        # heuristics: we expect a few numbers; Axis has "1,289.00   Dr 100.00   Dr" — first is total, second minimum
        if amts:
            # Prefer amounts that have a Dr suffix (amount due likely marked Dr in your sample)
            # choose first amount that's > 0
            for amt, drcr in amts:
                val = float(amt.replace(",", "")) if amt.replace(",", "").replace(".", "").isdigit() else 0.0
                if val > 0:
                    return normalize_money(amt)
    # 2) Label-based
    patterns = [
        r"Total\s+Payment\s+Due\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)",
        r"Total\s+Amount\s+Due\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)",
        r"Amount\s+Payable\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)",
        r"Total\s+Outstanding\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)",
    ]
    for p in patterns:
        mm = re.search(p, text, re.IGNORECASE)
        if mm:
            return normalize_money(mm.group(1))
    # 3) Table-like fallback
    m = re.search(r"Previous\s+Balance.*?=\s*Total\s*Payment\s*Due\s*([\d,]+(?:\.\d{1,2})?)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return normalize_money(m.group(1))
    return "0.00"


def extract_minimum_due(text):
    # 1) PAYMENT SUMMARY block - second amount often minimum due
    m = re.search(r"(PAYMENT\s+SUMMARY|Payment\s+Summary)", text, re.IGNORECASE)
    if m:
        block = text[m.start(): m.start() + 800]
        amts = find_amounts_with_drcr(block)
        if len(amts) >= 2:
            return normalize_money(amts[1][0])

    # 2) label-based
    patterns = [
        r"Minimum\s+Payment\s+Due\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)",
        r"Minimum\s+Amount\s+Due\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)",
    ]
    for p in patterns:
        mm = re.search(p, text, re.IGNORECASE)
        if mm:
            return normalize_money(mm.group(1))
    return "0.00"


def extract_credit_limit(text):
    # Try to find "Credit Limit" near top; Axis has "Credit  Card Number ... 115,000.00 113,711.00 34,500.00"
    top = text[:2500]
    m = re.search(r"(?:Credit\s*Limit|Available\s*Credit|Total\s*Limit)\s*[:\-]?\s*([\d,]+(?:\.\d{1,2})?)", top, re.IGNORECASE)
    if m:
        return normalize_money(m.group(1))
    # fallback: search anywhere for a large numeric that looks like a limit (heuristic)
    all_nums = re.findall(r"([\d]{1,3}(?:[,]\d{3})+(?:\.\d{1,2})?)", text[:4000])
    # choose the largest found (most likely limit)
    if all_nums:
        cleaned = [(n, float(n.replace(",", ""))) for n in all_nums if n.replace(",", "").replace(".", "").isdigit()]
        if cleaned:
            cleaned.sort(key=lambda x: x[1], reverse=True)
            top_val = cleaned[0][0]
            # sanity check range
            v = cleaned[0][1]
            if 1000 <= v <= 50000000:
                return normalize_money(top_val)
    return "0.00"


# ---------------------- TRANSACTIONS ----------------------------------------

def extract_transactions(text):
    """
    Extract transactions from the statement. Uses several patterns; returns list of dicts.
    """
    transactions = []

    # find a transaction-like section
    trans_marker = re.search(r"(?:TRANSACTION\s+DETAILS|Transaction\s+Details|DATE\s+TRANSACTION|Date\s+Description\s+Amount|Account\s+Summary|Account\s+Transactions|Account\s+Summary)", text, re.IGNORECASE)
    if trans_marker:
        start = trans_marker.start()
        section = text[start:start + 8000]
    else:
        # fallback: entire text
        section = text

    # Patterns: date, description, amount (Dr/Cr optional)
    patterns = [
        re.compile(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+([A-Za-z][A-Za-z0-9\s&'.,\-/()]{3,120}?)\s+([\d,]+(?:\.\d{1,2})?)\s*(?:([Dd]r|[Cc]r))?", re.MULTILINE),
        re.compile(r"(\d{2}\/\d{2}\/\d{4})\s+([A-Z][A-Z0-9\s&'.,\-/()]{3,120}?)\s+([\d,]+(?:\.\d{1,2})?)\s*(?:([Dd]r|[Cc]r))?", re.MULTILINE),
    ]

    for pat in patterns:
        for m in pat.finditer(section):
            dt = normalize_date(m.group(1))
            desc = ' '.join(m.group(2).split())
            amt = normalize_money(m.group(3))
            drcr = (m.group(4) or "").upper()
            if drcr:
                amt = f"{amt} {drcr}"
            else:
                # optionally infer Dr/Cr from nearby text (not implemented here)
                pass

            # filters to avoid catching headers or name lines
            if len(desc) < 3:
                continue
            if re.match(r'^[\d\s,\.]+$', desc):
                continue
            if desc.upper().startswith(("DATE", "TRANSACTION", "BALANCE", "OPENING", "CLOSING")):
                continue
            # avoid picking very long all-caps lines that are likely headlines
            if re.match(r'^[A-Z\s]{30,}$', desc):
                continue

            transactions.append({
                "date": dt,
                "description": desc,
                "amount": amt
            })
            if len(transactions) >= 200:
                break
        if transactions:
            break

    # final fallback: try the simpler line-by-line parse if nothing found
    if not transactions:
        for line in section.splitlines():
            m = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}).*?([\d,]+(?:\.\d{1,2})?)", line)
            if m:
                transactions.append({
                    "date": normalize_date(m.group(1)),
                    "description": line[:60].strip(),
                    "amount": normalize_money(m.group(2))
                })
            if len(transactions) >= 50:
                break

    return transactions


# ---------------------------------------------------------------------------

# Example quick test helper (not executed here):
# if __name__ == "__main__":
#     raw_text = open("extracted_axis_text.txt").read()
#     print(parse(raw_text))
