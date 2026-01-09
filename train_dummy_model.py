import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import random

# Define features
features = ['mean_val', 'std_val', 'peak_amp', 'heart_rate', 'rr_var', 'entropy']

# Generate synthetic data
n_samples = 1000
data = []
labels = []

for _ in range(n_samples):
    # Simulate features
    mean_val = random.uniform(400, 600)
    std_val = random.uniform(10, 50)
    peak_amp = random.uniform(50, 150)
    heart_rate = random.uniform(60, 120)
    rr_var = random.uniform(20, 100)
    entropy = random.uniform(0.5, 2.0)
    
    # Simple logic for labels
    if heart_rate > 100 or std_val > 40:
        label = "anxiety"
    elif heart_rate > 85 or std_val > 30:
        label = "stress"
    else:
        label = "normal"
        
    data.append([mean_val, std_val, peak_amp, heart_rate, rr_var, entropy])
    labels.append(label)

df = pd.DataFrame(data, columns=features)

# Train model
print("Training dummy model...")
clf = RandomForestClassifier(n_estimators=10, random_state=42)
clf.fit(df, labels)

# Save model
print("Saving model to stress_rf_model.pkl...")
joblib.dump(clf, 'stress_rf_model.pkl')
print("✅ Model saved successfully!")
