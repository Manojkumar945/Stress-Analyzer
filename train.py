# =============================================
#  Stress Level Detection using Random Forest
# =============================================

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# 1️⃣ Load Dataset
df = pd.read_csv("stress_ecg_dataset.csv")
print("Dataset shape:", df.shape)
print(df.head())

# 2️⃣ Split Features and Labels
X = df.drop("label", axis=1)
y = df["label"]

# 3️⃣ Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4️⃣ Train Random Forest Model
model = RandomForestClassifier(
    n_estimators=200,      # number of trees
    max_depth=10,          # limit depth to avoid overfitting
    random_state=42
)
model.fit(X_train, y_train)

# 5️⃣ Predictions
y_pred = model.predict(X_test)

# 6️⃣ Evaluation
print("\n📊 Classification Report:\n", classification_report(y_test, y_pred))
print("✅ Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2), "%")

# 7️⃣ Confusion Matrix
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues',
            xticklabels=model.classes_, yticklabels=model.classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# 8️⃣ Feature Importance
importances = pd.Series(model.feature_importances_, index=X.columns)
importances.sort_values().plot(kind='barh', figsize=(8, 5), title="Feature Importance")
plt.show()

import joblib
joblib.dump(model, "stress_rf_model.pkl")

