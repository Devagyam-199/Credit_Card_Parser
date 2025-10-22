import re

def normalize_money(s):
    if not s:
        return "0.00"
    s = s.replace("₹", "").replace("r", "").replace(",", "").strip()
    s = re.sub(r"[^\d.]", "", s)
    return s if s else "0.00"

def parse(text):
    """
    IDFC FIRST Bank Credit Card Statement Parser
    Clean, HDFC-style output: key data points + clean transactions.
    """
    result = {}

    # --- 1️⃣ Basic Details ---
    period = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", text)
    if period:
        result["statement_period"] = f"{period.group(1)} - {period.group(2)}"
        result["statement_start_date"] = period.group(1)
        result["statement_end_date"] = period.group(2)
    else:
        result["statement_period"] = result["statement_start_date"] = result["statement_end_date"] = "N/A"

    name = re.search(r"([A-Z][a-z]+\s+[A-Z][a-z]+)", text)
    result["cardholder_name"] = name.group(1).strip() if name else "N/A"

    acc = re.search(r"Account\s*Number\s*[:\-]?\s*(\d{8,})", text, re.IGNORECASE)
    result["account_number"] = acc.group(1) if acc else "N/A"

    rel = re.search(r"Customer\s*Relationship\s*(?:No\.?|Number)?\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
    result["customer_relationship_no"] = rel.group(1) if rel else "N/A"

    due = re.search(r"Payment\s*Due\s*Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    result["payment_due_date"] = due.group(1) if due else "N/A"

    open_bal = re.search(r"Opening\s+Balance\s*[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", text, re.IGNORECASE)
    result["opening_balance"] = normalize_money(open_bal.group(1)) if open_bal else "0.00"

    total_due = re.search(r"Total\s+Amount\s+Due\s*[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", text, re.IGNORECASE)
    result["total_amount_due"] = normalize_money(total_due.group(1)) if total_due else "0.00"

    min_due = re.search(r"Minimum\s+Amount\s+Due\s*[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", text, re.IGNORECASE)
    result["minimum_amount_due"] = normalize_money(min_due.group(1)) if min_due else "0.00"

    credit_lim = re.search(r"Credit\s*Limit[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", text, re.IGNORECASE)
    result["credit_limit"] = normalize_money(credit_lim.group(1)) if credit_lim else "0.00"

    avail_credit = re.search(r"Available\s*Credit[^\d]*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", text, re.IGNORECASE)
    result["available_credit"] = normalize_money(avail_credit.group(1)) if avail_credit else "0.00"

    # --- 2️⃣ Extract Transaction Section ---
    tx_start = text.find("YOUR TRANSACTIONS")
    tx_end = text.find("REWARDS SUMMARY")
    tx_text = text[tx_start:tx_end] if tx_start != -1 and tx_end != -1 else text

    # clean up weird characters
    tx_text = re.sub(r"\(cid:[^)]+\)", "", tx_text)
    tx_text = re.sub(r"\s{2,}", " ", tx_text)

    transactions = []
    pattern = re.compile(
        r"(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<desc>[A-Za-z0-9 &,\-\.\(\)/]+?)\s+(?P<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2}))(?:\s*(?P<cr>CR))?(?=\s|$)",
        re.MULTILINE
    )

    for m in pattern.finditer(tx_text):
        desc = m.group("desc").strip()
        # Filter out junk lines
        if any(keyword in desc.lower() for keyword in [
            "message of the month", "statement summary", "rewards summary",
            "special offers", "important information", "page ", "click here", "payment modes"
        ]):
            continue

        tx = {
            "date": m.group("date"),
            "description": desc,
            "amount": normalize_money(m.group("amount")),
            "type": "CR" if m.group("cr") else "DR"
        }
        transactions.append(tx)

    # Filter out duplicate/junk entries
    clean_tx = []
    seen = set()
    for t in transactions:
        key = (t["date"], t["description"], t["amount"])
        if key not in seen:
            seen.add(key)
            clean_tx.append(t)

    result["transactions"] = clean_tx
    result["bank_detected"] = "idfc"

    return result
