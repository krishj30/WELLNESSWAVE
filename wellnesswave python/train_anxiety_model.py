import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data():
    """Load and preprocess the anxiety dataset."""
    print("Loading anxiety dataset...")
    df = pd.read_csv('anxiety_dataset_balanced.csv')
    
    # Rename columns for consistency
    column_mapping = {
        'Do you feel nervous or anxious often?': 'Nervousness',
        'Do you experience sudden panic attacks?': 'Panic_attacks',
        'Do you have trouble relaxing or staying calm?': 'Trouble_relaxing',
        'Do you avoid social situations due to anxiety?': 'Social_avoidance',
        'Do you experience excessive worry about different things?': 'Excessive_worry',
        'Do you have difficulty sleeping due to anxiety?': 'Sleep_difficulty',
        'Do you feel lightheaded or dizzy when anxious?': 'Lightheadedness',
        'Do you experience a racing heart or shortness of breath?': 'Physical_symptoms',
        'Do you have trouble concentrating due to anxiety?': 'Concentration_issues',
        'Do you feel a sense of impending doom or danger?': 'Impending_doom',
        'Anxiety_Level': 'Anxiety_Level'
    }
    df = df.rename(columns=column_mapping)
    
    # Create label encoder for anxiety levels
    le = LabelEncoder()
    df['Anxiety_Level'] = le.fit_transform(df['Anxiety_Level'])
    
    # Save label encoder
    joblib.dump(le, 'anxiety_label_encoder.joblib')
    
    # Save column information
    column_info = {}
    for col in df.columns:
        if col != 'Anxiety_Level':
            column_info[col] = {
                'type': 'numerical',
                'range': [int(df[col].min()), int(df[col].max())],
                'mean': float(df[col].mean()),
                'std': float(df[col].std())
            }
    
    with open('anxiety_column_info.json', 'w') as f:
        json.dump(column_info, f, indent=4)
    
    return df

def train_model(df):
    """Train the anxiety prediction model."""
    print("Preparing data for training...")
    
    # Separate features and target
    X = df.drop('Anxiety_Level', axis=1)
    y = df['Anxiety_Level']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\nModel Performance:")
    print(f"Accuracy: {accuracy:.2%}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    joblib.dump(model, 'anxiety_model.joblib')
    print("\nModel saved as 'anxiety_model.joblib'")
    
    # Calculate and save feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save feature importance
    feature_importance.to_csv('anxiety_feature_importance.csv', index=False)
    print("\nFeature importance saved to 'anxiety_feature_importance.csv'")

def main():
    """Main function to train the anxiety prediction model."""
    try:
        # Load and preprocess data
        df = load_and_preprocess_data()
        
        # Train the model
        train_model(df)
        
        print("\nTraining completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 