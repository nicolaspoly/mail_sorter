import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# =========================
# AUTH
# =========================
def authenticate_gmail():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


# =========================
# LABELS
# =========================
def get_or_create_label(service, label_name):
    labels = service.users().labels().list(userId='me').execute()

    for label in labels['labels']:
        if label['name'] == label_name:
            return label['id']

    new_label = service.users().labels().create(
        userId='me',
        body={"name": label_name}
    ).execute()

    return new_label['id']


# =========================
# APPLY LABEL
# =========================
def apply_label(service, message_id, label_id):
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={"addLabelIds": [label_id]}
        ).execute()
    except Exception as e:
        print(f"⚠️ Erreur label mail {message_id}: {e}")


# =========================
# MARK PROCESSED
# =========================
def mark_as_processed(service, message_id):
    label_id = get_or_create_label(service, "processed")
    apply_label(service, message_id, label_id)