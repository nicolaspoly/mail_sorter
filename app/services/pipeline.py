import joblib
from sentence_transformers import SentenceTransformer

from app.utils.text_utils import process_emails
from app.services.gmail_service import (
    authenticate_gmail,
    get_or_create_label,
    apply_label,
    mark_as_processed
)


# =========================
# MAIN PIPELINE
# =========================
def run_pipeline():

    print("🚀 Starting email processing...\n")

    # ✅ 1. Charger modèle
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    model = joblib.load("app/data/models/email_classifier.joblib")

    # ✅ 2. Connexion Gmail
    service = authenticate_gmail()

    # ✅ 3. Traitement emails (ML)
    results = process_emails(
        model=model,
        embedder=embedder,
        service=service
    )

    # ✅ 4. Labels mapping (perfs)
    label_map = {}

    for email in results:

        category = email["category"]
        message_id = email["message_id"]

        # ✅ créer label si besoin
        if category not in label_map:
            label_map[category] = get_or_create_label(service, category)

        # ✅ appliquer label
        apply_label(service, message_id, label_map[category])

        # ✅ éviter retraitement
        mark_as_processed(service, message_id)

        # ✅ logs
        print(f"✅ {category} → label appliqué")

    print("\n✅ Pipeline terminé")

    return results


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_pipeline()
