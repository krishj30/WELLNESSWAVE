import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load the model and label encoder
model = joblib.load('anxiety_model.joblib')
label_encoder = joblib.load('anxiety_label_encoder.joblib')

def predict_anxiety(answers):
    try:
        # Convert answers to numerical format
        input_data = np.array(list(answers.values())).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(input_data)
        probabilities = model.predict_proba(input_data)[0]
        
        # Get the predicted class and its probability
        predicted_class = label_encoder.inverse_transform(prediction)[0]
        confidence = max(probabilities) * 100
        
        # Get probabilities for each class
        class_probabilities = {
            label: float(prob) * 100 
            for label, prob in zip(label_encoder.classes_, probabilities)
        }
        
        return {
            "prediction": predicted_class,
            "confidence": confidence,
            "probabilities": class_probabilities
        }
        
    except Exception as e:
        print(f"Error in predict_anxiety: {str(e)}")
        raise Exception("Error making anxiety prediction") from e 