from fastapi import APIRouter
from app.services.email_service import fetch_emails

router = APIRouter()

@router.get("/emails")
def get_emails():
    print("🔥 endpoint /emails called")
    return fetch_emails()

from app.services.classification_pipeline import classify_emails


@router.get("/classify-emails")
def classify():
    return classify_emails()

from app.services.process_pipeline import process_emails

@router.post("/process-emails")
def process():
    return process_emails()
