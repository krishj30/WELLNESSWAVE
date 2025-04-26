import os
import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import numpy as np

# Load environment variables and initialize Flask app
load_dotenv('db.env')
app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type"],
    "supports_credentials": True
}})

# Database connection
try:
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/krishdb'))
    db = client.get_database()
    assessments_collection = db.assessments
    print("✅ MongoDB Connected successfully")
except Exception as e:
    print(f"❌ MongoDB Connection failed: {str(e)}")
    assessments_collection = None

@app.route('/api/assessment', methods=['POST'])
def submit_assessment():
    try:
        data = request.get_json()
        
        if 'answers' not in data or not isinstance(data['answers'], list):
            return jsonify({"status": "error", "message": "Invalid assessment data"}), 400

        score = sum(data['answers'])
        result = calculate_assessment_result("anxiety", score)

        assessment = {
            "type": "anxiety",
            "answers": data["answers"],
            "score": score,
            "result": result,
            "created_at": datetime.datetime.utcnow()
        }
        
        result = assessments_collection.insert_one(assessment)

        return jsonify({
            "status": "success",
            "message": "Assessment submitted successfully",
            "data": {
                "id": str(result.inserted_id),
                "score": score,
                "result": assessment["result"],
                "recommendations": get_anxiety_recommendations(score)
            }
        }), 201

    except Exception as e:
        print(f"Assessment error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error processing assessment"
        }), 500

def calculate_assessment_result(assessment_type, score):
    if score <= 4: return "Minimal"
    elif score <= 9: return "Mild"
    elif score <= 14: return "Moderate"
    else: return "Severe"

def get_anxiety_recommendations(score):
    if score <= 4:
        return [
            "Continue monitoring your mental health",
            "Practice regular self-care",
            "Maintain healthy lifestyle habits"
        ]
    elif score <= 9:
        return [
            "Consider talking to a trusted friend or family member",
            "Practice relaxation techniques",
            "Maintain a regular sleep schedule"
        ]
    elif score <= 14:
        return [
            "Consider consulting a mental health professional",
            "Practice mindfulness and meditation",
            "Establish a regular exercise routine"
        ]
    else:
        return [
            "Strongly recommend seeking professional help",
            "Contact a mental health Crisis hotline if needed",
            "Don't hesitate to reach out to support systems"
        ]

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "success",
        "message": "API is healthy"
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
