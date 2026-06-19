from app.services.email_service import fetch_emails,decode_email_header
from app.services.classifier_service import classify_email
from app.services.file_service import move_file 


def process_emails():
    emails = fetch_emails()

    results = []

    for email in emails:
        subject = email["subject"]
        body = email["body"]
        attachments = email["attachments"]
        sender = email["sender"]
        category = classify_email(subject, body,sender)

        moved_files = []

        for file in attachments:
            new_path = move_file(file, category)
            moved_files.append(new_path)

        results.append({
            "subject": decode_email_header(subject),
            "body": body,
            "category": category,
            "files": moved_files,
            "sender": decode_email_header(sender)
        })

    return results
