import os
import json  # NEW: For json.dumps
import re
from pdfplumber import open as pdf_open
from bank_detect import bank_detect
# Explicit imports (avoids package issues)
from banks.axis_parser import parse as axis_parse
from banks.hdfc_parser import parse as hdfc_parse
from banks.icici_parser import parse as icici_parse
from banks.kotak_parser import parse as kotak_parse
from banks.general_parser import parse as general_parse  # Fallback

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
    
    # Specific parsers
    parsers = {
        "axis": axis_parse,
        "kotak": kotak_parse,
        "hdfc": hdfc_parse,
        "icici": icici_parse
    }
    
    # Use specific if detected and confident; else general
    if bank and confidence >= 20:
        parser = parsers.get(bank.lower())
        if parser:
            result = parser(text)
        else:
            print(f"Specific parser not found for {bank}; using general.")
            result = general_parse(text)
            result["bank_detected"] = bank
    else:
        print("Bank detection failed; using general parser.")
        result = general_parse(text)
        result["bank_detected"] = "Unknown"
        confidence = 0
    
    # Add categorization
    result["transaction_categories"] = categorize_transactions(result.get("transactions", []))
    result["extraction_method"] = "Native"
    result["confidence"] = confidence
    return result

def categorize_transactions(transactions):
    categories = {
        "Fuel": 0,
        "Food": 0,
        "Shopping": 0,
        "Online Payments": 0,
        "Bills": 0,
        "Entertainment": 0,
        "Other": 0,
    }

    for tx in transactions:
        desc = tx.get("description", "").lower()
        amount_str = re.sub(r"[^\d.]", "", str(tx.get("amount", 0)))
        amount = float(amount_str) if amount_str else 0

        # --- Fuel ---
        if any(word in desc for word in ["fuel", "petrol", "hpcl", "ioc", "indianoil", "bharat petroleum"]):
            categories["Fuel"] += amount

        # --- Food / Dining ---
        elif any(word in desc for word in ["food", "zomato", "swiggy", "restaurant", "cafe", "dominos", "pizza"]):
            categories["Food"] += amount

        # --- Shopping ---
        elif any(word in desc for word in ["flipkart", "amazon", "myntra", "ajio", "meesho", "store", "shopping", "bigbasket"]):
            categories["Shopping"] += amount

        # --- Online Payments (NEW) ---
        elif any(word in desc for word in [
            "paytm", "gpay", "google pay", "phonepe", "upi", "imps", "neft",
            "instapay", "transfer", "netbanking", "bhim", "rtgs", "bank transfer"
        ]):
            categories["Online Payments"] += amount

        # --- Bills & Utilities ---
        elif any(word in desc for word in [
            "electricity", "water", "gas", "broadband", "mobile", "recharge",
            "postpaid", "dth", "billdesk", "bill payment"
        ]):
            categories["Bills"] += amount

        # --- Entertainment ---
        elif any(word in desc for word in [
            "netflix", "hotstar", "prime video", "spotify", "bookmyshow", "movie", "game"
        ]):
            categories["Entertainment"] += amount

        # --- Everything else ---
        else:
            categories["Other"] += amount

    return categories


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python main_parser.py <pdf_path>"}))  # JSON error
        sys.exit(1)
    try:
        result = parse_credit_card_statement(sys.argv[1])
        print(json.dumps(result, indent=2))  # FIXED: Valid JSON output
    except Exception as e:
        print(json.dumps({"error": str(e)}))  # JSON-safe error