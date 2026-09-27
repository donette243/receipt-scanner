import re
import unicodedata


CATEGORIES = {
    "food": [
       
        "milk", "lait",
        "bread", "pain",
        "rice", "riz",
        "pasta", "pates", "pâtes",
        "meat", "viande",
        "chicken", "poulet",
        "fish", "poisson",
        "seafood", "fruits de mer",
        "cheese", "fromage",
        "apple", "pomme",
        "banana", "banane",
        "orange",
        "tomato", "tomate",
        "potato", "pomme de terre",
        "sugar", "sucre",
        "salt", "sel",
        "oil", "huile",
        "flour", "farine",
        "egg", "oeuf", "œuf",
        "cereal", "cereales", "céréales",
        "yogurt", "yaourt",
        "beef", "boeuf", "bœuf",
        "pork", "porc",
        "entrecote", "entrecôte",
        "steak",
        "burger", "hamburger",
        "pizza",
        "sandwich",
        "frite", "frites",
        "salade",
        "soupe", "soup",
        "dessert",
        "gateau", "gâteau",
        "tarte",
        "glace", "ice cream",
        "chocolat", "chocolate",
        "молоко",
        "хлеб",
        "рис",
        "макароны",
        "паста",
        "мясо",
        "курица",
        "рыба",
        "сыр",
        "яблоко",
        "яблоки",
        "банан",
        "бананы",
        "апельсин",
        "помидор",
        "томаты",
        "картофель",
        "сахар",
        "соль",
        "масло",
        "мука",
        "яйцо",
        "яйца",
        "йогурт",
        "говядина",
        "свинина",
        "колбаса",
        "сосиски",
        "шоколад",
        "конфеты",
        "печенье",
    ],

    "beverages": [
        
        "water", "eau",
        "badoit",
        "evian",
        "vittel",
        "perrier",
        "san pellegrino",
        "coca", "coca cola",
        "pepsi",
        "fanta",
        "sprite",
        "orangina",
        "schweppes",
        "soda",
        "soft drink",
        "juice", "jus",
        "coffee", "cafe", "café",
        "espresso",
        "cappuccino",
        "latte",
        "tea", "the", "thé",
        "beer", "biere", "bière",
        "vin", "wine",
        "champagne",
        "vodka",
        "whisky", "whiskey",
        "rum", "rhum",
        "gin",
        "tequila",
        "cocktail",
        "aperol",
        "spritz",
        "mojito",

        "вода",
        "сок",
        "кофе",
        "чай",
        "лимонад",
        "газировка",
        "напиток",
        "пиво",
        "вино",
        "шампанское",
        "водка",
        "виски",
        "ром",
        "джин",
        "коктейль",
    ],

    "hygiene": [
        
        "shampoo", "shampoing",
        "soap", "savon",
        "toothpaste", "dentifrice",
        "deodorant", "déodorant",
        "cream", "crème",
        "toothbrush",
        "brosse a dents",
        "brosse à dents",
        "gel douche",
        "toilet paper",
        "papier toilette",
        "tampon",
        "serviette hygienique",
        "serviette hygiénique",
        "шампунь",
        "мыло",
        "зубная паста",
        "зубная щетка",
        "дезодорант",
        "гель для душа",
        "туалетная бумага",
        "крем",
        "тампоны",
        "прокладки",
    ],

    "clothing": [
       
        "shirt", "chemise",
        "t-shirt", "tee shirt",
        "pants", "pantalon",
        "dress", "robe",
        "shoes", "chaussures",
        "jacket", "veste",
        "coat", "manteau",
        "jeans",
        "chaussette", "chaussettes",
        "socks",
        "sweater",
        "pull", "pull-over",

        "рубашка",
        "футболка",
        "брюки",
        "платье",
        "обувь",
        "кроссовки",
        "куртка",
        "пальто",
        "джинсы",
        "носки",
        "свитер",
    ],

    "electronics": [
        
        "phone",
        "telephone", "téléphone",
        "computer", "ordinateur",
        "laptop",
        "earphones",
        "ecouteurs", "écouteurs",
        "headphones",
        "casque audio",
        "charger", "chargeur",
        "cable", "câble",
        "keyboard", "clavier",
        "mouse", "souris",
        "monitor",
        "ecran", "écran",
        "usb",
        "iphone",
        "android",
        "tablet", "tablette",
        "телефон",
        "смартфон",
        "компьютер",
        "ноутбук",
        "наушники",
        "зарядка",
        "зарядное устройство",
        "кабель",
        "клавиатура",
        "мышь",
        "монитор",
        "планшет",
    ],

    "transport": [
        
        "metro", "métro",
        "bus",
        "train",
        "taxi",
        "fuel",
        "essence",
        "diesel",
        "gasoline",
        "parking",
        "uber",
        "bolt",
        "ticket transport",
        "transport",
        "peage", "péage",
        "метро",
        "автобус",
        "поезд",
        "такси",
        "бензин",
        "дизель",
        "топливо",
        "парковка",
        "проезд",
        "транспорт",
    ],

    "medicine": [
        
        "medicine",
        "medicament", "médicament",
        "vitamin", "vitamine",
        "pharmacy", "pharmacie",
        "paracetamol", "paracétamol",
        "ibuprofen",
        "ibuprofene", "ibuprofène",
        "aspirin", "aspirine",
        "antibiotic", "antibiotique",

        "лекарство",
        "лекарства",
        "витамин",
        "витамины",
        "аптека",
        "парацетамол",
        "ибупрофен",
        "аспирин",
        "антибиотик",
    ],

    "restaurant": [
        
        "restaurant",
        "restauration",
        "delivery",
        "livraison",
        "takeaway",
        "a emporter",
        "à emporter",
        "fast food",
        "mcdonald",
        "burger king",
        "kfc",
        "subway",

        "ресторан",
        "кафе",
        "доставка",
        "фастфуд",
        "быстрое питание",
    ],
}


def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    text = unicodedata.normalize(
        "NFD",
        text,
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(
        r"[_/\\|]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


NORMALIZED_CATEGORIES = {
    category: [
        normalize_text(keyword)
        for keyword in keywords
    ]
    for category, keywords in CATEGORIES.items()
}


def _contains_keyword(
    text: str,
    keyword: str,
) -> bool:
    if not keyword:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(keyword)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE,
        )
    )


def categorize_item(name: str) -> str:
    normalized = normalize_text(name)

    if not normalized:
        return "other"
    category_order = (
        "beverages",
        "food",
        "medicine",
        "hygiene",
        "clothing",
        "electronics",
        "transport",
        "restaurant",
    )

    for category in category_order:
        for keyword in NORMALIZED_CATEGORIES[
            category
        ]:
            if _contains_keyword(
                normalized,
                keyword,
            ):
                return category

    return "other"


def categorize_items(
    items: list[dict],
) -> list[dict]:
    categorized_items = []

    for item in items:
        categorized_item = item.copy()

        categorized_item["category"] = (
            categorize_item(
                categorized_item.get(
                    "name",
                    "",
                )
            )
        )

        categorized_items.append(
            categorized_item
        )

    return categorized_items