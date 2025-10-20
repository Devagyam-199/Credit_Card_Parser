import re

# --- Helpers ----------------------------------------------------------------
def lines_of(text):
    return [ln.rstrip() for ln in text.splitlines()]

def first_n_lines(text, n=60):
    return "\n".join(lines_of(text)[:n])

def find_nearby_amounts(text_block, max_amounts=5):
    # Find monetary values like 1,289.00 or 1289.00 or 1,289
    amt_re = re.compile(r"([\d]{1,3}(?:[,]\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)\s*(Dr|Cr)?", re.IGNORECASE)
    res = []
    for m in amt_re.finditer(text_block):
        val = m.group(1)
        drcr = m.group(2) or ""
        # normalize to have two decimals if present, else keep as-is
        res.append((val, drcr.strip()))
        if len(res) >= max_amounts:
            break
    return res

def normalize_money(s):
    if not s or s == "N/A":
        return "0.00"
    s2 = s.replace(",", "")
    # ensure two decimal places if missing
    if re.match(r"^\d+$", s2):
        return f"{s2}.00"
    if re.match(r"^\d+\.\d{1}$", s2):
        return f"{s2}0"
    return s2

# --- Main parser ------------------------------------------------------------
def parse(text):
    """
    Line-aware, context-first parser for credit card statements.
    Returns a dict with main fields and transactions.
    """
    result = {}
    raw_lines = lines_of(text)
    top_block = first_n_lines(text, n=80)

    # ------------------ 1) Cardholder name (heuristic) -----------------------
    # Prefer: first short ALL-CAPS line near top that's not known header/address.
    name = "N/A"
    skip_keywords = {
        "PAYMENT", "STATEMENT", "PAGE", "FLIPKART", "CONTACT", "CUSTOMER", "CREDIT", 
        "ACCOUNT", "CARD", "LIMIT", "SUMMARY", "STATEMENT", "PAGE", "GST", "IMPORTANT"
    }
    for idx, ln in enumerate(raw_lines[:80]):
        s = ln.strip()
        if not s: 
            continue
        # is uppercase and not too long
        if s == s.upper() and 3 <= len(s) <= 40 and not any(k in s for k in skip_keywords):
            # reject if it contains digits/pincode or only direction words
            if re.search(r"\d", s):
                continue
            # also avoid lines with city/state only (heuristic: multiple words with short words like NR, NR., RD)
            # Accept if contains at least one "name-like" token (not NR, B-002, ROAD, APT)
            bad_tokens = {"NR", "ND", "RD", "ROAD", "STREET", "APT", "FLAT", "PIN", "PINCODE", "B-", "NO.", "NO", "BLDG"}
            tokens = set(re.sub(r"[^\w ]", " ", s).split())
            if tokens & bad_tokens:
                continue
            name = s
            break
    result["cardholder_name"] = name

    # ------------------ 2) Card number --------------------------------------
    card_no = "N/A"
    # tolerant patterns, allow extra spaces, missing colon
    card_patterns = [
        r"Card\s*(?:No\.?|Number)\s*[:\-]?\s*([0-9\*]{4,20})",
        r"Card\s*No[:\-]?\s*([0-9\*]{4,20})",
        r"(\d{4,6}\*{2,}\d{4})",
        r"(\d{4}\*{4}\d{4})",
    ]
    for pat in card_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            card_no = m.group(1).strip()
            break
    result["card_number"] = card_no

    # ------------------ 3) Statement period & dates -------------------------
    # Typical axis style: "16/04/2021 - 15/05/2021 04/06/2021 15/05/2021" (period start-end then payment due then statement date)
    period_re = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s*[-to]+\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text)
    if period_re:
        result["statement_period_start"] = period_re.group(1)
        result["statement_period_end"] = period_re.group(2)
    else:
        result["statement_period_start"] = result["statement_period_end"] = "N/A"

    # Statement / payment due date by looking for four dates in a nearby chunk
    # fallback: search for known labels too
    # search for line containing multiple dates
    date_line = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}).{0,80}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}).{0,80}(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", top_block)
    if date_line:
        # assign heuristically: start,end,payment_due or statement date
        # if we already have start/end, prefer next matches for payment/statement date
        if result["statement_period_start"] == "N/A":
            result["statement_period_start"] = date_line.group(1)
            result["statement_period_end"] = date_line.group(2)
            result["payment_due_date"] = date_line.group(3)
        else:
            # we have start/end; take the next two as payment/statement
            result["payment_due_date"] = date_line.group(3)
            # try to find a fourth date for statement_date
            fourth = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text[date_line.end():])
            result["statement_date"] = fourth.group(1) if fourth else "N/A"
    else:
        # label-based fallback
        sd = re.search(r"(?:Statement(?: Generation| Generated)? Date|Statement Date|Generated on)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, re.IGNORECASE)
        pd = re.search(r"(?:Payment\s*Due\s*Date|Due\s*Date|Payment Due)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, re.IGNORECASE)
        if sd: result["statement_date"] = sd.group(1)
        else: result["statement_date"] = "N/A"
        if pd: result["payment_due_date"] = pd.group(1)
        else: result["payment_due_date"] = "N/A"

    # ------------------ 4) Amounts: use payment summary block first -----------
    total_amount = "0.00"
    min_amount = "0.00"
    credit_limit = "0.00"

    # 1) Look for PAYMENT SUMMARY block
    ps_idx = re.search(r"PAYMENT\s*SUMMARY|Payment\s*Summary", text, re.IGNORECASE)
    if ps_idx:
        # take a reasonable slice after that label (200 chars)
        slice_start = ps_idx.start()
        block = text[slice_start:slice_start + 400]
        found = find_nearby_amounts(block, max_amounts=6)
        # heuristics: first amount -> total due, second -> minimum due
        if found:
            total_amount = normalize_money(found[0][0])
            if len(found) >= 2:
                min_amount = normalize_money(found[1][0])
    # 2) If not found or values still placeholders, fallback to label-search
    if (not total_amount) or total_amount == "0.00":
        m = re.search(r"(?:Total\s*(?:Payment|Amount)\s*Due|Total\s*Due|Amount\s*Payable)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
        if m:
            total_amount = normalize_money(m.group(1))

    if (not min_amount) or min_amount == "0.00":
        m = re.search(r"(?:Minimum\s*(?:Payment|Amount)\s*Due)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
        if m:
            min_amount = normalize_money(m.group(1))

    # 3) Credit limit: search for "Credit Limit" near top_block then fallback
    cl = None
    cl_m = re.search(r"(?:Credit\s*Limit|Total\s*Limit|Available\s*Limit)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", top_block, re.IGNORECASE)
    if cl_m:
        cl = normalize_money(cl_m.group(1))
    else:
        cl_m = re.search(r"(?:Credit\s*Limit|Total\s*Limit|Available\s*Limit)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
        if cl_m:
            cl = normalize_money(cl_m.group(1))
    if cl:
        credit_limit = cl

    result["total_amount_due"] = total_amount
    result["minimum_amount_due"] = min_amount
    result["credit_limit"] = credit_limit

    # ------------------ 5) Transactions -------------------------------------
    # robust TG: date then description then amount + Dr/Cr — allow multiple spaces and long description
    trans_pattern = re.compile(
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+([A-Za-z0-9 ,.&'\/\-:()]{5,100}?)\s+([\d,]+(?:\.\d{2})?)\s*(Dr|Cr)",
        re.IGNORECASE
    )
    transactions = []
    for m in trans_pattern.finditer(text):
        transactions.append({
            "date": m.group(1),
            "description": m.group(2).strip(),
            "amount": f"{normalize_money(m.group(3))} {m.group(4)}"
        })

    result["transactions"] = transactions[:200]

    return result
