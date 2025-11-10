import pandas as pd
from pathlib import Path
from backend.preprocess import clean_texts
from backend.sentiment import SentimentAnalyzer

CSV_PATH = Path("data/offline_sample.csv")

def load_texts(path: Path):
    try:
        # Try normal CSV parse; skip malformed lines instead of crashing
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
        # If your CSV has a dedicated 'text' column, prefer it
        if "text" in df.columns:
            return df["text"].astype(str).tolist()
        # If it has exactly one column, use that column as text
        if len(df.columns) == 1:
            return df.iloc[:, 0].astype(str).tolist()
        # Otherwise, join multiple columns into a single text string
        return df.astype(str).agg(" ".join, axis=1).tolist()
    except pd.errors.ParserError:
        # Fallback: treat file as plain text (one sample per line)
        with open(path, encoding="utf-8", errors="ignore") as f:
            return [ln.strip() for ln in f if ln.strip()]

texts = load_texts(CSV_PATH)

# --- your existing evaluation code below ---
texts_clean = clean_texts(texts)

# choose model you want to try
analyzer = SentimentAnalyzer(
    mode="ml",
    ml_model_path="backend/tfidf_linear_svc.joblib",
    vectorizer_path="backend/tfidf_vectorizer.joblib",
)
# or: analyzer = SentimentAnalyzer(mode="lexicon")
# or: analyzer = SentimentAnalyzer(mode="lstm", lstm_model_path="backend/lstm_model.h5",
#                                  lstm_tokenizer_path="backend/tokenizer.pkl")

preds = analyzer.predict(texts_clean)

out = pd.DataFrame({
    "text": texts,
    "clean": texts_clean,
    "prediction": preds
})
out.to_csv("data/offline_predictions.csv", index=False)
print("Saved -> data/offline_predictions.csv")
print(out.head(10))
