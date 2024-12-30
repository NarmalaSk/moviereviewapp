from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv  # Import dotenv to load env variables

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Hugging Face API URL and your API Key from environment variables
API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
API_KEY = os.getenv("HUGGING_FACE_API_KEY")  # Get the Hugging Face API key from environment variables

# Groq API URL (replace with actual Groq API URL and key if needed)
GROQ_API_URL = "https://api.groq.com/inference"  # Placeholder URL for Groq inference
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Get the Groq API key from environment variables

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

groq_headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}"
}

# Array to store API responses
api_responses = []

# Custom class to access JSON response using dot notation
class JsonResponse:
    def __init__(self, list_response):
        # Assuming the response is a list of predictions
        self.label = list_response[0]['label'] if len(list_response) > 0 else "Unknown"
        self.score = list_response[0]['score'] if len(list_response) > 0 else "Unknown"

@app.route('/')
def index():
    return render_template('index.html', reviews=api_responses)

@app.route('/predict', methods=['POST'])
def predict():
    review = request.form['review']  # Get the review text from the form

    if not review:
        return jsonify({"error": "Review text is required"}), 400

    # Send the review text to Hugging Face API for sentiment analysis
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": review})
        result = response.json()

        # Check if the model is still loading or if there is an error
        if isinstance(result, dict) and "error" in result and "loading" in result["error"]:
            return call_groq_inference(review)
        
        # Handle response normally if no error
        if isinstance(result, list) and result:
            response_object = JsonResponse(result[0])  # The first object in the list
            api_responses.append({
                "review": review,
                "sentiment": response_object.label,
                "score": response_object.score
            })

            # Print the stored results
            print("Stored Reviews and Sentiments:", json.dumps(api_responses, indent=2))

            sentiment = response_object.label
            score = response_object.score
            
            return render_template('index.html', sentiment=sentiment, score=score, review=review, reviews=api_responses)

    except Exception as e:
        print(f"Hugging Face API request failed: {e}")
        return call_groq_inference(review)

    # If Hugging Face returned an unexpected response format or error, call Groq
    return call_groq_inference(review)


def call_groq_inference(review):
    # Send the review text to Groq API for inference if Hugging Face fails
    try:
        # Construct the body for Groq inference request
        groq_input = {"inputs": review}
        
        # Send request to Groq API
        groq_response = requests.post(GROQ_API_URL, headers=groq_headers, json=groq_input)
        
        # Check if the response is successful
        if groq_response.status_code == 200:
            groq_result = groq_response.json()

            # Convert Groq result to JsonResponse object
            groq_response_object = JsonResponse(groq_result)

            # Store the Groq response in the array
            api_responses.append({
                "review": review,
                "sentiment": groq_response_object.label,
                "score": groq_response_object.score
            })

            print(f"Stored Reviews and Sentiments (Groq):", json.dumps(api_responses, indent=2))

            sentiment = groq_response_object.label
            score = groq_response_object.score

            return render_template('index.html', sentiment=sentiment, score=score, review=review, reviews=api_responses)
        else:
            raise Exception(f"Groq API error: {groq_response.status_code}")
    
    except Exception as e:
        print(f"Groq API request failed: {e}")
        return jsonify({"error": "Both Hugging Face and Groq inference failed"}), 500


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
