import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

os.makedirs('model', exist_ok=True)

columns = [
    'duration','protocol_type','service','flag','src_bytes','dst_bytes',
    'land','wrong_fragment','urgent','hot','num_failed_logins','logged_in',
    'num_compromised','root_shell','su_attempted','num_root',
    'num_file_creations','num_shells','num_access_files',
    'num_outbound_cmds','is_host_login','is_guest_login','count',
    'srv_count','serror_rate','srv_serror_rate','rerror_rate',
    'srv_rerror_rate','same_srv_rate','diff_srv_rate',
    'srv_diff_host_rate','dst_host_count','dst_host_srv_count',
    'dst_host_same_srv_rate','dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate',
    'dst_host_serror_rate','dst_host_srv_serror_rate',
    'dst_host_rerror_rate','dst_host_srv_rerror_rate',
    'label','difficulty'
]

print("Loading data...")
df = pd.read_csv('data/kddtrain.csv', header=None, names=columns)

# Drop the difficulty column we dont need it
df = df.drop('difficulty', axis=1)

print("Raw label samples:")
print(df['label'].unique())

print("\nProcessing labels...")
# normal stays normal, everything else is attack
df['label'] = df['label'].apply(
    lambda x: 'normal' if str(x).strip().lower() == 'normal' else 'attack'
)

print("Label counts:")
print(df['label'].value_counts())

print("\nEncoding text columns...")
for col in df.columns:
    if col == 'label':
        continue
    try:
        df[col] = pd.to_numeric(df[col])
    except (ValueError, TypeError):
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str).str.strip())
        joblib.dump(le, f'model/le_{col}.pkl')

# Split features and label
X = df.drop('label', axis=1)
y = df['label']

joblib.dump(list(X.columns), 'model/feature_names.pkl')

print(f"\nDataset shape: {X.shape}")
print(f"Labels: {y.value_counts().to_dict()}")

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\nTraining Random Forest model... please wait 2-3 minutes")
model = RandomForestClassifier(
    n_estimators=100, random_state=42, n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
print("\nDetailed Report:")
print(classification_report(y_test, y_pred))

# Save everything
joblib.dump(model, 'model/ids_model.pkl')
X_test.to_csv('model/X_test.csv', index=False)
y_test.to_csv('model/y_test.csv', index=False)

print("\nModel saved successfully in model/ folder!")
print("Now run: streamlit run dashboard.py")