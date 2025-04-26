from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from anxiety_predict_utils import predict_anxiety, get_feature_importance
import traceback
import sys

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('anxiety_index.html')

@app.route('/test', methods=['GET'])
def test():
    try:
        return jsonify({
            'status': 'Server is running',
            'model_loaded': True
        })
    except Exception as e:
        return jsonify({
            'status': 'Error',
            'model_loaded': False,
            'error': str(e)
        })

@app.route('/predict/anxiety', methods=['POST', 'OPTIONS'])
def predict_anxiety():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({'error': 'No answers provided'}), 400

        answers = data['answers']
        if not isinstance(answers, list):
            return jsonify({'error': 'Answers must be a list'}), 400

        # Convert answers to the format expected by the model
        input_data = {}
        for answer in answers:
            if 'question' in answer and 'answer' in answer:
                input_data[answer['question']] = answer['answer']

        # Make prediction using the model
        result = predict_anxiety(input_data)
        
        if not result:
            return jsonify({'error': 'Failed to make prediction'}), 500

        return jsonify({
            'category': result['predicted_class'],
            'probability': float(result['confidence']),
            'symptom_summary': {
                'severe': result.get('severe_symptoms', []),
                'moderate': result.get('moderate_symptoms', []),
                'mild': result.get('mild_symptoms', [])
            }
        })

    except Exception as e:
        print(f"Error in predict_anxiety: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/feature_importance', methods=['GET'])
def feature_importance():
    try:
        importance_data = get_feature_importance()
        return jsonify(importance_data.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n=== Starting Anxiety Prediction Server ===")
    print("Server will be available at http://127.0.0.1:5001")
    app.run(debug=True, port=5001) 