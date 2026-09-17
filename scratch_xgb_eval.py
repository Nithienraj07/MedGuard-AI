import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

df = pd.read_csv('data/processed/engineered_appointments.csv')
y = df['No_Show']
X = df.drop(columns=['No_Show'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

num_show = (y_train == 0).sum()
num_noshow = (y_train == 1).sum()
scale_pos_weight_value = num_show / num_noshow

xgboost_model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight_value,
    random_state=42,
    eval_metric="logloss"
)

xgboost_model.fit(X_train, y_train)

xgboost_y_pred = xgboost_model.predict(X_test)
xgboost_y_prob = xgboost_model.predict_proba(X_test)[:, 1]

accuracy_xgb = accuracy_score(y_test, xgboost_y_pred)
precision_xgb = precision_score(y_test, xgboost_y_pred, zero_division=0)
recall_xgb = recall_score(y_test, xgboost_y_pred, zero_division=0)
f1_xgb = f1_score(y_test, xgboost_y_pred, zero_division=0)
roc_auc_xgb = roc_auc_score(y_test, xgboost_y_prob)
conf_matrix_xgb = confusion_matrix(y_test, xgboost_y_pred)

print("=" * 50)
print("XGBOOST BASELINE EVALUATION")
print("=" * 50)
print(f"Accuracy:  {accuracy_xgb:.4f}")
print(f"Precision: {precision_xgb:.4f}")
print(f"Recall:    {recall_xgb:.4f}")
print(f"F1 Score:  {f1_xgb:.4f}")
print(f"ROC-AUC:   {roc_auc_xgb:.4f}")
print("\nConfusion Matrix:")
print(conf_matrix_xgb)
print("=" * 50)
