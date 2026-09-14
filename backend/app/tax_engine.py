# FBR Withholding Tax Rules Engine
# Based on Tax Year 2027 Rate Card
# Source: Federal Board of Revenue (FBR) Pakistan

TAX_RULES = {
    "professional_services": {
        "description": "Professional services (lawyers, consultants, doctors, etc.)",
        "section": "153(1)(b)",
        "rate_filer": 0.08,
        "rate_non_filer": 0.16,
    },
    "supply_of_goods": {
        "description": "Supply of goods",
        "section": "153(1)(a)",
        "rate_filer": 0.04,
        "rate_non_filer": 0.08,
    },
    "rent": {
        "description": "Rent of immovable property",
        "section": "155",
        "rate_filer": 0.15,
        "rate_non_filer": 0.30,
    },
    "salary": {
        "description": "Salary income",
        "section": "149",
        "rate_filer": 0.05,
        "rate_non_filer": 0.05,
    },
    "advertising": {
        "description": "Advertising services",
        "section": "153(1)(b)",
        "rate_filer": 0.10,
        "rate_non_filer": 0.20,
    },
    "transport": {
        "description": "Transport / freight services",
        "section": "153(1)(b)",
        "rate_filer": 0.02,
        "rate_non_filer": 0.04,
    },
    "other": {
        "description": "Other / unclassified",
        "section": "153(1)(b)",
        "rate_filer": 0.08,
        "rate_non_filer": 0.16,
    }
}

KEYWORD_MAP = {
    "professional_services": [
        "consultant", "consulting", "legal", "lawyer", "doctor",
        "accountant", "audit", "advisory", "engineering", "architect"
    ],
    "supply_of_goods": [
        "supply", "goods", "product", "material", "equipment",
        "hardware", "purchase", "inventory", "stock"
    ],
    "rent": [
        "rent", "lease", "property", "office space", "building", "premises"
    ],
    "salary": [
        "salary", "salaries", "payroll", "wages", "compensation"
    ],
    "advertising": [
        "advertising", "advertisement", "marketing", "media", "promotion"
    ],
    "transport": [
        "transport", "freight", "logistics", "delivery", "shipping", "courier"
    ]
}


def classify_transaction(description: str) -> str:
    description_lower = description.lower()
    for category, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return "other"


def calculate_tax(amount: float, transaction_type: str, is_filer: bool = True) -> dict:
    rule = TAX_RULES.get(transaction_type, TAX_RULES["other"])
    rate = rule["rate_filer"] if is_filer else rule["rate_non_filer"]
    tax_amount = round(amount * rate, 2)
    return {
        "transaction_type": transaction_type,
        "description": rule["description"],
        "section": rule["section"],
        "amount": amount,
        "rate_applied": f"{rate * 100}%",
        "withholding_tax": tax_amount,
        "amount_after_tax": round(amount - tax_amount, 2),
        "taxpayer_status": "Filer" if is_filer else "Non-Filer"
    }


def process_invoice_tax(extracted_data: dict, is_filer: bool = True) -> dict:
    description = extracted_data.get("description", "")
    transaction_type = classify_transaction(description)

    try:
        amount = float(extracted_data.get("total_amount", 0) or 0)
    except:
        amount = 0.0

    tax_result = calculate_tax(amount, transaction_type, is_filer)
    return tax_result