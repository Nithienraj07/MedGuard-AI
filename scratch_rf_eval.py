import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

df = pd.read_csv('data/processed/engineered_appointments.csv')
y = df['No_Show']
X = df.drop(columns=['No_Show'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

random_forest_model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
random_forest_model.fit(X_train, y_train)

random_forest_y_pred = random_forest_model.predict(X_test)
random_forest_y_prob = random_forest_model.predict_proba(X_test)[:, 1]

accuracy_rf = accuracy_score(y_test, random_forest_y_pred)
precision_rf = precision_score(y_test, random_forest_y_pred, zero_division=0)
recall_rf = recall_score(y_test, random_forest_y_pred, zero_division=0)
f1_rf = f1_score(y_test, random_forest_y_pred, zero_division=0)
roc_auc_rf = roc_auc_score(y_test, random_forest_y_prob)
conf_matrix_rf = confusion_matrix(y_test, random_forest_y_pred)

print("=" * 50)
print("RANDOM FOREST (CLASS-WEIGHTED) EVALUATION")
print("=" * 50)
print(f"Accuracy:  {accuracy_rf:.4f}")
print(f"Precision: {precision_rf:.4f}")
print(f"Recall:    {recall_rf:.4f}")
print(f"F1 Score:  {f1_rf:.4f}")
print(f"ROC-AUC:   {roc_auc_rf:.4f}")
print("\nConfusion Matrix:")
print(conf_matrix_rf)
print("=" * 50)
