import re

def parse(text):
    result = {}
    result["cardholder_name"] = re.search(r"^\s*([A-Z. ]+ \d+)", text, re.MULTILINE).group(1) if re.search(r"^\s*([A-Z. ]+ \d+)", text, re.MULTILINE) else "N/A"
    result["card_number"] = re.search(r"(\d{4}X{8}\d{4})", text).group(1) if re.search(r"(\d{4}X{8}\d{4})", text) else "N/A"
    result["statement_date"] = re.search(r"STATEMENT DATE\s*([A-Za-z]+ \d{2}, \d{4})", text, re.IGNORECASE).group(1) if re.search(r"STATEMENT DATE\s*([A-Za-z]+ \d{2}, \d{4})", text, re.IGNORECASE) else "N/A"
    result["payment_due_date"] = re.search(r"PAYMENT DUE DATE\s*([A-Za-z]+ \d{2}, \d{4})", text, re.IGNORECASE).group(1) if re.search(r"PAYMENT DUE DATE\s*([A-Za-z]+ \d{2}, \d{4})", text, re.IGNORECASE) else "N/A"
    result["total_amount_due"] = re.search(r"Total Amount Due\s*([\d.,]+)", text).group(1) if re.search(r"Total Amount Due\s*([\d.,]+)", text) else "0.00"
    result["minimum_amount_due"] = re.search(r"Minimum Amount Due\s*([\d.,]+)", text).group(1) if re.search(r"Minimum Amount Due\s*([\d.,]+)", text) else "0.00"
    result["credit_limit"] = re.search(r"Credit Limit\s*([\d.,]+)", text).group(1) if re.search(r"Credit Limit\s*([\d.,]+)", text) else "0.00"

    transactions = []
    trans_pattern = re.compile(r"(\d{2}\/\d{2}\/\d{4})\s+(\d+)\s+([A-Z \/]+ Received)\s+(\d)\s+([\d.,]+) (CR)?", re.MULTILINE)
    for match in trans_pattern.finditer(text):
        transactions.append({
            "date": match.group(1),
            "description": match.group(3),
            "amount": f"{match.group(5)} {match.group(6) or 'Dr'}"
        })
    result["transactions"] = transactions[:10]

    return result