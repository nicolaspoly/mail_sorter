import re

def extract_domain(sender):
    match = re.search(r'@([a-zA-Z0-9.-]+)', sender)
    return match.group(1).lower() if match else ""


MARKETING_DOMAINS = [
    "adidas.com",
    "fr-news.adidas.com",
    "bcbx.delivery",
    "chess.com",
    "saily.com",
    "fnac.com",
]

SECURITY_DOMAINS = [
    "google.com",
    "accounts.google.com",
    "apple.com",
    "email.apple.com",
    "supercell.com",
]

CAREER_DOMAINS = [
    "indeed.com",
    "linkedin.com"
]

SOCIAL_DOMAINS = [
    "strava.com",
    "inria.fr",
]


# 🔒 SECURITY
SECURITY_STRONG_WORDS = [
    "alerte de sécurité",
    "activité suspecte",
    "nouvelle connexion",
    "tentative de connexion",
    "connexion depuis",
]

SECURITY_CRITICAL_PATTERNS = [
    ("compte", "fermé"),
    ("compte", "suspendu"),
    ("compte", "désactivé"),
    ("accès", "bloqué"),
    ("plus", "connecter"),
]


# 🟡 MARKETING (renforcé ✅)
MARKETING_WORDS = [
    "promo", "offre", "réduction", "%",
    "black friday", "shop", "order",
    "deal", "soldes", "wishlist",
    "jeu", "concours", "gagne", "participer",
    "abonnement", "premium", "réduction", "économisez"
]


# 💼 CAREER
CAREER_STRONG_WORDS = [
    "offre d'emploi",
    "candidature",
    "recrutement",
    "poste à pourvoir",
    "entretien",
]


# 🟣 SOCIAL
SOCIAL_WORDS = [
    "kudos",
    "challenge",
    "activity",
    "notification",
    "forum",
]



def classify_email(subject, body, sender):
    text = (subject + " " + body).lower()
    domain = extract_domain(sender)

    sender_lower = sender.lower()

    # ✅ 🔥 PRIORITÉ MAX : TES MAILS
    if "n.jouglet23@gmail.com" in sender_lower:
        return "other"


    # 🔴 1. SECURITY
    if any(d in domain for d in SECURITY_DOMAINS):
        return "security"

    if any(k in text for k in SECURITY_STRONG_WORDS):
        return "security"

    for w1, w2 in SECURITY_CRITICAL_PATTERNS:
        if w1 in text and w2 in text:
            return "security"


    # 💼 2. CAREER
    if any(d in domain for d in CAREER_DOMAINS):
        return "career"

    if any(k in text for k in CAREER_STRONG_WORDS):
        return "career"


    # 🟡 3. MARKETING ✅ (avant social)
    if any(d in domain for d in MARKETING_DOMAINS):
        return "marketing"

    if any(k in text for k in MARKETING_WORDS):
        return "marketing"


    # 🟣 4. SOCIAL
    if any(d in domain for d in SOCIAL_DOMAINS):
        return "social"

    if any(k in text for k in SOCIAL_WORDS):
        return "social"


    return "other"

from app.services.gmail_service import authenticate_gmail
from app.utils.text_utils import fetch_emails_gmail
from app.services.classifier_service import classify_email


def classify_emails():

    # ✅ connecter une seule fois
    service = authenticate_gmail()

    emails = fetch_emails_gmail(service=service)

    results = []

    for email in emails:

        category = classify_email(
            email["subject"],
            email["body"],
            email["sender"]
        )

        results.append({
            "subject": email["subject"],
            "category": category,
            "message_id": email["message_id"]  # 🔥 important pour Gmail actions
        })

    return results