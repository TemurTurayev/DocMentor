"""
Medical Terms Database for DocMentor TREAD optimization.
Contains weighted medical terminology for prioritization in token processing.
"""

# Russian Medical Terms (Русские медицинские термины)
MEDICAL_TERMS_RU = {
    # Анатомия (Anatomy)
    "anatomy": [
        "сердце", "легкие", "печень", "почки", "селезенка",
        "желудок", "кишечник", "поджелудочная", "желчный пузырь",
        "головной мозг", "спинной мозг", "нервы", "артерии", "вены",
        "лимфатические узлы", "костный мозг", "суставы", "мышцы",
        "щитовидная железа", "надпочечники", "гипофиз"
    ],

    # Системы органов (Organ Systems)
    "organ_systems": [
        "сердечно-сосудистая система", "дыхательная система",
        "пищеварительная система", "мочевыделительная система",
        "нервная система", "эндокринная система",
        "иммунная система", "опорно-двигательный аппарат",
        "репродуктивная система", "кожа и придатки"
    ],

    # Симптомы (Symptoms)
    "symptoms": [
        "боль", "лихорадка", "кашель", "одышка", "тошнота",
        "рвота", "диарея", "запор", "головная боль", "головокружение",
        "слабость", "усталость", "потеря веса", "потеря аппетита",
        "отеки", "сыпь", "зуд", "кровотечение", "синяки"
    ],

    # Патология (Pathology)
    "diseases": [
        # Сердечно-сосудистые
        "гипертония", "гипотония", "инфаркт миокарда", "стенокардия",
        "аритмия", "сердечная недостаточность", "инсульт",
        "атеросклероз", "тромбоз", "эмболия",

        # Респираторные
        "астма", "бронхит", "пневмония", "ХОБЛ", "туберкулез",
        "плеврит", "эмфизема", "пневмоторакс",

        # Желудочно-кишечные
        "гастрит", "язва", "панкреатит", "холецистит",
        "аппендицит", "колит", "гепатит", "цирроз",

        # Эндокринные
        "диабет", "тиреотоксикоз", "гипотиреоз",
        "синдром Кушинга", "акромегалия",

        # Неврологические
        "менингит", "энцефалит", "эпилепсия", "болезнь Паркинсона",
        "болезнь Альцгеймера", "рассеянный склероз",

        # Почечные
        "пиелонефрит", "гломерулонефрит", "почечная недостаточность",
        "мочекаменная болезнь"
    ],

    # Диагностические процедуры (Diagnostic Procedures)
    "diagnostics": [
        "анализ крови", "анализ мочи", "биохимия", "ЭКГ", "ЭХО-КГ",
        "рентген", "УЗИ", "КТ", "МРТ", "эндоскопия",
        "биопсия", "пункция", "спирометрия", "холтер"
    ],

    # Лекарственные препараты (Medications)
    "medications": [
        "антибиотики", "анальгетики", "жаропонижающие",
        "антигипертензивные", "диуретики", "бета-блокаторы",
        "ингибиторы АПФ", "антикоагулянты", "антиагреганты",
        "статины", "инсулин", "гормоны", "витамины",
        "антигистаминные", "бронходилататоры", "глюкокортикостероиды"
    ],

    # Лабораторные показатели (Lab Values)
    "lab_values": [
        "гемоглобин", "эритроциты", "лейкоциты", "тромбоциты",
        "СОЭ", "глюкоза", "креатинин", "мочевина", "билирубин",
        "АЛТ", "АСТ", "холестерин", "триглицериды",
        "калий", "натрий", "кальций", "железо"
    ],

    # Медицинские процедуры (Medical Procedures)
    "procedures": [
        "операция", "хирургия", "анестезия", "интубация",
        "катетеризация", "дренирование", "трахеостомия",
        "переливание крови", "диализ", "химиотерапия",
        "лучевая терапия", "физиотерапия"
    ]
}

# English Medical Terms
MEDICAL_TERMS_EN = {
    "anatomy": [
        "heart", "lungs", "liver", "kidneys", "spleen",
        "stomach", "intestine", "pancreas", "gallbladder",
        "brain", "spinal cord", "nerves", "arteries", "veins"
    ],

    "symptoms": [
        "pain", "fever", "cough", "dyspnea", "nausea",
        "vomiting", "diarrhea", "constipation", "headache",
        "dizziness", "weakness", "fatigue", "weight loss"
    ],

    "diseases": [
        "hypertension", "hypotension", "myocardial infarction",
        "angina", "arrhythmia", "heart failure", "stroke",
        "asthma", "bronchitis", "pneumonia", "COPD",
        "diabetes", "hyperthyroidism", "hypothyroidism"
    ],

    "diagnostics": [
        "blood test", "urinalysis", "ECG", "echocardiography",
        "X-ray", "ultrasound", "CT scan", "MRI", "endoscopy"
    ],

    "medications": [
        "antibiotics", "analgesics", "antipyretics",
        "antihypertensives", "diuretics", "beta-blockers",
        "ACE inhibitors", "anticoagulants", "statins", "insulin"
    ]
}

