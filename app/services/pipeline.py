import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os
import re
from app.utils.text_utils import fetch_emails, process_emails

###################
# IMPORT DATA
###################

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

###################
# IMPORT MODEL
###################
import joblib
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
model = joblib.load("app/data/models/email_classifier.joblib")


results = process_emails(model=model, embedder=embedder)
