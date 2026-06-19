import pandas as pd
import json

# ✅ IMPORTS
from app.services.classifier_service import classify_email
from app.services.email_classifier_ml import predict_email  # ton modèle transformers

# =========================
# 1. LOAD DATA
# =========================
with open("/Users/nicolasjouglet/Downloads/response_1781821630469.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

df["subject"] = df["subject"].fillna("")
df["body"] = df["body"].fillna("")
df["sender"] = df["sender"].fillna("")
df["label"] = df["category"]

# =========================
# 2. PREDICTIONS
# =========================

print("⏳ Génération des prédictions...")

df["rule_pred"] = df.apply(
    lambda row: classify_email(
        row["subject"],
        row["body"],
        row["sender"]
    ),
    axis=1
)

df["ml_pred"], df["ml_conf"] = zip(*df.apply(
    lambda row: predict_email(
        row["subject"],
        row["body"],
        row["sender"]
    ),
    axis=1
))

# =========================
# 3. FILTRAGE INTELLIGENT
# =========================

# 👉 cas problématiques :
review_df = df[
    (df["rule_pred"] != df["label"]) |
    (df["ml_pred"] != df["label"]) 
 #   (df["ml_conf"] < 0.6)
]

print(f"\n⚠️ Éléments à reviewer : {len(review_df)}")

# =========================
# 4. BOUCLE INTERACTIVE
# =========================

for i, row in review_df.iterrows():

    print("\n===================================")
    print(f"📧 INDEX   : {i}")
    print(f"📩 SUBJECT : {row['subject']}")
    print(f"📨 SENDER  : {row['sender']}")

    print("\n📝 BODY (début):")
    print(row["body"][:400])

    print("\n---")
    print(f"✅ TRUE LABEL : {row['label']}")
    print(f"📏 RULE       : {row['rule_pred']}")
    print(f"🤖 ML         : {row['ml_pred']} ({row['ml_conf']:.2f})")
    print("---")

    print("""
Choix :
1 → garder label (dataset correct)
2 → utiliser RULE
3 → utiliser ML
4 → saisir manuellement
(skip → Entrée)
(q → quit)
""")

    action = input("👉 Ton choix : ").strip()

    if action == "1":
        continue

    elif action == "2":
        df.at[i, "label"] = row["rule_pred"]
        print("✅ corrigé via RULE")

    elif action == "3":
        df.at[i, "label"] = row["ml_pred"]
        print("✅ corrigé via ML")

    elif action == "4":
        new_label = input("👉 nouveau label : ")
        df.at[i, "label"] = new_label
        print("✅ corrigé manuellement")

    elif action == "q":
        break

# =========================
# 5. SAVE DATASET
# =========================

df.to_json("cleaned_dataset.json", orient="records", indent=2)

print("\n✅ Dataset sauvegardé : cleaned_dataset.json")
