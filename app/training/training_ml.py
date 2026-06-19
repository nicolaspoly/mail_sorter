import pandas as pd
import json

# =========================
# 1. LOAD DATASET
# =========================
with open("downloads/cleaned_dataset.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

df["subject"] = df["subject"].fillna("")
df["body"] = df["body"].fillna("")
df["sender"] = df["sender"].fillna("")

df["label"] = df["category"]

# =========================
# 2. FEATURE ENGINEERING
# =========================
df["text"] = (
    df["subject"] + " " +
    df["body"] + " " +
    df["sender"]
)

# =========================
# 3. EMBEDDINGS (🔥 NOUVEAU)
# =========================
from sentence_transformers import SentenceTransformer

print("⏳ Loading model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

print("⏳ Encoding emails...")
X = embedder.encode(
    df["text"].tolist(),
    show_progress_bar=True
)

y = df["label"]

# =========================
# 4. TRAIN / TEST SPLIT
# =========================
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =========================
# 5. MODEL
# =========================
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

print("⏳ Training model...")
model.fit(X_train, y_train)

# =========================
# 6. EVALUATION
# =========================
from sklearn.metrics import classification_report

y_pred = model.predict(X_test)

print("\n📊 Classification report:\n")
print(classification_report(y_test, y_pred))

# =========================
# 7. PREDICTION FUNCTION
# =========================
def predict_email(subject, body, sender):
    text = subject + " " + body + " " + sender

    emb = embedder.encode([text])
    
    proba = model.predict_proba(emb)[0]
    label = model.predict(emb)[0]
    confidence = max(proba)

    return label, confidence

# =========================
# 8. TEST
# =========================
# print("\n🔮 Prediction test:\n")

# label, conf = predict_email(
#     "JUSQU'À -40 % Black Friday",
#     "Profitez de nos offres",
#     "adidas@fr-news.adidas.com"
# )

# print(f"Label: {label} | Confidence: {conf:.2f}")

# # =========================
# # 9. DEBUG DATASET
# # =========================
# print("\n📈 Distribution labels:\n")
# print(df["label"].value_counts())

# # =========================
# # 10. FULL DATASET CHECK
# # =========================

# print("\n🔎 Full dataset verification:\n")

# results = []

# for idx, row in df.iterrows():
#     subject = row["subject"]
#     body = row["body"]
#     sender = row["sender"]
#     true_label = row["label"]

#     pred_label, conf = predict_email(subject, body, sender)

#     results.append({
#         "subject": subject[:60],
#         "true": true_label,
#         "pred": pred_label,
#         "confidence": conf,
#         "correct": true_label == pred_label
#     })

# results_df = pd.DataFrame(results)

# =========================
# 11. STATS
# =========================

# accuracy = results_df["correct"].mean()
# print(f"\n✅ Accuracy (full dataset): {accuracy:.2f}")

# # =========================
# # 12. ERREURS
# # =========================

# errors = results_df[results_df["correct"] == False]

# print(f"\n❌ Nombre d'erreurs: {len(errors)}")

# print("\n🔍 Exemple d'erreurs:\n")
# print(errors.head(10))

# =========================
# 13. ARBITRAGE INTERACTIF
# =========================

def review_errors(errors_df):

    corrected_labels = []

    for idx, row in errors_df.iterrows():

        print("\n----------------------------")
        print(f"Subject: {row['subject']}")
        print(f"TRUE LABEL: {row['true']}")
        print(f"PREDICTED: {row['pred']}")
        print(f"CONFIDENCE: {row['confidence']:.2f}")

        # choix humain
        choice = input("✅ 1 = ML correct | 2 = Dataset correct | 3 = skip : ")

        if choice == "1":
            final_label = row["pred"]  # ML gagne
        elif choice == "2":
            final_label = row["true"]  # dataset garde
        else:
            final_label = row["true"]

        corrected_labels.append(final_label)

    errors_df["final_label"] = corrected_labels

    return errors_df

# =========================
# 14. SAVE MODEL
# =========================

import joblib
import os

os.makedirs("app/data/models", exist_ok=True)

joblib.dump(model, "app/data/models/email_classifier.joblib")

print("✅ Modèle sauvegardé dans app/data/models/")

def predict_email(subject, body, sender,model=model, embedder=embedder):
    text = subject + " " + body + " " + sender

    emb = embedder.encode([text])

    proba = model.predict_proba(emb)[0]
    label = model.predict(emb)[0]
    confidence = max(proba)

    return label, confidence