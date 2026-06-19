from email.message import EmailMessage
from app.services.email_service import extract_body, extract_attachments


def test_full_pipeline(tmp_path):
    # créer email fake
    msg = EmailMessage()
    msg["Subject"] = "Invoice Amazon"
    msg.set_content("Your payment receipt")

    # ajouter pièce jointe
    msg.add_attachment(
        b"fake pdf content",
        maintype="application",
        subtype="pdf",
        filename="invoice.pdf"
    )

    # extraction
    body = extract_body(msg)
    attachments = extract_attachments(msg)

    # classification

    # assertions
    assert "payment" in body.lower()
    assert len(attachments) == 1
