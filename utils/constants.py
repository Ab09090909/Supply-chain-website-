# Ethiopian Cities
ETHIOPIAN_CITIES = [
    "Addis Ababa", "Dire Dawa", "Mekelle", "Gondar", "Bahir Dar", 
    "Hawassa", "Adama", "Jimma", "Dessie", "Harar", "Shashamane", 
    "Bishoftu", "Arba Minch", "Nekemte", "Debre Markos", "Debre Birhan"
]

# Commercial Sectors
SECTORS = [
    "Agriculture", "Manufacturing", "Construction", "Textiles", 
    "Electronics", "Pharmaceuticals"
]

# Product Categories
CATEGORIES = [
    "Grains", "Vegetables", "Fruits", "Livestock", "Building Materials", 
    "Fabrics", "Machinery", "Medicines", "Consumer Goods"
]

# Local Payment Methods
PAYMENT_METHODS = ["Telebirr", "CBE Birr", "Dashen Bank", "Amole"]

# Order Status Flow
ORDER_STATUSES = ["Pending", "Confirmed", "Shipped", "Delivered", "Completed"]

# Unit Types
UNIT_TYPES = ["kg", "quintal", "ton", "piece", "box", "liter", "meter"]

# Currency Formatting Helper
def format_etb(amount: float) -> str:
    """Formats a number as Ethiopian Birr with comma separators."""
    return f"ETB {amount:,.2f}"
