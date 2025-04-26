import joblib
import pandas as pd
import numpy as np
import json

def load_model_components():
    """Load the trained model and preprocessing components."""
    try:
        model = joblib.load('anxiety_model.joblib')
        label_encoder = joblib.load('anxiety_label_encoder.joblib')
        
        with open('anxiety_column_info.json', 'r') as f:
            column_info = json.load(f)
        
        return model, label_encoder, column_info
    except Exception as e:
        print(f"Error loading model components: {str(e)}")
        raise

def preprocess_input(input_data):
    """Preprocess the input data for prediction."""
    try:
        model, label_encoder, column_info = load_model_components()
        
        # Create a DataFrame with the input data
        df = pd.DataFrame([input_data])
        
        # Ensure all required features are present
        required_features = list(column_info.keys())
        for feature in required_features:
            if feature not in df.columns:
                print(f"Warning: Missing feature {feature}")
                df[feature] = column_info[feature]['mean']
        
        # Reorder columns to match training data
        df = df[required_features]
        
        return df
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        raise

def analyze_symptoms(processed_data):
    """Analyze the severity and patterns of anxiety symptoms."""
    # Define critical symptoms and their weights
    critical_symptoms = {
        'Panic_attacks': 3.0,
        'Physical_symptoms': 2.5,
        'Impending_doom': 2.5,
        'Social_avoidance': 2.0,
        'Nervousness': 2.0,
        'Excessive_worry': 2.0,
        'Trouble_relaxing': 1.5,
        'Sleep_difficulty': 1.5,
        'Lightheadedness': 1.5,
        'Concentration_issues': 1.5
    }
    
    # Initialize symptom analysis
    symptom_analysis = {
        'critical_count': 0,
        'moderate_count': 0,
        'mild_count': 0,
        'total_weight': 0,
        'severe_symptoms': [],
        'moderate_symptoms': [],
        'mild_symptoms': []
    }
    
    # Analyze each symptom
    for symptom, weight in critical_symptoms.items():
        value = processed_data[symptom].iloc[0]
        
        # Severe symptoms (value >= 4)
        if value >= 4:
            symptom_analysis['critical_count'] += 1
            symptom_analysis['total_weight'] += weight
            symptom_analysis['severe_symptoms'].append(symptom)
        
        # Moderate symptoms (value == 3)
        elif value == 3:
            symptom_analysis['moderate_count'] += 1
            symptom_analysis['total_weight'] += weight * 0.7
            symptom_analysis['moderate_symptoms'].append(symptom)
        
        # Mild symptoms (value <= 2)
        else:
            symptom_analysis['mild_count'] += 1
            symptom_analysis['total_weight'] += weight * 0.3
            symptom_analysis['mild_symptoms'].append(symptom)
    
    return symptom_analysis

def predict_anxiety(input_data):
    """Make a prediction for anxiety with enhanced analysis."""
    try:
        model, label_encoder, column_info = load_model_components()
        
        # Preprocess the input data
        processed_data = preprocess_input(input_data)
        
        # Get symptom analysis
        symptom_analysis = analyze_symptoms(processed_data)
        
        # Get model probability
        probability = model.predict_proba(processed_data)[0]
        
        # Calculate risk level based on symptom analysis and model probability
        risk_level = 0
        interpretation = ""
        confidence = 0.0
        
        # Critical case: Multiple severe symptoms or high scores in critical symptoms
        if (symptom_analysis['critical_count'] >= 2 or 
            'Panic_attacks' in symptom_analysis['severe_symptoms'] or
            'Physical_symptoms' in symptom_analysis['severe_symptoms'] or
            (symptom_analysis['critical_count'] == 1 and 
             symptom_analysis['moderate_count'] >= 3)):
            risk_level = 3
            interpretation = "Extreme Anxiety"
            confidence = max(probability[3], 0.9)
        
        # Severe case: High model probability with significant symptoms
        elif probability[3] > 0.7 and symptom_analysis['total_weight'] > 8:
            risk_level = 2
            interpretation = "Severe Anxiety"
            confidence = probability[3]
        
        # Moderate case: Mixed symptoms with moderate probability
        elif (probability[2] > 0.6 and 
              (symptom_analysis['moderate_count'] >= 2 or 
               symptom_analysis['total_weight'] > 5)):
            risk_level = 1
            interpretation = "Moderate Anxiety"
            confidence = probability[2]
        
        # Mild case: Few symptoms and low probability
        elif probability[1] > 0.5:
            risk_level = 0
            interpretation = "Mild Anxiety"
            confidence = probability[1]
        
        # No anxiety case: No significant symptoms
        else:
            risk_level = 0
            interpretation = "No Anxiety"
            confidence = probability[0]
        
        # Add detailed symptom summary
        symptom_summary = {
            'severe': symptom_analysis['severe_symptoms'],
            'moderate': symptom_analysis['moderate_symptoms'],
            'mild': symptom_analysis['mild_symptoms']
        }
        
        return {
            'prediction': risk_level,
            'probability': float(confidence),
            'interpretation': interpretation,
            'symptom_summary': symptom_summary
        }
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return {
            'prediction': 0,
            'probability': 0.0,
            'interpretation': f'Error in prediction: {str(e)}',
            'symptom_summary': {'severe': [], 'moderate': [], 'mild': []}
        }

def get_feature_importance():
    """Get the importance of each feature."""
    try:
        model, _, column_info = load_model_components()
        
        importance = model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': list(column_info.keys()),
            'importance': importance
        })
        
        return feature_importance.sort_values('importance', ascending=False)
    except Exception as e:
        print(f"Error getting feature importance: {str(e)}")
        raise 