from app.services.classifier_service import classify_email
from app.services.email_service import fetch_emails


def classify_emails():
    emails = fetch_emails()

    results = []

    for email in emails:
        category = classify_email(email["subject"], email["body"], email["sender"])

        results.append({
            "subject": email["subject"],
            "category": category
        })

    return results