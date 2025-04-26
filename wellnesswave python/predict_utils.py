import joblib
import pandas as pd
import numpy as np
import json

def load_model_components():
    """Load the trained model and preprocessing components."""
    try:
        model = joblib.load('depression_model.joblib')
        with open('column_info.json', 'r') as f:
            column_info = json.load(f)
        return model, column_info
    except Exception as e:
        print(f"Error loading model components: {str(e)}")
        raise

def encode_value(value, column_info):
    """Encode a value based on column info mapping."""
    if value in column_info['values']:
        return column_info['encoded_values'][column_info['values'].index(value)]
    return 0  # Default to 0 if value not found

def preprocess_input(input_data):
    """Preprocess the input data for prediction."""
    try:
        print("Starting preprocessing with input:", input_data)
        model, column_info = load_model_components()
        
        # Create a DataFrame with the input data
        df = pd.DataFrame([input_data])
        print("Created DataFrame:", df)
        
        # Map the question names to match the training data columns
        question_mapping = {
            "Age": "Age",
            "Feeling sad": "Feeling sad",
            "Irritable towards people": "Irritable towards people",
            "Sleep problems": "Trouble sleeping at night",
            "Problems concentrating or making decision": "Problems concentrating or making decision",
            "Appetite changes": "loss of appetite",
            "Feeling of guilt": "Feeling of guilt",
            "Problems of bonding with people": "Problems of bonding with people",
            "Suicidal thoughts": "Suicide attempt"
        }
        
        # Rename columns based on mapping
        df = df.rename(columns=question_mapping)
        print("After renaming columns:", df.columns)
        
        # Create a new DataFrame with required columns
        processed_df = pd.DataFrame()
        
        # Process each column according to column_info
        for col_name, info in column_info.items():
            if col_name in df.columns:
                value = df[col_name].iloc[0]
                encoded_value = encode_value(value, info)
            else:
                # Use default value if column is missing
                encoded_value = 0
            processed_df[col_name] = [encoded_value]
        
        print("Final preprocessed data:", processed_df)
        return processed_df
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        raise

def analyze_symptoms(processed_data, original_data):
    """Analyze the severity and patterns of symptoms."""
    try:
        print("Analyzing symptoms with data:", original_data)
        # Define symptoms to analyze
        symptoms = {
            'Feeling sad': {'severe': ['Yes'], 'moderate': ['Sometimes']},
            'Trouble sleeping at night': {'severe': ['Yes'], 'moderate': ['Two or more days a week']},
            'Problems concentrating or making decision': {'severe': ['Yes'], 'moderate': ['Often']},
            'loss of appetite': {'severe': ['Yes'], 'moderate': ['Not at all']},
            'Feeling of guilt': {'severe': ['Yes'], 'moderate': ['Maybe']},
            'Irritable towards people': {'severe': ['Yes'], 'moderate': ['Sometimes']},
            'Problems of bonding with people': {'severe': ['Yes'], 'moderate': ['Sometimes']},
            'Suicide attempt': {'severe': ['Yes'], 'moderate': ['Not interested to say']}
        }
        
        # Initialize symptom analysis
        symptom_analysis = {
            'severe_symptoms': [],
            'moderate_symptoms': [],
            'mild_symptoms': []
        }
        
        # Map frontend questions to backend symptoms
        symptom_mapping = {
            'Feeling sad': 'Feeling sad',
            'Sleep problems': 'Trouble sleeping at night',
            'Problems concentrating or making decision': 'Problems concentrating or making decision',
            'Appetite changes': 'loss of appetite',
            'Feeling of guilt': 'Feeling of guilt',
            'Irritable towards people': 'Irritable towards people',
            'Problems of bonding with people': 'Problems of bonding with people',
            'Suicidal thoughts': 'Suicide attempt'
        }
        
        # Analyze each symptom
        for frontend_name, backend_name in symptom_mapping.items():
            if frontend_name in original_data:
                value = original_data[frontend_name]
                if backend_name in symptoms:
                    if value in symptoms[backend_name]['severe']:
                        symptom_analysis['severe_symptoms'].append(backend_name)
                    elif value in symptoms[backend_name]['moderate']:
                        symptom_analysis['moderate_symptoms'].append(backend_name)
                    else:
                        symptom_analysis['mild_symptoms'].append(backend_name)
        
        print("Symptom analysis result:", symptom_analysis)
        return symptom_analysis
    except Exception as e:
        print(f"Error in symptom analysis: {str(e)}")
        raise

def predict_depression(input_data):
    """Make a prediction for depression with enhanced analysis."""
    try:
        print("Starting prediction with input:", input_data)
        # Keep original data for symptom analysis
        original_data = input_data.copy()
        
        # Preprocess the input data
        processed_data = preprocess_input(input_data)
        
        # Get model probability
        model, _ = load_model_components()
        probability = model.predict_proba(processed_data)[0]
        print("Model probability:", probability)
        
        # Get symptom analysis using original data
        symptom_analysis = analyze_symptoms(processed_data, original_data)
        
        # Calculate risk level and interpretation
        if len(symptom_analysis['severe_symptoms']) == 0 and len(symptom_analysis['moderate_symptoms']) == 0:
            interpretation = "Not Depressed"
            confidence = 0.95
        elif 'Suicide attempt' in symptom_analysis['severe_symptoms'] or len(symptom_analysis['severe_symptoms']) >= 3:
            interpretation = "High Risk of Depression"
            confidence = max(probability[1], 0.9)
        elif len(symptom_analysis['severe_symptoms']) >= 2:
            interpretation = "Likely Depressed"
            confidence = probability[1]
        elif len(symptom_analysis['severe_symptoms']) >= 1 or len(symptom_analysis['moderate_symptoms']) >= 3:
            interpretation = "Moderate Risk of Depression"
            confidence = probability[1]
        else:
            interpretation = "Low Risk of Depression"
            confidence = probability[0]
        
        result = {
            'category': interpretation,
            'probability': float(confidence),
            'symptom_summary': symptom_analysis
        }
        print("Final prediction result:", result)
        return result
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        raise

def get_feature_importance():
    """Get the importance of each feature."""
    try:
        model, column_info = load_model_components()
        importance = model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': list(column_info.keys()),
            'importance': importance
        })
        return feature_importance.sort_values('importance', ascending=False)
    except Exception as e:
        print(f"Error getting feature importance: {str(e)}")
        raise 