# Uzbek Medical Terms (O'zbek tibbiy atamalar)
MEDICAL_TERMS_UZ = {
    "anatomy": [
        "yurak", "o'pka", "jigar", "buyrak", "taloq",
        "oshqozon", "ichak", "oshqozon osti bezi",
        "bosh miya", "orqa miya", "asab", "arteriya", "vena"
    ],

    "symptoms": [
        "og'riq", "isitma", "yo'tal", "nafas qisilishi",
        "ko'ngil aynish", "qusish", "ich ketish",
        "bosh og'rig'i", "zaiflik", "holsizlik"
    ],

    "diseases": [
        "gipertoniya", "yurak xuruji", "astma", "bronxit",
        "pnevmoniya", "diabet", "gepatit", "gastrit"
    ]
}

# Term weights for TREAD optimization
# Higher weights = higher priority in token routing
TERM_WEIGHTS = {
    "critical_symptoms": 1.5,  # Life-threatening symptoms
    "diseases": 1.3,           # Disease names
    "anatomy": 1.2,            # Anatomical terms
    "diagnostics": 1.2,        # Diagnostic procedures
    "medications": 1.1,        # Medications
    "symptoms": 1.1,           # General symptoms
    "lab_values": 1.0,         # Lab values
    "procedures": 1.0          # Medical procedures
}

# Critical medical terms that should always be prioritized
CRITICAL_TERMS = [
    # Russian
    "инфаркт", "инсульт", "остановка сердца", "анафилаксия",
    "кровотечение", "шок", "кома", "судороги", "асфиксия",
    "отек Квинке", "тромбоэмболия", "инфаркт миокарда",

    # English
    "cardiac arrest", "stroke", "anaphylaxis", "hemorrhage",
    "shock", "coma", "seizures", "asphyxia", "pulmonary embolism",

    # Uzbek
    "yurak xuruji", "qon ketish", "shok", "koma"
]


def get_all_terms(language="ru"):
    """
    Get all medical terms for a specific language.

    Args:
        language: Language code ('ru', 'en', 'uz')

    Returns:
        Set of all medical terms
    """
    if language == "ru":
        terms_dict = MEDICAL_TERMS_RU
    elif language == "en":
        terms_dict = MEDICAL_TERMS_EN
    elif language == "uz":
        terms_dict = MEDICAL_TERMS_UZ
    else:
        raise ValueError(f"Unsupported language: {language}")

    all_terms = set()
    for category_terms in terms_dict.values():
        all_terms.update(category_terms)

    return all_terms


def get_term_weight(term, category=None):
    """
    Get the weight/priority for a specific medical term.

    Args:
        term: Medical term
        category: Optional category of the term

    Returns:
        Weight value (float)
    """
    # Critical terms get highest weight
    if term.lower() in [t.lower() for t in CRITICAL_TERMS]:
        return 2.0

    # Category-based weights
    if category and category in TERM_WEIGHTS:
        return TERM_WEIGHTS[category]

    # Default weight for medical terms
    return 1.0


def is_medical_term(text, language="ru"):
    """
    Check if a text contains medical terminology.

    Args:
        text: Text to check
        language: Language code

    Returns:
        Boolean indicating if text contains medical terms
    """
    text_lower = text.lower()
    terms = get_all_terms(language)

    for term in terms:
        if term.lower() in text_lower:
            return True

    return False


def extract_medical_terms(text, language="ru"):
    """
    Extract medical terms from text.

    Args:
        text: Input text
        language: Language code

    Returns:
        List of found medical terms with their categories
    """
    text_lower = text.lower()
    found_terms = []

    if language == "ru":
        terms_dict = MEDICAL_TERMS_RU
    elif language == "en":
        terms_dict = MEDICAL_TERMS_EN
    elif language == "uz":
        terms_dict = MEDICAL_TERMS_UZ
    else:
        return found_terms

    for category, terms in terms_dict.items():
        for term in terms:
            if term.lower() in text_lower:
                found_terms.append({
                    "term": term,
                    "category": category,
                    "weight": get_term_weight(term, category)
                })

    return found_terms


# Usage example:
if __name__ == "__main__":
    # Test the medical terms database
    print("=== Medical Terms Database Test ===\n")

    # Test Russian terms
    text_ru = "Пациент жалуется на боль в области сердца, одышку и повышенное давление."
    terms_ru = extract_medical_terms(text_ru, "ru")
    print(f"Russian text: {text_ru}")
    print(f"Found terms: {terms_ru}\n")

    # Test English terms
    text_en = "Patient presents with chest pain, dyspnea, and hypertension."
    terms_en = extract_medical_terms(text_en, "en")
    print(f"English text: {text_en}")
    print(f"Found terms: {terms_en}\n")

    # Test critical terms
    critical_text = "Suspected myocardial infarction with cardiac arrest."
    is_critical = any(term in critical_text.lower() for term in [t.lower() for t in CRITICAL_TERMS])
    print(f"Critical text: {critical_text}")
    print(f"Contains critical terms: {is_critical}")
