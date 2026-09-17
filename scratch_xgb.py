import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

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

print("XGBoost Baseline model successfully trained!")
print("Hard predictions and probability scores successfully generated!")
