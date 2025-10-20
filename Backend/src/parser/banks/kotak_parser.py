import re

def parse(text):
    result = {}
    result["cardholder_name"] = re.search(r"^\s*([A-Z ]+ CVS)", text, re.MULTILINE).group(1) if re.search(r"^\s*([A-Z ]+ CVS)", text, re.MULTILINE) else "N/A"
    result["card_number"] = re.search(r"Primary Card Transactions:\s*(\d{6}XXXXX\d{4})", text).group(1) if re.search(r"Primary Card Transactions:\s*(\d{6}XXXXX\d{4})", text) else "N/A"
    result["statement_date"] = re.search(r"Statement Date\s*(\d{1,2}-[A-Za-z]{3}-\d{4})", text).group(1) if re.search(r"Statement Date\s*(\d{1,2}-[A-Za-z]{3}-\d{4})", text) else "N/A"
    result["payment_due_date"] = re.search(r"Due Date\s*(\d{1,2}-[A-Za-z]{3}-\d{4})", text).group(1) if re.search(r"Due Date\s*(\d{1,2}-[A-Za-z]{3}-\d{4})", text) else "N/A"
    result["total_amount_due"] = re.search(r"Total Amount Due \(Rs\.\)\s*([\d.,]+)", text).group(1) if re.search(r"Total Amount Due \(Rs\.\)\s*([\d.,]+)", text) else "0.00"
    result["minimum_amount_due"] = "0.00"
    result["credit_limit"] = re.search(r"Credit Limit \(Rs\.\)\s*([\d.,]+)", text).group(1) if re.search(r"Credit Limit \(Rs\.\)\s*([\d.,]+)", text) else "0.00"

    transactions = []
    trans_pattern = re.compile(r"(\d{2}\/\d{2}\/\d{4})\s+([A-Z0-9*. ]+)\s+([A-Z ]+ \s+ IN)?\s+([A-Za-z]+)\s+([\d.,]+)(Cr)?", re.MULTILINE)
    for match in trans_pattern.finditer(text):
        transactions.append({
            "date": match.group(1),
            "description": match.group(2),
            "amount": f"{match.group(5)} {match.group(6) or ''}"
        })
    result["transactions"] = transactions[:10]

    return result