import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('depressionData.csv')

# Drop the Timestamp column
df = df.drop('Timestamp', axis=1)

# Handle missing values with mode
df = df.fillna(df.mode().iloc[0])

# Create label encoders for each column
label_encoders = {}
columns_to_encode = df.columns.drop('Depressed')  # Don't encode the target variable

# Encode each column
for column in columns_to_encode:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    label_encoders[column] = le

# Prepare features and target
X = df.drop('Depressed', axis=1)
y = df['Depressed'].map({'Yes': 1, 'No': 0})

# Calculate class weights
class_weights = dict(zip(np.unique(y), 1 / np.bincount(y)))

# Train the model with class weights
print("Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight=class_weights,
    min_samples_leaf=5
)
model.fit(X, y)

# Save the model and encoders
print("Saving model and encoders...")
joblib.dump(model, 'model.joblib')
joblib.dump(label_encoders, 'label_encoders.joblib')

# Save column information
column_info = {}
for column in columns_to_encode:
    column_info[column] = {
        'values': label_encoders[column].classes_.tolist(),
        'encoded_values': list(range(len(label_encoders[column].classes_)))
    }

# Save column info
import json
with open('column_info.json', 'w') as f:
    json.dump(column_info, f)

# Print model accuracy
y_pred = model.predict(X)
accuracy = (y_pred == y).mean()
print(f"\nModel accuracy: {accuracy * 100:.2f}%")

# Print feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
})
print("\nFeature Importance:")
print(feature_importance.sort_values('importance', ascending=False)) 