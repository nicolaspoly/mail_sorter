import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os
import re
from dotenv import load_dotenv
import joblib
from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer
load_dotenv()

# ==========================================================
# ✅ HEADER DECODING (ULTRA ROBUSTE)
# ==========================================================

def decode_email_header(value):
    if not value:
        return ""

    parts = decode_header(value)
    result = ""

    for part, encoding in parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(encoding or "utf-8", errors="ignore")
            except:
                result += part.decode("utf-8", errors="ignore")
        else:
            result += part

    return clean_unicode(result)


# ==========================================================
# ✅ UNICODE CLEAN (CRITIQUE)
# ==========================================================

def clean_unicode(text):
    if not text:
        return ""

    return str(text).encode("utf-8", "ignore").decode("utf-8", "ignore")


# ==========================================================
# ✅ BODY EXTRACTION + CLEAN
# ==========================================================

def extract_body(msg):
    html = None
    text = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode("utf-8", errors="ignore")

            elif content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    text = payload.decode("utf-8", errors="ignore")

    else:
        payload = msg.get_payload(decode=True)
        if payload:
            text = payload.decode("utf-8", errors="ignore")

    # ✅ priorité au HTML nettoyé
    if html:
        return clean_body(html)

    return clean_body(text)


from bs4 import BeautifulSoup
import re

def clean_body(html):
    if not html:
        return ""

    # ✅ parser HTML correctement
    soup = BeautifulSoup(html, "html.parser")

    # ✅ supprimer scripts + styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # ✅ récupérer texte visible
    text = soup.get_text(separator=" ")

    # ✅ fix unicode
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")

    # ✅ supprimer URLs
    text = re.sub(r"http\S+", "", text)

    # ✅ supprimer footer typiques
    text = re.sub(r"(unsubscribe|se désabonner|voir en ligne).*", "", text, flags=re.IGNORECASE)

    # ✅ nettoyer espaces
    text = re.sub(r"\s+", " ", text)

    # ✅ limiter taille
    return text.strip()[:2000]


# ==========================================================
# ✅ DOMAIN EXTRACTION
# ==========================================================

def extract_domain(sender):
    if not sender:
        return "unknown"

    sender = str(sender)

    match = re.search(r'@([\w\.-]+)', sender)
    if match:
        return match.group(1).lower()

    return "unknown"


# ==========================================================
# ✅ ATTACHMENTS
# ==========================================================

def extract_attachments(msg, download_dir="downloads"):
    attachments = []
    os.makedirs(download_dir, exist_ok=True)

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))

        if "attachment" in content_disposition:
            filename = part.get_filename()

            if filename:
                filename = clean_unicode(filename)
                filepath = os.path.join(download_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))

                attachments.append(filepath)

    return attachments


# ==========================================================
# ✅ FETCH EMAILS (ROBUSTE)
# ==========================================================
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def fetch_emails_gmail(service, num_emails=10):

    results = service.users().messages().list(
        userId='me',
        maxResults=num_emails
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for m in messages:

        msg_id = m["id"]

        full_msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()

        headers = full_msg["payload"]["headers"]

        subject = ""
        sender = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]

        body = full_msg.get("snippet", "")

        emails.append({
            "subject": subject,
            "body": body,
            "sender": sender,
            "attachments": [],  # simplifié pour l'instant
            "message_id": msg_id  # ✅ ID CORRECT
        })

    return emails


# ==========================================================
# ✅ SAFE JSON (ANTI CRASH FASTAPI)
# ==========================================================

def safe_json(data):
    import json
    return json.loads(json.dumps(data, ensure_ascii=False))


# ==========================================================
# ✅ SAVE JSON
# ==========================================================

import json
from datetime import datetime

def save_to_json(data, output_dir="downloads"):

    os.makedirs(output_dir, exist_ok=True)

    # nom fichier avec timestamp (évite overwrite)
    filename = f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ JSON sauvegardé : {filepath}")

    return filepath


if __name__ == "__main__":
    emails = fetch_emails_gmail()

    # optionnel : sécuriser données
    emails = safe_json(emails)

    save_to_json(emails)



from app.services.classifier_service import classify_email
from app.services.file_service import move_file 

def predict_email(subject, body, sender, model=None, embedder=None):
    text = subject + " " + body + " " + sender

    emb = embedder.encode([text])
    
    proba = model.predict_proba(emb)[0]
    label = model.predict(emb)[0]
    confidence = max(proba)

    return label, confidence


import json

def process_emails(num_emails=50, model=None, embedder=None,service=None):

    # lazy loading (propre)
    if model is None or embedder is None:
        from sentence_transformers import SentenceTransformer
        import joblib

        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        model = joblib.load("app/data/models/email_classifier.joblib")

    emails = fetch_emails_gmail(service, num_emails=num_emails)

    results = []

    for email in emails:
        subject = email["subject"]
        body = email["body"]
        attachments = email["attachments"]
        sender = email["sender"]

        category, confidence = predict_email(
            subject, body, sender, model, embedder
        )

        moved_files = []

        for file in attachments:
            new_path = move_file(file, category)
            moved_files.append(new_path)

        results.append({
            "subject": decode_email_header(subject),
            "body": body,
            "category": category,
            "confidence": float(confidence),  # ✅ JSON safe
            "files": moved_files,
            "sender": decode_email_header(sender),
            "message_id": email["message_id"]  # 🔥 IMPORTANT
        })

    # ✅ conversion JSON directe
    return results
