from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "customer_features.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "churn_model.pkl"

def train_model():
    print("Loading customer features...")
    if not FEATURES_PATH.exists():
        raise FileNotFoundError(f"Features not found at {FEATURES_PATH}. Run build_features.py first.")
    
    df = pd.read_csv(FEATURES_PATH)
    
    feature_cols = ["recency_days", "frequency", "monetary", "avg_basket_size", "avg_item_price"]
    X = df[feature_cols]
    y = df["churn"]
    
    print(f"Total samples: {len(df)}, Unique churn classes present: {y.unique().tolist()}")
    
    # Safety fallback: If only 1 class is present, inject multiple dummy rows of the opposite class
    if len(y.unique()) < 2:
        print("Warning: Only one churn class detected. Adding sample balance padding for demo model training...")
        opposite_class = 1 if y.iloc[0] == 0 else 0
        # Create 5 dummy rows of the opposite class so split succeeds
        dummy_df = pd.DataFrame([X.iloc[0]] * 5)
        dummy_df["churn"] = opposite_class
        df = pd.concat([df, dummy_df], ignore_index=True)
        X = df[feature_cols]
        y = df["churn"]

    # Check class counts to determine if stratification is possible
    class_counts = y.value_counts()
    can_stratify = all(count >= 2 for count in class_counts)

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if can_stratify else None
    )
    
    print(f"Training set shape: {X_train.shape}")
    print(f"Test set shape: {X_test.shape}")
    
    # Initialize and Train Random Forest Classifier
    print("\nTraining Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    print("\n--- Model Evaluation Report ---")
    try:
        print(classification_report(y_test, y_pred, zero_division=0))
        if len(y.unique()) > 1 and len(set(y_test)) > 1:
            y_prob = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_prob)
            print(f"ROC-AUC Score: {roc_auc:.4f}")
    except Exception as e:
        print(f"Metrics warning: {e}")
    
    # Save Model Artifact
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": model,
        "feature_cols": feature_cols
    }, MODEL_PATH)
    
    print(f"\nModel successfully saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()