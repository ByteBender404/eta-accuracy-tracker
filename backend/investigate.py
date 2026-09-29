import joblib
import pandas as pd
import numpy as np

# Load model
model = joblib.load("ml_model.pkl")

# Extract components
preprocessor = model.named_steps['preprocessor']
regressor = model.named_steps['regressor']

# Get feature names
num_cols = preprocessor.transformers_[0][2]
cat_cols = preprocessor.transformers_[1][2]
ohe = preprocessor.transformers_[1][1]

# In newer sklearn, get_feature_names_out can be used directly
try:
    cat_feature_names = ohe.get_feature_names_out(cat_cols)
    feature_names = num_cols + list(cat_feature_names)
except AttributeError:
    # Fallback for older sklearn
    cat_feature_names = ohe.get_feature_names(cat_cols)
    feature_names = num_cols + list(cat_feature_names)

# Get importances
importances = regressor.feature_importances_

# Create a dataframe
df_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
df_imp = df_imp.sort_values('Importance', ascending=False).head(10)

print("\n--- Top 10 Feature Importances ---")
for index, row in df_imp.iterrows():
    print(f"{row['Feature']}: {row['Importance']:.4f}")
