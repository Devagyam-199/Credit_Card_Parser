import re

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
    result = {}
    raw_lines = lines_of(text)
    name = "N/A"
    skip_keywords = {
        "PAYMENT", "STATEMENT", "PAGE", "CONTACT", "CUSTOMER", "CREDIT", 
        "ACCOUNT", "CARD", "LIMIT", "SUMMARY", "STATEMENT", "PAGE", "GST", "IMPORTANT"
    }
    
    # Cardholder Name - Look for "Name : NIKHIL KHANDELWAL" but exclude lines with numbers/emails
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
    
    # Card Number - Your regex works perfectly!
    card_match = re.search(r"Card No\s*:\s*(\d{4}\s+\d{2}XX\s+XXXX\s+\d{4})", text)
    result["card_number"] = card_match.group(1).strip() if card_match else "N/A"
    
    # Statement Date - Works!
    statement_match = re.search(r"Statement Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    result["statement_date"] = statement_match.group(1) if statement_match else "N/A"
    
    # Payment Due Date - Works!
    due_match = re.search(r"Payment Due Date[\s\S]*?(\d{2}/\d{2}/\d{4})", text)
    result["payment_due_date"] = due_match.group(1) if due_match else "N/A"
    
    # Total Amount Due - FIX: Avoid matching "0" by being more specific
    # Look for the actual table row with Payment Due Date and amounts
    total_match = re.search(
        r"Payment Due Date\s+Total Dues\s+Minimum Amount Due.*?\n.*?(\d{1,2}/\d{1,2}/\d{4})\s+([\d,]+\.?\d*)",
        text,
        re.DOTALL
    )
    if total_match and total_match.group(2) != "0":
        result["total_amount_due"] = total_match.group(2)
    else:
        # Fallback: Look in Account Summary section for non-zero value
        total_match2 = re.search(r"Total Dues\s+([\d,]+\.\d{2})", text)
        result["total_amount_due"] = total_match2.group(1) if total_match2 else "0.00"
    
    # Minimum Amount Due - FIX: Similar approach
    min_match = re.search(
        r"Payment Due Date\s+Total Dues\s+Minimum Amount Due.*?\n.*?\d{1,2}/\d{1,2}/\d{4}\s+[\d,]+\.?\d*\s+([\d,]+\.?\d*)",
        text,
        re.DOTALL
    )
    if min_match and min_match.group(1) != "0":
        result["minimum_amount_due"] = min_match.group(1)
    else:
        # Fallback
        min_match2 = re.search(r"Minimum Amount Due\s+([\d,]+\.\d{2})", text)
        result["minimum_amount_due"] = min_match2.group(1) if min_match2 else "0.00"
    
    # Credit Limit - Works!
    credit_match = re.search(r"Credit Limit[\s\S]*?([\d.,]+)", text)
    result["credit_limit"] = credit_match.group(1) if credit_match else "0.00"

    # Transactions - Works!
    transactions = []
    trans_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+([A-Z0-9* ]+)\s+([A-Z]+)?\s+([\d.,]+)", re.MULTILINE)
    for match in trans_pattern.finditer(text):
        if len(transactions) >= 10:
            break
        transactions.append({
            "date": match.group(1),
            "description": match.group(2).strip(),
            "amount": match.group(4)
        })
    result["transactions"] = transactions
    
    return result