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


def likely_name_line(s):
    """Return True if s looks like a person's name (Title Case, letters & spaces)."""
    s = s.strip()
    # reject lines that contain digits or punctuation that indicate address/header
    if re.search(r"\d", s):
        return False
    if len(s) < 3 or len(s) > 60:
        return False
    # reject lines that are clearly header words or all uppercase headers
    bad_headers = {"MESSAGE OF THE MONTH", "STATEMENT SUMMARY", "PAYMENT DUE DATE", "ACCOUNT NUMBER", "CUSTOMER RELATIONSHIP"}
    if s.upper() in bad_headers:
        return False
    # reject if contains common address tokens
    address_tokens = ["H-NO", "H.NO", "HOUSE", "HNO", "GURGAON", "HARYANA", "PIN", "PINCODE", "ROAD", "STREET", "NEAR", "APT", "FLAT", "GURGAON-"]
    if any(tok in s.upper() for tok in address_tokens):
        return False
    # Accept Title Case like "Ved Prakash" or "Nikhil Khandelwal"
    if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$", s):
        return True
    # Also accept capitalized names with initials: "A K Sharma" or "A. K. Sharma"
    if re.match(r"^[A-Z](?:\.?|\b)(?:\s+[A-Z](?:\.?|\b))*\s+[A-Z][a-z]+$", s):
        return True
    # lastly, accept mixed-case names that have at least two words and at least one lowercase letter
    if len(s.split()) >= 2 and re.search(r"[a-z]", s):
        return True
    return False


def parse(text):
    """
    IDFC FIRST Bank Credit Card Statement Parser
    Improved name extraction with iterative regex & heuristics
    """
    result = {}
    lines = text.splitlines()
    raw_lines = lines_of(text)

    # --- Statement Period ---
    period = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", text)
    if period:
        result["statement_period"] = f"{period.group(1)} - {period.group(2)}"
        result["statement_start_date"] = period.group(1)
        result["statement_end_date"] = period.group(2)
    else:
        result["statement_period"] = "N/A"
        result["statement_start_date"] = "N/A"
        result["statement_end_date"] = "N/A"

    # --- 2️⃣ Cardholder Name (final robust logic for IDFC) ---
    name = re.search(r"([A-Z][a-z]+\s+[A-Z][a-z]+)", text)
    result["cardholder_name"] = name.group(1).strip() if name else "N/A"

    # --- Account & Customer Details ---
    acc = re.search(r"Account\s*Number\s*[:\s]*(\d{8,})", text, re.IGNORECASE)
    result["account_number"] = acc.group(1) if acc else "N/A"

    rel = re.search(r"Customer\s*Relationship\s*(?:No\.?)?\s*(\d+)", text, re.IGNORECASE)
    result["customer_relationship_no"] = rel.group(1) if rel else "N/A"

    # --- Payment Due Date ---
    due_match = re.search(r"Payment\s+Due\s+Date.*?(\d{2}/\d{2}/\d{4})", text, re.DOTALL | re.IGNORECASE)
    result["payment_due_date"] = due_match.group(1) if due_match else "N/A"

    # --- Financial Summary ---
    summary_idx = -1
    for i, line in enumerate(lines):
        if "STATEMENT SUMMARY" in line.upper():
            summary_idx = i
            break

    if summary_idx != -1:
        summary_section = "\n".join(lines[summary_idx : summary_idx + 20])

        open_match = re.search(r"Opening\s*Balance.*?r(\d+(?:,\d+)*(?:\.\d+)?)", summary_section, re.IGNORECASE | re.DOTALL)
        result["opening_balance"] = normalize_money(open_match.group(1)) if open_match else "0.00"

        total_match = re.search(r"Total\s*Amount\s*Due.*?r(\d+(?:,\d+)*(?:\.\d+)?)", summary_section, re.IGNORECASE | re.DOTALL)
        result["total_amount_due"] = normalize_money(total_match.group(1)) if total_match else "0.00"

        min_match = re.search(r"Minimum\s*Amount\s*Due.*?r(\d+(?:,\d+)*(?:\.\d+)?)", summary_section, re.IGNORECASE | re.DOTALL)
        result["minimum_amount_due"] = normalize_money(min_match.group(1)) if min_match else "0.00"

        # Try to capture credit & available limits (flexible)
        # Many statements put them on a single line or adjacent lines; search entire summary_section for two r-values.
        limit_values = re.findall(r"r(\d{1,3}(?:,\d{2,3})*(?:,\d{3})*(?:\.\d+)?)", summary_section, flags=re.IGNORECASE)
        # normalize and dedupe numeric values (preserve order of appearance)
        limits_norm = []
        for v in limit_values:
            nv = normalize_money(v)
            if nv not in limits_norm:
                limits_norm.append(nv)
        # heuristics: credit limit tends to be the largest (or first/last depending on layout)
        if len(limits_norm) >= 2:
            # try to pick the largest as credit_limit
            numeric = [(float(x), x) for x in limits_norm]
            numeric_sorted = sorted(numeric, key=lambda t: t[0], reverse=True)
            result["credit_limit"] = numeric_sorted[0][1]
            # pick next largest as available_credit if available
            result["available_credit"] = numeric_sorted[1][1] if len(numeric_sorted) > 1 else "0.00"
        else:
            result["credit_limit"] = "0.00"
            result["available_credit"] = "0.00"
    else:
        result["opening_balance"] = "0.00"
        result["total_amount_due"] = "0.00"
        result["minimum_amount_due"] = "0.00"
        result["credit_limit"] = "0.00"
        result["available_credit"] = "0.00"

    # --- Card Number ---
    card = re.search(r"Card\s*Number:\s*XXXX\s*(\d{4})", text, re.IGNORECASE)
    result["card_number"] = f"XXXX{card.group(1)}" if card else "N/A"

    # --- Transactions (kept as before) ---
    transactions = []
    tx_start_idx = -1
    tx_end_idx = -1

    for i, line in enumerate(lines):
        if "YOUR TRANSACTIONS" in line.upper():
            tx_start_idx = i
        if tx_start_idx != -1 and ("REWARDS" in line.upper() or "IMPORTANT INFORMATION" in line.upper()):
            tx_end_idx = i
            break

    if tx_start_idx != -1:
        if tx_end_idx == -1:
            tx_end_idx = len(lines)

        tx_lines = lines[tx_start_idx:tx_end_idx]
        tx_text = "\n".join(tx_lines)

        pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d+(?:,\d+)*(?:\.\d+)?)\s*(CR)?", re.MULTILINE)

        for match in pattern.finditer(tx_text):
            desc = match.group(2).strip()
            skip = ["Transaction Date", "Transactional Details", "FX Transactions", "Amount", "Page ", "Card Number"]
            if any(s in desc for s in skip):
                continue
            desc = " ".join(desc.split())
            if len(desc) > 2:
                transactions.append({
                    "date": match.group(1),
                    "description": desc,
                    "amount": normalize_money(match.group(3)),
                    "type": "CR" if match.group(4) else "DR"
                })

    # dedupe transactions
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
