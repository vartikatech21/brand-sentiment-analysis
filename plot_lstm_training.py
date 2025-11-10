# plot_lstm_training.py
import pickle
import matplotlib.pyplot as plt
import os

# Path to the saved history file
history_path = "backend/lstm_history.pkl"

# Check if file exists
if not os.path.exists(history_path):
    raise FileNotFoundError(f"⚠️ Could not find {history_path}. "
                            "Make sure you saved training history using train_lstm().")

# Load training history
with open(history_path, "rb") as f:
    history = pickle.load(f)

# Print available keys (optional)
print("✅ Loaded training history keys:", list(history.keys()))

# Plot setup
plt.figure(figsize=(10, 4))

# -------------------------
# Accuracy Plot
# -------------------------
plt.subplot(1, 2, 1)
plt.plot(history.get('accuracy', []), 'b-', label='Training Accuracy')
plt.plot(history.get('val_accuracy', []), 'r-', label='Validation Accuracy')
plt.title('📈 LSTM Model Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

# -------------------------
# Loss Plot
# -------------------------
plt.subplot(1, 2, 2)
plt.plot(history.get('loss', []), 'b--', label='Training Loss')
plt.plot(history.get('val_loss', []), 'r--', label='Validation Loss')
plt.title('📉 LSTM Model Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
