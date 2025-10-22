import re
from datetime import datetime

def parse(text):
    result = {
        "bank": "icici",
        "cardholder_name": "N/A",
        "card_number": "N/A",
        "statement_date": "N/A",
        "payment_due_date": "N/A",
        "total_amount_due": "0.00",
        "minimum_amount_due": "0.00",
        "credit_limit": "0.00",
        "transactions": [],
        "transaction_categories": {
            "Fuel": 0,
            "Food": 0,
            "Shopping": 0,
            "Online Payments": 0,
            "Travel": 0,
            "Bills": 0,
            "Entertainment": 0,
            "Other": 0
        }
    }

    lines = text.splitlines()

    # ---- name, card, date, amounts (same as before) ---- #
    for line in lines[:50]:
        line = line.strip()
        if re.match(r'^(MR|MRS|MS|DR)\s+[A-Z][A-Z\s]{2,60}$', line):
            result["cardholder_name"] = line
            break

    card_match = re.search(r'(\d{4}[Xx\*]{4,12}\d{4})', text)
    if card_match:
        result["card_number"] = card_match.group(1)

    def find_date(label):
        for i, l in enumerate(lines):
            if re.search(label, l, re.IGNORECASE):
                for j in range(i, min(i + 5, len(lines))):
                    m = re.search(r'([A-Za-z]+\s+\d{1,2},\s*\d{4})', lines[j])
                    if m:
                        return normalize_date(m.group(1))
        return "N/A"

    result["statement_date"] = find_date("STATEMENT\\s+DATE")
    result["payment_due_date"] = find_date("PAYMENT\\s+DUE\\s+DATE")

    def find_amount(label):
        for i, l in enumerate(lines):
            if re.search(label, l, re.IGNORECASE):
                for j in range(i, min(i + 5, len(lines))):
                    m = re.search(r'[₹`]\s*([\d,]+\.\d{2})', lines[j])
                    if m:
                        return normalize_money(m.group(1))
        return "0.00"

    result["total_amount_due"] = find_amount("Total\\s+Amount\\s+due")
    result["minimum_amount_due"] = find_amount("Minimum\\s+Amount\\s+due")
    result["credit_limit"] = find_amount("Credit\\s+Limit")

    # ---- Transactions ---- #
    trans_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{4})\s+(\d{6,12})\s+([A-Za-z0-9\s\-,.&\'()/@]+?)\s+(-?\d+)\s+(\d{1,3}(?:,\d{3})*\.\d{2})\s*(CR|DR|Cr|Dr)?\s*',
        re.MULTILINE | re.IGNORECASE
    )

    transactions = []
    categories = result["transaction_categories"]

    for m in trans_pattern.finditer(text):
        desc = " ".join(m.group(3).split())
        if any(k in desc.upper() for k in ["DATE", "TRANSACTION", "DETAILS", "REWARD"]):
            continue

        amount_val = float(normalize_money(m.group(5)))
        tx_type = (m.group(6) or "").upper()

        tx = {
            "date": m.group(1),
            "serial_no": m.group(2),
            "description": desc,
            "points": m.group(4),
            "amount": normalize_money(m.group(5)),
            "type": tx_type
        }

        desc_l = desc.lower()

        # ---- Smarter Categorization ---- #
        if any(k in desc_l for k in ["fuel", "petrol", "indianoil", "hindustan petroleum", "hpcl", "bharat petroleum", "shell"]):
            categories["Fuel"] += amount_val
        elif any(k in desc_l for k in ["zomato", "swiggy", "restaurant", "food", "cafe", "dominos", "pizza", "mcdonald", "eat", "barbeque"]):
            categories["Food"] += amount_val
        elif any(k in desc_l for k in ["flipkart", "amazon", "myntra", "ajio", "shopping", "reliance digital", "rel retail", "croma", "electronics", "store", "mall"]):
            categories["Shopping"] += amount_val
        elif any(k in desc_l for k in ["upi", "paytm", "gpay", "google pay", "phonepe", "netbanking", "neft", "imps", "transfer", "received"]):
            categories["Online Payments"] += amount_val
        elif any(k in desc_l for k in ["irctc", "goibibo", "makemytrip", "yatra", "airlines", "indigo", "air india", "travel", "hotel", "booking"]):
            categories["Travel"] += amount_val
        elif any(k in desc_l for k in ["electricity", "gas", "water", "broadband", "postpaid", "prepaid", "billdesk", "vodafone", "airtel", "jio", "bsnl", "reliance energy"]):
            categories["Bills"] += amount_val
        elif any(k in desc_l for k in ["bookmyshow", "pvr", "inox", "cinema", "netflix", "spotify", "hotstar", "ott", "entertainment", "youtube"]):
            categories["Entertainment"] += amount_val
        else:
            categories["Other"] += amount_val

        transactions.append(tx)

    result["transactions"] = transactions
    result["transaction_categories"] = categories
    return result


# -------------------- Utility Helpers --------------------
def normalize_money(s):
    if not s:
        return "0.00"
    s2 = s.replace("`", "").replace("₹", "").replace(",", "").strip()
    if re.match(r'^\d+$', s2):
        return f"{s2}.00"
    if re.match(r'^\d+\.\d$', s2):
        return f"{s2}0"
    return s2


def normalize_date(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%d/%m/%Y")
    except:
        if re.match(r'\d{2}/\d{2}/\d{4}', date_str):
            return date_str
        return "N/A"
