import re

# ---------------- Helper functions ----------------
def lines_of(text):
    return [ln.rstrip() for ln in text.splitlines()]

def first_n_lines(text, n=80):
    return "\n".join(lines_of(text)[:n])

def find_nearby_amounts(text_block, max_amounts=5):
    amt_re = re.compile(r"([\d]{1,3}(?:[,]\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)\s*(Dr|Cr)?", re.IGNORECASE)
    res = []
    for m in amt_re.finditer(text_block):
        val = m.group(1)
        drcr = m.group(2) or ""
        res.append((val, drcr.strip()))
        if len(res) >= max_amounts:
            break
    return res

def normalize_money(s):
    if not s or s == "N/A":
        return "0.00"
    s2 = s.replace(",", "")
    if re.match(r"^\d+$", s2):
        return f"{s2}.00"
    if re.match(r"^\d+\.\d{1}$", s2):
        return f"{s2}0"
    return s2


# ---------------- Main Axis Bank parser ----------------
def parse(text):
    result = {}
    raw_lines = lines_of(text)
    top_block = first_n_lines(text, 100)

    # ------------------ 1) Cardholder name ------------------
    name = "N/A"
    skip_keywords = {
        "PAYMENT", "STATEMENT", "PAGE", "FLIPKART", "CUSTOMER", "CREDIT", 
        "ACCOUNT", "CARD", "LIMIT", "SUMMARY", "IMPORTANT", "BILLING"
    }
    for idx, ln in enumerate(raw_lines[:80]):
        s = ln.strip()
        if not s:
            continue
        if s == s.upper() and 3 <= len(s) <= 40 and not any(k in s for k in skip_keywords):
            if re.search(r"\d", s):
                continue
            tokens = set(re.sub(r"[^\w ]", " ", s).split())
            if tokens & {"NR", "RD", "ROAD", "BLDG", "PIN"}:
                continue
            name = s
            break
    result["cardholder_name"] = name

    # ------------------ 2) Card number ------------------
    card_no = "N/A"
    card_patterns = [
        r"Card\s*(?:No\.?|Number)\s*[:\-]?\s*([0-9\*]{4,20})",
        r"(\d{4,6}\*{2,}\d{4})",
        r"(\d{4}\*{4}\d{4})",
    ]
    for pat in card_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            card_no = m.group(1).strip()
            break
    result["card_number"] = card_no

    # ------------------ 3) Dates (period + due + statement) ------------------
    # Try to capture all 4 dates from top section — pattern found in Axis PDFs:
    # Example: "16/04/2021 - 15/05/2021 04/06/2021 15/05/2021"
    dates_found = re.findall(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", top_block)
    result["statement_period_start"] = "N/A"
    result["statement_period_end"] = "N/A"
    result["payment_due_date"] = "N/A"
    result["statement_date"] = "N/A"

    if len(dates_found) >= 2:
        result["statement_period_start"] = dates_found[0]
        result["statement_period_end"] = dates_found[1]
    if len(dates_found) >= 3:
        result["payment_due_date"] = dates_found[2]
    if len(dates_found) >= 4:
        result["statement_date"] = dates_found[3]

    # Fallbacks using labeled text
    if result["payment_due_date"] == "N/A":
        m = re.search(r"Payment\s*Due\s*Date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", text, re.IGNORECASE)
        if m:
            result["payment_due_date"] = m.group(1)

    if result["statement_date"] == "N/A":
        m = re.search(r"Statement\s*Date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})", text, re.IGNORECASE)
        if m:
            result["statement_date"] = m.group(1)

    # ------------------ 4) Amounts (summary) ------------------
    total_amount = "0.00"
    min_amount = "0.00"
    credit_limit = "0.00"

    ps_idx = re.search(r"PAYMENT\s*SUMMARY|BILL\s*SUMMARY|STATEMENT\s*SUMMARY", text, re.IGNORECASE)
    if ps_idx:
        block = text[ps_idx.start(): ps_idx.start() + 600]
        found = find_nearby_amounts(block, max_amounts=6)
        if found:
            total_amount = normalize_money(found[0][0])
            if len(found) >= 2:
                min_amount = normalize_money(found[1][0])

    if total_amount == "0.00":
        m = re.search(r"(?:Total\s*(?:Payment|Amount)\s*Due)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", text)
        if m:
            total_amount = normalize_money(m.group(1))

    if min_amount == "0.00":
        m = re.search(r"(?:Minimum\s*(?:Payment|Amount)\s*Due)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", text)
        if m:
            min_amount = normalize_money(m.group(1))

    cl_m = re.search(r"(?:Credit\s*Limit|Total\s*Limit|Available\s*Limit)\s*[:\-]?\s*([\d,]+(?:\.\d{2})?)", text)
    if cl_m:
        credit_limit = normalize_money(cl_m.group(1))

    result["total_amount_due"] = total_amount
    result["minimum_amount_due"] = min_amount
    result["credit_limit"] = credit_limit

    # ------------------ 5) Transactions ------------------
    trans_pattern = re.compile(
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})\s+([A-Za-z0-9 ,.&'\/\-:()]{5,120}?)\s+([\d,]+(?:\.\d{2})?)\s*(Dr|Cr)",
        re.IGNORECASE
    )
    transactions = []
    for m in trans_pattern.finditer(text):
        transactions.append({
            "date": m.group(1),
            "description": m.group(2).strip(),
            "amount": f"{normalize_money(m.group(3))} {m.group(4).capitalize()}"
        })

    result["transactions"] = transactions[:300]
    return result
