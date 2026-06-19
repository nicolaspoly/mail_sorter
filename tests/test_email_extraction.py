from email.message import EmailMessage
from app.services.email_service import extract_body


def test_extract_body_simple():
    msg = EmailMessage()
    msg.set_content("Hello world")

    body = extract_body(msg)

    assert "Hello world" in body

def test_extract_body_multipart():
    msg = EmailMessage()
    msg.set_content("Plain text version")
    msg.add_alternative("<p>HTML version</p>", subtype="html")

    body = extract_body(msg)

    assert "Plain text version" in body

import os
from email.message import EmailMessage
from app.services.email_service import extract_attachments


def test_extract_attachments(tmp_path):
    msg = EmailMessage()
    msg.set_content("Test email")

    # ajouter une pièce jointe
    msg.add_attachment(
        b"fake content",
        maintype="application",
        subtype="octet-stream",
        filename="test.txt"
    )

    # override dossier downloads temporairement
    os.makedirs("downloads", exist_ok=True)

    attachments = extract_attachments(msg)

    assert len(attachments) == 1
    assert os.path.exists(attachments[0])

def test_extract_attachments_cleanup(tmp_path):
    msg = EmailMessage()
    msg.set_content("Test")

    msg.add_attachment(
        b"data",
        maintype="application",
        subtype="octet-stream",
        filename="file.txt"
    )

    attachments = extract_attachments(msg)

    assert len(attachments) == 1

    # cleanup
    for f in attachments:
        os.remove(f)