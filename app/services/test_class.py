import pandas as pd
import json

# ✅ IMPORT TON CLASSIFIER
from classifier_service import classify_email


# =========================
# 1. LOAD DATA
# =========================
with open("/Users/nicolasjouglet/Downloads/response_1781821630469.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)  # ✅ ICI TU CRÉES df

# nettoyage
df["subject"] = df["subject"].fillna("")
df["body"] = df["body"].fillna("")
df["sender"] = df["sender"].fillna("")

# vérité terrain
df["label"] = df["category"]


# =========================
# 2. RULE PREDICTIONS
# =========================
df["rule_pred"] = df.apply(
    lambda row: classify_email(
        row["subject"],
        row["body"],
        row["sender"]
    ),
    axis=1
)


# =========================
# 3. DISPLAY DIFFS
# =========================
diff_df = df[df["rule_pred"] != df["label"]]

print(f"\n⚠️ Nombre de désaccords RULE vs TRUE : {len(diff_df)}\n")

for i, row in diff_df.iterrows():
    print("===================================")
    print(f"📩 SUBJECT : {row['subject'][:100]}")
    print(f"📨 SENDER  : {row['sender']}")
    print(f"📏 RULE    : {row['rule_pred']}")
    print(f"✅ TRUE    : {row['label']}")
    print("===================================\n")

    input("Appuie sur Entrée pour continuer...")


    # =========================
# NAVIGATION MAIL PAR MAIL
# =========================

for i, row in df.iterrows():
    print("\n===================================")
    print(f"📧 INDEX  : {i}")
    print(f"📩 SUBJECT: {row['subject']}")
    print(f"📨 SENDER : {row['sender']}")
    
    print("\n📝 BODY (début):")
    print(row["body"][:500])  # éviter trop long

    print("\n📊 LABEL ACTUEL :", row["label"])
    print("===================================")

    # ✅ action utilisateur
    action = input("👉 Entrée = suivant | 'edit' pour modifier | 'quit' pour arrêter : ")

    if action == "edit":
        new_label = input("👉 Nouveau label (marketing / social / security / career / other) : ")
        df.at[i, "label"] = new_label
        print("✅ Label mis à jour")

    elif action == "quit":
        break