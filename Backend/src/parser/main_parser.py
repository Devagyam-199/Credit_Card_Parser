import os
import json
import re
from pdfplumber import open as pdf_open
from bank_detect import bank_detect
from banks.axis_parser import parse as axis_parse
from banks.hdfc_parser import parse as hdfc_parse
from banks.icici_parser import parse as icici_parse
from banks.idfc_parser import parse as idfc_parse
from banks.general_parser import parse as general_parse

def extract_text_native(pdf_path):
    text = ""
    with pdf_open(pdf_path) as pdf:
        text_pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(text_pages)
    if not text.strip():
        raise ValueError("No text extracted from PDF. Ensure it's not a scanned image.")
    return text

def parse_credit_card_statement(pdf_path):
    text = extract_text_native(pdf_path)
    bank, confidence = bank_detect(text)
    print(f"Detected: {bank} ({confidence})")
    parsers = {
        "axis": axis_parse,
        "hdfc": hdfc_parse,
        "icici": icici_parse,
        "idfc": idfc_parse,
    }

    if bank and confidence >= 10:
        parser = parsers.get(bank.lower())
        if parser:
            result = parser(text)
            result["bank_detected"] = bank
        else:
            print(f"Specific parser not found for {bank}; using general.")
            result = general_parse(text)
            result["bank_detected"] = bank
    else:
        print("Bank detection failed/low confidence; using general parser.")
        result = general_parse(text)
        result["bank_detected"] = "Unknown"
        confidence = 0

    if "bank_detected" not in result:
        result["bank_detected"] = bank or "Unknown"

    result["transaction_categories"] = categorize_transactions(result.get("transactions", []))
    result["extraction_method"] = "Native"
    result["confidence"] = confidence
    return result

def categorize_transactions(transactions):
    categories = {
        "Fuel": 0,
        "Food": 0,
        "Shopping": 0,
        "Travel": 0,
        "Bills": 0,
        "Entertainment": 0,
        "Other": 0,
    }

    for tx in transactions:
        desc = tx.get("description", "").lower()
        desc = re.sub(r'[^a-z0-9 ]+', ' ', desc)
        amount_str = re.sub(r"[^\d.]", "", str(tx.get("amount", 0)))
        amount = float(amount_str) if amount_str else 0
        tx_type = str(tx.get("type", "")).upper()

        if "CR" in tx_type or tx.get("is_credit"):
            continue

        if any(word in desc for word in ["fuel", "petrol", "diesel", "hpcl", "ioc", "indianoil", "bharat petroleum", "shell", "pump"]):
            categories["Fuel"] += amount
        elif any(word in desc for word in ["food", "zomato", "swiggy", "restaurant", "cafe", "dominos", "pizza", "mcdonald", "kfc", "burger", "dining"]):
            categories["Food"] += amount
        elif any(word in desc for word in ["flipkart", "amazon", "myntra", "ajio", "meesho", "store", "shopping", "bigbasket", "reliance digital", "rel retail", "digital", "retail", "mall"]):
            categories["Shopping"] += amount
        elif any(word in desc for word in ["makemytrip", "ixigo", "irctc", "goibibo", "uber", "ola", "rapido", "flight", "hotel", "booking", "bus", "train"]):
            categories["Travel"] += amount
        elif any(word in desc for word in ["electricity", "water", "gas", "broadband", "mobile", "recharge", "postpaid", "dth", "billdesk", "bill payment", "airtel", "jio"]):
            categories["Bills"] += amount
        elif any(word in desc for word in ["netflix", "hotstar", "prime video", "spotify", "bookmyshow", "movie", "game", "youtube", "pvr", "inox"]):
            categories["Entertainment"] += amount
        elif any(word in desc for word in ["upi", "neft", "imps", "payment", "transfer"]):
            categories["Bills"] += amount
        else:
            categories["Other"] += amount

    return categories

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python main_parser.py <pdf_path>"}))
        sys.exit(1)
    try:
        result = parse_credit_card_statement(sys.argv[1])
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))