import re


def lines_of(text):
    return [ln.rstrip() for ln in text.splitlines()]


def normalize_money(s):
    """Clean money strings: r18,100 → 18100.00"""
    if not s:
        return "0.00"
    s = s.replace("₹", "").replace("r", "").replace(",", "").strip()
    s = re.sub(r"[^\d.]", "", s)
    if not s:
        return "0.00"
    if "." not in s:
        return f"{s}.00"
    return s


def looks_like_name(s):
    """Return True if s looks like a personal name like 'Ved Prakash'."""
    s = s.strip()
    if not s:
        return False
    if re.search(r"\d|₹|r", s, re.IGNORECASE):  # reject lines with digits or money
        return False
    if len(s.split()) > 4 or len(s.split()) < 2:
        return False
    if not re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$", s):
        return False
    return True


def next_line_has_address(next_line: str):
    if not next_line:
        return False
    addr_tokens = [
        "H-NO", "H.NO", "HOUSE", "HNO", "ROAD", "STREET",
        "NEAR", "APT", "FLAT", "COLONY", "SECTOR", "GURGAON",
        "HARYANA", "PIN", "PINCODE", "TOWER", "EXTN", "AREA"
    ]
    up = next_line.upper()
    return any(tok in up for tok in addr_tokens)


def extract_name_idfc(text):
    """IDFC-specific name extraction based on actual PDF layout."""
    raw = lines_of(text)
    for i, line in enumerate(raw):
        if re.search(r"Account\s*Number", line, re.IGNORECASE):
            # Check the next 12 lines
            for j in range(i + 1, min(i + 12, len(raw))):
                cand = raw[j].strip()
                if not cand or len(cand) < 3:
                    continue
                # skip numeric or currency-like lines
                if re.search(r"[₹r\d]", cand):
                    continue
                if "TOTAL" in cand.upper() or "AMOUNT" in cand.upper() or "DUE" in cand.upper():
                    continue
                next_line = raw[j + 1].strip() if j + 1 < len(raw) else ""
                if looks_like_name(cand) and next_line_has_address(next_line):
                    return cand
                if looks_like_name(cand):
                    return cand
            break
    return "N/A"


def parse(text):
    """IDFC FIRST Bank Credit Card Statement Parser (final corrected)."""
    result = {}
    lines = text.splitlines()

    # --- Statement Period ---
    period = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", text)
    if period:
        result["statement_period"] = f"{period.group(1)} - {period.group(2)}"
        result["statement_start_date"] = period.group(1)
        result["statement_end_date"] = period.group(2)
    else:
        result.update({
            "statement_period": "N/A",
            "statement_start_date": "N/A",
            "statement_end_date": "N/A"
        })

    # --- ✅ Fixed Cardholder Name Extraction ---
    result["cardholder_name"] = extract_name_idfc(text)

    # --- Account & Relationship ---
    acc = re.search(r"Account\s*Number\s*[:\s]*([0-9]{6,})", text, re.IGNORECASE)
    result["account_number"] = acc.group(1) if acc else "N/A"

    rel = re.search(r"Customer\s*Relationship\s*(?:No\.?)?\s*([0-9A-Za-z\-]+)", text, re.IGNORECASE)
    result["customer_relationship_no"] = rel.group(1) if rel else "N/A"

    # --- Payment Due Date ---
    due_match = re.search(r"Payment\s+Due\s+Date.*?(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE | re.DOTALL)
    result["payment_due_date"] = due_match.group(1) if due_match else "N/A"

    # --- Financial Summary ---
    summary_idx = next((i for i, l in enumerate(lines) if "STATEMENT SUMMARY" in l.upper()), -1)
    if summary_idx != -1:
        summary_section = "\n".join(lines[summary_idx: summary_idx + 25])
        open_match = re.search(r"Opening\s*Balance.*?r(\d[\d,\.]*)", summary_section, re.IGNORECASE | re.DOTALL)
        total_match = re.search(r"Total\s*Amount\s*Due.*?r(\d[\d,\.]*)", summary_section, re.IGNORECASE | re.DOTALL)
        min_match = re.search(r"Minimum\s*Amount\s*Due.*?r(\d[\d,\.]*)", summary_section, re.IGNORECASE | re.DOTALL)

        result["opening_balance"] = normalize_money(open_match.group(1)) if open_match else "0.00"
        result["total_amount_due"] = normalize_money(total_match.group(1)) if total_match else "0.00"
        result["minimum_amount_due"] = normalize_money(min_match.group(1)) if min_match else "0.00"

        limit_values = re.findall(r"r(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?)", summary_section, re.IGNORECASE)
        limits_norm = []
        for v in limit_values:
            nv = normalize_money(v)
            if nv not in limits_norm:
                limits_norm.append(nv)
        if len(limits_norm) >= 2:
            numeric = [(float(x), x) for x in limits_norm]
            numeric_sorted = sorted(numeric, key=lambda t: t[0], reverse=True)
            result["credit_limit"] = numeric_sorted[0][1]
            result["available_credit"] = numeric_sorted[1][1]
        else:
            result["credit_limit"] = "0.00"
            result["available_credit"] = "0.00"
    else:
        result.update({
            "opening_balance": "0.00",
            "total_amount_due": "0.00",
            "minimum_amount_due": "0.00",
            "credit_limit": "0.00",
            "available_credit": "0.00"
        })

    # --- Card Number ---
    card = re.search(r"Card\s*Number\s*[:\s]*XXXX\s*(\d{4})", text, re.IGNORECASE)
    result["card_number"] = f"XXXX{card.group(1)}" if card else "N/A"

    # --- Transactions ---
    transactions = []
    tx_start_idx = tx_end_idx = -1
    for i, line in enumerate(lines):
        if "YOUR TRANSACTIONS" in line.upper():
            tx_start_idx = i
        if tx_start_idx != -1 and ("REWARDS" in line.upper() or "IMPORTANT INFORMATION" in line.upper()):
            tx_end_idx = i
            break

    if tx_start_idx != -1:
        tx_end_idx = tx_end_idx if tx_end_idx != -1 else len(lines)
        tx_section = "\n".join(lines[tx_start_idx:tx_end_idx])

        tx_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d[\d,\.]*)\s*(CR)?", re.MULTILINE)
        for match in tx_pattern.finditer(tx_section):
            desc = match.group(2).strip()
            if any(skip in desc for skip in ["Transaction Date", "Transactional Details", "FX Transactions", "Amount", "Page", "Card Number"]):
                continue
            transactions.append({
                "date": match.group(1),
                "description": " ".join(desc.split()),
                "amount": normalize_money(match.group(3)),
                "type": "CR" if match.group(4) else "DR"
            })

    seen = set()
    unique_txns = []
    for tx in transactions:
        key = (tx["date"], tx["description"], tx["amount"])
        if key not in seen:
            seen.add(key)
            unique_txns.append(tx)

    result["transactions"] = unique_txns
    result["bank_detected"] = "idfc"
    return result
