import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
import pandas as pd
from backend.preprocess import clean_text

# --- Load data again ---
from backend.model_train import load_and_merge
data = load_and_merge()

# Split dataset
X = data["text"].values
y = data["label"].values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Load trained TF-IDF and SVC models
vectorizer = joblib.load("backend/tfidf_vectorizer.joblib")
clf = joblib.load("backend/tfidf_linear_svc.joblib")

# Transform test data
X_test_vec = vectorizer.transform(X_test)
y_pred = clf.predict(X_test_vec)

# --- Classification Report ---
report = classification_report(y_test, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()

# --- Plot metrics ---
plt.figure(figsize=(8, 5))
metrics = ['precision', 'recall', 'f1-score']
classes = ['-1 (Negative)', '0 (Neutral)', '1 (Positive)']

for i, metric in enumerate(metrics):
    plt.bar([x + i*0.25 for x in range(3)],
            report_df.loc[['-1','0','1'], metric],
            width=0.25, label=metric.capitalize())

plt.xticks([r + 0.25 for r in range(3)], classes)
plt.title("Linear SVC Performance Metrics")
plt.ylabel("Score")
plt.ylim(0, 1)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# --- Confusion Matrix (optional) ---
cm = confusion_matrix(y_test, y_pred, labels=[-1,0,1])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Negative','Neutral','Positive'])
disp.plot(cmap='Blues', values_format='d')
plt.title("Linear SVC Confusion Matrix")
plt.show()
