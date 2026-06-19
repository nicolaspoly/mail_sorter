import pandas as pd
import json

# =========================
# 1. LOAD DATASET
# =========================
with open("/Users/nicolasjouglet/Downloads/response_1781821630469.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# nettoyage
df["subject"] = df["subject"].fillna("")
df["body"] = df["body"].fillna("")
df["sender"] = df["sender"].fillna("")

# ✅ utiliser les labels existants
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
# 3. VECTORIZATION
# =========================
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),  # 🔥 amélioration majeure
    stop_words="english"
)

X = vectorizer.fit_transform(df["text"])
y = df["label"]


# =========================
# 4. TRAIN / TEST SPLIT
# =========================
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y   # ✅ important pour équilibre
)


# =========================
# 5. MODEL
# =========================
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"  # ✅ améliore les classes rares
)

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
    X_new = vectorizer.transform([text])
    return model.predict(X_new)[0]


print("\n🔮 Prediction test:\n")

print(predict_email(
    "JUSQU'À -40 % Black Friday",
    "Profitez de nos offres",
    "adidas@fr-news.adidas.com"
))


# =========================
# 8. DEBUG DATASET
# =========================
print("\n📈 Distribution labels:\n")
print(df["label"].value_counts())